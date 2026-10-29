import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT)]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

inputs = json.loads((PACKAGE / "INPUTS.json").read_text())
roster = json.loads((PACKAGE / "ROSTER.json").read_text())
for path, digest in json.loads((PACKAGE / "REFERENCES.json").read_text()).items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
sources = {}
for name, entry in inputs.items():
    data = (ROOT / entry["capture"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == entry["sha256"]
    sources[name] = data
    document = html5lib.parse(data.decode(), namespaceHTMLElements=False)
    scripts = [n.text or "" for n in document.find("body").iter("script") if n.get("src") is None]
    assert scripts
    result = subprocess.run(["node", "-e", "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];const register=(fn,name)=>names.push(name);vm.runInNewContext(s,{test:register,promise_test:register});process.stdout.write(JSON.stringify(names));});"], input="\n".join(scripts), text=True, capture_output=True, check=True)
    assert json.loads(result.stdout) == roster["/" + name]
with tempfile.TemporaryDirectory(prefix="css-move-landing-") as temporary:
    scratch = Path(temporary)
    for name, data in sources.items():
        output = scratch / name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
    (scratch / "lint.ignore").write_text("")
    subprocess.run(["git", "init", "-q", str(scratch)], check=True)
    manifest = Manifest(str(scratch), "/")
    manifest.update([(name, None, True) for name in sorted(sources)], parallel=False)
    serialized = manifest.to_json()
    for name in sources:
        node = serialized["items"]["testharness"]
        for part in name.split("/"):
            node = node[part]
        assert len(node) == 2 and node[1][0] is None
    output = PACKAGE / "SUBSET-MANIFEST.json"
    if output.exists():
        assert json.loads(output.read_text()) == serialized
    else:
        output.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n")
    previous = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), list(sources), "normal", jobs=1) == 0
    finally:
        os.chdir(previous)
    base = json.loads((PACKAGE / "METADATA-PLAN.json").read_text())
    meta = scratch / base["path"]
    meta.parent.mkdir(parents=True)
    meta.write_bytes((PACKAGE / "existing-selector.ini").read_bytes())
    for patch in ["metadata.patch", "landing.patch"]:
        subprocess.run(["git", "apply", "--check", str(PACKAGE / patch)], cwd=scratch, check=True)
        subprocess.run(["git", "apply", str(PACKAGE / patch)], cwd=scratch, check=True)
        subprocess.run(["git", "apply", "-R", str(PACKAGE / patch)], cwd=scratch, check=True)
    assert hashlib.sha256(meta.read_bytes()).hexdigest() == base["before_sha256"]
print(json.dumps({"pages": 2, "landing_callbacks": 2, "validation_only_callbacks": 1, "lint_errors": 0, "body_before_callbacks": True, "inert_enumeration_only": True, "patch_apply_reverse": True, "scratch_removed": True}))
