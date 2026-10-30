import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [
    str(WPT / "tools"), str(WPT), str(ROOT / "third_party/python/pyyaml/lib")]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

page = "animation-duration-finite-depth.tentative.html"
handler = "duration-finite-depth-record.py"
source = (HERE / page).read_text()
dom = html5lib.parse(source, namespaceHTMLElements=False)
scripts = [node.text for node in dom.iter("script") if not node.get("src")]
assert len(scripts) == 1 and source.index("<body>") < source.index("<script>\n")
start = source.index('  root.classList.add("advanced");')
end = source.index("  const beforeMembership = details(context);", start)
window = source[start:end]
assert window.count("getComputedStyle(leaf).opacity") == 2 and "index <= 3" in window
assert all(word not in window for word in ["getAnimations", "details(", "timing(", "getTiming", "getComputedTiming", "currentTime"])
assert source.index("await record(depth, observations)") < source.index("assertObservation(literal,") < source.index("assertObservation(contextual,")
assert 'if (mode === "contextual") root.classList.replace("literal", "contextual");' in source
assert source.count("currentTime =") == 1 and "updateTiming" not in source
old = ROOT / "artifacts/css-contextual-duration-same-element-dependency-probe-v1/tests/css/css-animations/duration-same-element-record.py"
assert (HERE / handler).read_text().split("def reject_constant", 1)[1] == old.read_text().split("def reject_constant", 1)[1]
program = r"""
const vm = require('vm');
let text='';
process.stdin.on('data', x=>text+=x);
process.stdin.on('end', ()=>{
  const names=[];
  function ok(b) {if(!b) throw Error('assertion');}
  const context=vm.createContext({promise_test:(_,name)=>names.push(name),
    assert_equals:(a,b)=>ok(a===b),assert_true:ok});
  vm.runInContext(text,context);
  const expected=vm.runInContext('expected',context);
  const verify=vm.runInContext('assertObservation',context);
  const records=[];
  function snapshot(n, advanced) {
    const nodes=[];
    for(let i=0;i<n;i++) {
      const duration=(i%2 === 0) !== advanced ? 1000 : 2000;
      const input=duration===1000?16:32, output=48-input;
      const timing={duration,progress:duration===1000?1:.75,time:1500,state:'paused'};
      nodes.push({font:i%2===0?input:output,lineHeight:i%2===0?output:input,duration,timing});
    }
    const duration=(n%2===0) !== advanced ? 1000:2000;
    return {rootFont:advanced?32:16,nodes,leafDuration:duration,opacity:duration===1000?1:0,
      leaf:{duration,progress:duration===1000?1:.75,time:1500,state:'paused'}};
  }
  for(const depth of [1,2,4,8]) {
    const observations={};
    for(const mode of ['literal','contextual']) {
      const initial=snapshot(depth,false), final=snapshot(depth,true);
      const oracle=expected(depth,true);
      ok(oracle.opacity===(depth===1?1:0));
      ok(expected(depth,false).opacity===(depth===1?0:1));
      const value={depth,mode,literalInitial:initial,initial,
        samples:['first-leaf-read','passive-frame-1','passive-frame-2','passive-frame-3'].map(phase=>({phase,opacity:final.opacity})),
        beforeMembership:final,afterMembership:structuredClone(final),
        membership:Array.from({length:depth+1},()=>({animation:true,effect:true}))};
      verify(value,'synthetic');observations[mode]=value;
    }
    records.push({kind:`depth-${depth}`,observations});
  }
  const negatives=[];
  function reject(label,mutate) {
    const value=structuredClone(records[3].observations.contextual);mutate(value);
    try {verify(value,label);} catch (_) {negatives.push(label);return;}
    throw Error('false control passed '+label);
  }
  reject('stale first read',v=>v.samples[0].opacity=1);
  reject('stale late sample',v=>v.samples[3].opacity=1);
  reject('intermediate stale output',v=>v.beforeMembership.nodes[3].font=16);
  reject('inherited input stale',v=>v.beforeMembership.nodes[3].lineHeight=32);
  reject('intermediate duration stale',v=>v.beforeMembership.nodes[3].timing.duration=2000);
  reject('CSS duration stale',v=>v.beforeMembership.nodes[3].duration=2000);
  reject('leaf progress stale',v=>v.beforeMembership.leaf.progress=1);
  reject('root unchanged',v=>v.beforeMembership.rootFont=16);
  reject('after membership stale',v=>v.afterMembership.opacity=1);
  reject('identity replaced',v=>v.membership[0].animation=false);
  reject('held time changed',v=>v.afterMembership.leaf.time=1501);
  process.stdout.write(JSON.stringify({names,records,oracle_positive_cases:8,oracle_negatives:negatives}));
});
"""
result = subprocess.run(["node", "-e", program], input=scripts[0], text=True, capture_output=True, check=True)
checks = json.loads(result.stdout)
assert checks["names"] == [f"First leaf read updates a finite acyclic animation-duration chain of depth {n}" for n in (1, 2, 4, 8)]
spec = importlib.util.spec_from_file_location("finite_depth_schema", HERE / handler)
schema = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema)
for value in checks["records"]:
    assert schema.validate(value) == value["kind"]
wrong = copy.deepcopy(checks["records"][0])
wrong["observations"]["contextual"]["samples"][0]["opacity"] = None
wrong["observations"]["contextual"]["membership"][0]["effect"] = False
assert schema.validate(wrong) == wrong["kind"]
negative = []
def reject(name, mutate):
    value = copy.deepcopy(checks["records"][0]); mutate(value)
    try:
        schema.validate(value)
    except (AssertionError, KeyError, TypeError):
        negative.append(name)
        return
    raise AssertionError(name)
reject("wrong kind", lambda v: v.update(kind="depth-16"))
reject("missing mode", lambda v: v["observations"].pop("literal"))
reject("wrong depth", lambda v: v["observations"]["contextual"].update(depth=2))
reject("boolean depth", lambda v: v["observations"]["contextual"].update(depth=True))
reject("missing initial", lambda v: v["observations"]["contextual"].pop("initial"))
reject("missing sample", lambda v: v["observations"]["contextual"]["samples"].pop())
reject("wrong phase order", lambda v: v["observations"]["contextual"]["samples"].reverse())
reject("extra node", lambda v: v["observations"]["contextual"]["beforeMembership"]["nodes"].append({}))
reject("missing identity", lambda v: v["observations"]["contextual"]["membership"].pop())
reject("nonfinite", lambda v: v["observations"]["contextual"]["samples"][0].update(opacity=float("inf")))
with tempfile.TemporaryDirectory(prefix="css-finite-depth-static-") as temporary:
    scratch = Path(temporary)
    directory = scratch / "records"; directory.mkdir(mode=0o700)
    previous = {key: os.environ.get(key) for key in ("DURATION_PROGRESS_RECORD_DIR", "DURATION_PROGRESS_RUN_ID")}
    os.environ.update(DURATION_PROGRESS_RECORD_DIR=str(directory), DURATION_PROGRESS_RUN_ID="finite_depth_synthetic_run")
    try:
        for value in checks["records"]:
            request = type("Request", (), {"method": "POST", "body": json.dumps(value).encode()})()
            _, response = schema.main(request, None)
            assert json.loads(response)["kind"] == value["kind"]
            body = json.loads((directory / schema.FILES[value["kind"]]).read_text())
            assert body == dict(run_id="finite_depth_synthetic_run", **value)
            try: schema.main(request, None)
            except FileExistsError: pass
            else: raise AssertionError("duplicate record overwritten")
    finally:
        for key, value in previous.items():
            if value is None: os.environ.pop(key, None)
            else: os.environ[key] = value
    tests = scratch / "tests"; folder = tests / "css/css-animations"; folder.mkdir(parents=True)
    for name in (page, handler): shutil.copyfile(HERE / name, folder / name)
    (tests / "lint.ignore").write_text("")
    paths = ["css/css-animations/" + name for name in (page, handler)]
    manifest = Manifest(str(tests), "/")
    manifest.update([(path, None, True) for path in paths], parallel=False)
    (HERE / "SUBSET-MANIFEST.json").write_text(json.dumps(manifest.to_json(), sort_keys=True, indent=2) + "\n")
    cwd = os.getcwd()
    try:
        os.chdir(tests)
        assert lint.lint(str(tests), paths, "normal", jobs=1) == 0
    finally:
        os.chdir(cwd)
assert not scratch.exists()
checks.pop("records")
checks.update(schema_positive_cases=5, schema_negatives=negative, exclusive_roundtrips=4,
              duplicates_rejected=4, lint_errors=0, scratch_removed=True, browser_executed=False)
(HERE / "ROSTER.json").write_text(json.dumps({"tests": {"/css/css-animations/" + page: checks["names"]}, "callbacks":4}, indent=2) + "\n")
(HERE / "CHECK.json").write_text(json.dumps(checks, indent=2) + "\n")
print(json.dumps(checks, indent=2))
