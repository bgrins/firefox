import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run(args, cwd=None):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result.stdout


roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
for path, expected in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert digest((ROOT / path).read_bytes()) == expected, path
for path, role in roles.items():
    assert digest((HERE / "candidate" / path).read_bytes()) == role["candidate_sha256"]
    if role["base_sha256"]:
        assert digest((HERE / "base" / path).read_bytes()) == role["base_sha256"]
        assert digest(subprocess.check_output(["git", "show", role["base_revision"] + ":" + path], cwd=ROOT)) == role["base_sha256"]

historical = ROOT / "artifacts/css-layer-cutoff-composition-probe-v1/fix-a-b-d-v1.patch"
scratch = Path(tempfile.mkdtemp(prefix="rollback-e86-rebase-"))
try:
    for label, patch in [("historical", historical), ("rebased", HERE / "native.patch")]:
        tree = scratch / label
        shutil.copytree(HERE / "base", tree)
        run(["patch", "--batch", "--fuzz=0", "-p1", "-i", str(patch)], tree)
        for path in roles:
            assert (tree / path).read_bytes() == (HERE / "candidate" / path).read_bytes(), path
        run(["patch", "--batch", "--fuzz=0", "-R", "-p1", "-i", str(patch)], tree)
        for path, role in roles.items():
            if role["base_sha256"]:
                assert (tree / path).read_bytes() == (HERE / "base" / path).read_bytes()
            else:
                assert not (tree / path).exists()
    for path in roles:
        if path.endswith(".rs"):
            result = subprocess.run(["rustfmt", "--edition", "2024", "--emit", "stdout", str(HERE / "candidate" / path)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            assert result.returncode == 0, result.stderr.decode()
    js = """const fs=require('fs'),vm=require('vm');
const names=[]; const source=fs.readFileSync(process.argv[1],'utf8');
const bodies=[...source.matchAll(/<script>([\\s\\S]*?)<\\/script>/g)];
for(const match of bodies) new vm.Script(match[1]).runInNewContext({test:(body,name)=>names.push(name)});
process.stdout.write(JSON.stringify(names));"""
    roster = {}
    for path in roles:
        if path.endswith(".html"):
            names = json.loads(run(["node", "-e", js, str(HERE / "candidate" / path)]))
            assert len(names) == len(set(names))
            roster[path] = names
    counts = sorted(map(len, roster.values()))
    assert counts == [16, 16, 48], counts
    dpath = "testing/web-platform/tests/css/css-cascade/revert-layer-preserves-inline-exclusion.html"
    d48 = (HERE / "candidate" / dpath).read_text()
    d64 = (HERE / "held/revert-layer-preserves-inline-exclusion-64.html").read_text()
    assert d48 == d64.replace('["revert-layer", "revert-rule", "revert", "9px"]', '["revert-layer", "revert", "9px"]')
    assert d48 == (ROOT / "artifacts/css-layer-cutoff-composition-probe-v1/without-c-D48.html").read_text()
    full = json.loads(run(["node", "-e", js, str(HERE / "held/revert-layer-preserves-inline-exclusion-64.html")]))
    omitted = [name for name in full if name not in roster[dpath]]
    assert len(full) == 64 and len(omitted) == 16
    assert all(": inline revert-rule," in name for name in omitted)
    (HERE / "ROSTER.json").write_text(json.dumps({"selected": roster, "held_C_boundary": omitted, "callbacks": 80, "executed_callbacks": 0}, indent=2) + "\n")
    for resource in json.loads((HERE / "RESOURCES.json").read_text()).values():
        assert digest((ROOT / resource["path"]).read_bytes()) == resource["sha256"]
finally:
    shutil.rmtree(scratch)
assert not scratch.exists()
print(json.dumps({"source_roles": 2, "fixture_paths": 3, "callbacks_registered_only": 80, "held_C_callbacks": 16, "historical_and_rebased_roundtrips": True, "rustfmt_parser_only": True, "native_typecheck": False, "browser_execution": False, "scratch_removed": True}))
