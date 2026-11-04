import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REVISION = "a6f39620516a4cf76a5dbf5208960adc79068cf1"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def run(args, cwd=None):
    value = subprocess.run(args, cwd=cwd, capture_output=True)
    assert value.returncode == 0, (args, value.stdout.decode(), value.stderr.decode())
    return value.stdout


roles = json.loads((HERE / "SOURCE-ROLES.json").read_bytes())
references = json.loads((HERE / "REFERENCES.json").read_bytes())
for path, pin in references.items():
    assert sha(ROOT / path) == pin, path
assert len(roles) == 8
assert sum(row["kind"] == "rust" for row in roles.values()) == 3
assert sum(row["kind"] == "wpt" for row in roles.values()) == 5
patch = ""
for path, row in roles.items():
    candidate = HERE / "candidate" / path
    assert sha(candidate) == row["candidate_sha256"]
    assert candidate.read_bytes() == (ROOT / row["candidate_origin"]).read_bytes()
    if row["base_sha256"] is None:
        assert row["kind"] == "wpt"
        assert not run(["git", "--no-optional-locks", "ls-tree", REVISION, "--", path], ROOT)
        before = ""
    else:
        assert row["kind"] == "rust"
        base = HERE / "base" / path
        assert sha(base) == row["base_sha256"]
        assert base.read_bytes() == run(["git", "--no-optional-locks", "show", REVISION + ":" + path], ROOT)
        before = base.read_text()
    patch += "".join(difflib.unified_diff(before.splitlines(True), candidate.read_text().splitlines(True),
                      fromfile="a/" + path if row["base_sha256"] else "/dev/null", tofile="b/" + path))
assert patch == (HERE / "native.patch").read_text()
roster = json.loads((HERE / "ROSTER.json").read_bytes())
assert len(roster) == 5 and sum(map(len, roster.values())) == 188
for path, row in roles.items():
    if row["kind"] == "wpt":
        url = "/" + path.removeprefix("testing/web-platform/tests/")
        assert len(roster[url]) == len(set(roster[url])) == row["callbacks"]
for row in json.loads((HERE / "RESOURCES.json").read_bytes()).values():
    assert sha(ROOT / row["path"]) == row["sha256"]
scratch = Path(tempfile.mkdtemp(prefix="rollback-cumulative-patch-"))
try:
    tree = scratch / "tree"
    shutil.copytree(HERE / "base", tree)
    forward = run(["patch", "--batch", "--fuzz=0", "-p1", "-i", str(HERE / "native.patch")], tree)
    assert b"offset" not in forward.lower() and b"fuzz" not in forward.lower()
    assert {str(p.relative_to(tree)) for p in tree.rglob("*") if p.is_file()} == set(roles)
    for path in roles:
        assert (tree / path).read_bytes() == (HERE / "candidate" / path).read_bytes()
    reverse = run(["patch", "--batch", "--fuzz=0", "-R", "-p1", "-i", str(HERE / "native.patch")], tree)
    assert b"offset" not in reverse.lower() and b"fuzz" not in reverse.lower()
    assert {str(p.relative_to(tree)) for p in tree.rglob("*") if p.is_file()} == {path for path,row in roles.items() if row["base_sha256"]}
    for path,row in roles.items():
        if row["base_sha256"]:
            assert (tree / path).read_bytes() == (HERE / "base" / path).read_bytes()
finally:
    shutil.rmtree(scratch)
assert not scratch.exists()
print(json.dumps({"success":True,"base_revision":REVISION,"native_files":3,"wpt_files":5,"callbacks_from_authenticated_prior_rosters":188,
 "exact_candidate_origins":True,"forward_reverse_zero_fuzz_zero_offset":True,"patch_operations":2,"references":len(references),
 "resources_unchanged":True,"scratch":str(scratch),"scratch_removed":True,
 "native_compile":False,"browser_execution":False,"new_lint_or_manifest_generation":False}))
