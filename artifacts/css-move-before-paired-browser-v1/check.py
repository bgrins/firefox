import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT), str(ROOT / "third_party/python/PyYAML/lib")]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pins = read(HERE / "SOURCE-PINS.json")
pages = read(HERE / "PAGES.json")
for path, digest in read(HERE / "REFERENCES.json").items():
    assert sha(ROOT / path) == digest, path
sources = {}
for origin, record in pins.items():
    if not record["exists"]:
        assert not (ROOT / origin).exists(), origin
        continue
    body = (ROOT / record["capture"]).read_bytes()
    assert len(body) == record["bytes"] and hashlib.sha256(body).hexdigest() == record["sha256"]
    if origin.startswith("testing/web-platform/tests/"):
        sources[origin.removeprefix("testing/web-platform/tests/")] = body
harness = sources["resources/testharness.js"].decode()
start = harness.index("function get_test_name(")
end = harness.index("\n    /**", start)
naming = harness[start:end]
registered = {}
for url, page in pages.items():
    relative = page["source"].removeprefix("testing/web-platform/tests/")
    text = sources[relative].decode()
    if relative.endswith(".js"):
        code = text
        title = Path(url).name.split(".")[0]
    else:
        document = html5lib.parse(text, namespaceHTMLElements=False)
        title_node = document.find(".//title")
        title = title_node.text if title_node is not None else Path(url).name.split(".")[0]
        code = "\n".join(node.text or "" for node in document.iter("script") if node.get("src") is None)
        if page["kind"] in ("diagnostic", "landing", "identity"):
            assert document.find("body") is not None
            assert any(node.text and node.get("src") is None for node in document.find("body").iter("script"))
    js = """const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const data=JSON.parse(input);const names=[];let n=0;const ctx={seen_func_name:{},test_environment:{next_default_test_name:()=>data.title+(n++?' '+(n-1):'')}};vm.createContext(ctx);vm.runInContext(data.naming,ctx);ctx.test=ctx.promise_test=(fn,name)=>names.push(ctx.get_test_name(fn,name));vm.runInContext(data.code,ctx);process.stdout.write(JSON.stringify(names));});"""
    result = subprocess.run(["node", "-e", js], input=json.dumps({"code": code, "naming": naming, "title": title}), text=True, capture_output=True, check=True)
    names = json.loads(result.stdout)
    assert names and len(names) == len(set(names)), url
    if "names" in page:
        assert names == page["names"], url
    registered[url] = names
selector_url = "/dom/nodes/moveBefore/moveBefore-child-list-selector-invalidation.html"
selector_meta = pins["testing/web-platform/meta" + selector_url + ".ini"]
metadata = (ROOT / selector_meta["capture"]).read_text()
improvements = re.findall(r"^  \[(.*)\]\n    expected: FAIL$", metadata, re.M)
assert len(improvements) == 7 and set(improvements) <= set(registered[selector_url])
targets = {url: names for url, names in registered.items() if pages[url]["kind"] in ("diagnostic", "landing")}
targets[selector_url] = improvements
controls = {url: [name for name in names if name not in targets.get(url, [])] for url, names in registered.items()}
assert sum(map(len, registered.values())) == 70
assert sum(map(len, targets.values())) == 51
assert sum(map(len, controls.values())) == 19
with tempfile.TemporaryDirectory(prefix="css-move-pair-") as temporary:
    scratch = Path(temporary)
    for path, body in sources.items():
        target = scratch / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    (scratch / "lint.ignore").write_text("")
    subprocess.run(["git", "init", "-q", str(scratch)], check=True)
    manifest = Manifest(str(scratch), "/")
    manifest.update([(path, None, True) for path in sorted(sources)], parallel=False)
    serialized = manifest.to_json()
    restored = Manifest.from_json(str(scratch), serialized)
    assert restored.to_json() == serialized
    for url, page in pages.items():
        node = serialized["items"]["testharness"]
        relative = page["source"].removeprefix("testing/web-platform/tests/")
        for part in relative.split("/"):
            node = node[part]
        assert len(node) == 2
        assert node[1][0] == (url.lstrip("/") if relative.endswith(".window.js") else None), (url, node)
    previous = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), [page["source"].removeprefix("testing/web-platform/tests/") for page in pages.values()], "normal", jobs=1) == 0
    finally:
        os.chdir(previous)
for name, data in [("SUBSET-MANIFEST.json", serialized), ("ROSTER.json", {"expected_subtests": registered, "target_subtests": targets, "regression_subtests": controls})]:
    destination = HERE / name
    if destination.exists():
        assert read(destination) == data, name
    else:
        destination.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
print(json.dumps({"pages": 12, "callbacks": 70, "targets": 51, "strict_controls": 19, "selector_expected_fail_improvements": 7, "lint_errors": 0, "callbacks_executed": False, "scratch_removed": True}))
