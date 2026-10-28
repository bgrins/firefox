import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OLD = ROOT / "artifacts/css-line-height-contextual-number-repair-v1"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

refs = json.loads((HERE / "REFERENCES.json").read_text())
for name, digest in refs.items():
    assert sha(ROOT / name) == digest, name
release = ROOT / "artifacts/css-line-height-tree-release-observation-v1"
for name, record in json.loads((release / "FILES.json").read_text()).items():
    assert sha(release / name) == record["sha256"], name
result = json.loads((release / "RESULT.json").read_text())
assert result["full_workspace_and_release_binary_preservation"]
assert result["random_pref"] is False
assert len(result["failures"]) == 2 and len(result["passing_controls"]) == 6
roster = json.loads((HERE / "TARGET-SUBTESTS.json").read_text())
old_names = next(iter(json.loads((OLD / "TARGET-SUBTESTS.json").read_text()).values()))
assert [name for names in roster.values() for name in names] == old_names
random_path = next(iter(roster))
old_html = (OLD / "candidate" / random_path).read_text()
new_html = (HERE / "candidate" / random_path).read_text()
start = "function makeBox"
end = 'for (const kind of ["sibling-index", "sibling-count"])'
assert old_html[old_html.index(start):old_html.index(end)] == new_html[new_html.index(start):new_html.rindex("</script>")]
with tempfile.TemporaryDirectory(prefix="line-height-wpt-split-") as temp:
    scratch = Path(temp)
    for i, (name, expected) in enumerate(roster.items()):
        html = (HERE / "candidate" / name).read_text()
        js = re.findall(r"<script>([\s\S]*?)</script>", html)[0]
        file = scratch / f"test-{i}.js"
        file.write_text(js)
        subprocess.run(["node", "--check", str(file)], check=True, capture_output=True)
        file.write_text("const names=[]; function test(body,name) { names.push(name); }\n" + js + "\nprocess.stdout.write(JSON.stringify(names));\n")
        got = subprocess.run(["node", str(file)], check=True, capture_output=True, text=True)
        assert json.loads(got.stdout) == expected
        if "css-inline" in name:
            assert "random(" not in html
    for variant, base in [("fix.patch", "base"), ("upstream-fix.patch", "upstream-base")]:
        work = scratch / base
        shutil.copytree(OLD / base, work)
        patch = HERE / variant
        for mode in ["forward", "reverse", "forward"]:
            args = ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(patch)]
            if mode == "reverse":
                args.append("-R")
            done = subprocess.run(args, cwd=work, check=True, capture_output=True, text=True)
            assert not any(x in (done.stdout + done.stderr).lower() for x in ["offset", "fuzz", "failed"])
            if mode == "forward":
                for name in roster:
                    assert (work / name).read_bytes() == (HERE / "candidate" / name).read_bytes()
                font = "servo/components/style/values/specified/font.rs"
                expected = OLD / ("candidate" if base == "base" else "upstream-candidate") / font
                assert (work / font).read_bytes() == expected.read_bytes()
assert not scratch.exists()
print(json.dumps({"passed": True, "pages": 2, "tests": 12, "unchanged_random_case_bodies": 10, "moved_tree_cases": 2, "release_evidence_authenticated": True, "branch_and_captured_upstream_three_path_transport": True, "test_callbacks_executed": False, "scratch_removed": True}, indent=2))
