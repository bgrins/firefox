import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(path) for path in (WPT / "tools/third_party").iterdir() if path.is_dir()] + [str(WPT / "tools"), str(WPT)]
import html5lib
from manifest.manifest import Manifest

read = lambda name: json.loads((HERE / name).read_text())
for name, pin in read("REFERENCES.json").items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin, name
experiment = read("EXPERIMENT.json")
resources = read("RESOURCES.json")
expected = experiment["expected_subtests"]
with tempfile.TemporaryDirectory(prefix="css-easing-union-") as temporary:
    scratch = Path(temporary)
    for name, pin in resources.items():
        part = Path(name)
        assert not part.is_absolute() and ".." not in part.parts
        data = (ROOT / pin["path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == pin["sha256"]
        target = scratch / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    assert not (scratch / "css/css-easing/support/util.js").exists()
    registration_input = scratch / "registration.json"
    registration_input.write_text(json.dumps({"root": str(scratch), "expected": expected}))
    result = subprocess.run(["node", str(HERE / "enumerate.js"), str(registration_input)],
                            text=True, capture_output=True, check=True)
    assert json.loads(result.stdout) == expected
    for page in ["/css/css-animations/contextual-easing-lifecycle.html",
                 "/css/css-animations/contextual-keyframe-easing-scope.html",
                 "/css/css-animations/contextual-easing-pseudo-transition.html",
                 "/css/css-animations/contextual-easing-setKeyframes-override.html",
                 "/css/css-easing/contextual-easing-static-properties.html",
                 "/css/css-animations/contextual-easing-rule-expression-ownership.html"]:
        document = html5lib.parse((scratch / page.lstrip("/")).read_text(), namespaceHTMLElements=False)
        body = document.find("body")
        assert body is not None
        assert any(node.get("src") is None and node.text for node in body.iter("script")), page
    manifest = Manifest(str(scratch), "/")
    manifest.update([(name, None, True) for name in sorted(resources)], parallel=False)
    serialized = json.loads(json.dumps(manifest.to_json()))
    assert sum(1 for _ in manifest.itertypes("testharness")) == 22
    for page in expected:
        node = serialized["items"]["testharness"]
        for part in page.lstrip("/").split("/"):
            node = node[part]
        assert len(node) == 2 and node[1][0] is None
    for package in ["css-contextual-easing-reversible-browser-v4", "css-contextual-easing-after-moves-browser-v3"]:
        policy = json.loads((ROOT / "artifacts" / package / "POLICY.json").read_text())["wpt"]
        previous = json.loads((ROOT / policy["manifest"]["path"]).read_text())
        for page in policy["expected_subtests"]:
            old_entry = previous["items"]["testharness"]
            new_entry = serialized["items"]["testharness"]
            for part in page.lstrip("/").split("/"):
                old_entry, new_entry = old_entry[part], new_entry[part]
            assert old_entry == new_entry, page
    previous = json.loads((ROOT / "artifacts/css-contextual-easing-rule-expression-plan-v1/SUBSET-MANIFEST.json").read_text())
    page = "contextual-easing-rule-expression-ownership.html"
    assert previous["items"]["testharness"]["css"]["css-animations"][page] == serialized["items"]["testharness"]["css"]["css-animations"][page]
    saved = HERE / "SUBSET-MANIFEST.json"
    if saved.exists():
        assert json.loads(saved.read_text()) == serialized
    else:
        saved.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n")
print(json.dumps({"registered_pages": len(expected), "registered_callbacks": sum(map(len, expected.values())),
                  "genuine_testharness_pages": 22, "callbacks_executed": False,
                  "missing_util_preserved": True, "scratch_removed": True,
                  "six_authored_pages_have_body_before_callbacks": True,
                  "all22_previous_manifest_entries_preserved": True,
                  "live_source_or_app_read": False}))
