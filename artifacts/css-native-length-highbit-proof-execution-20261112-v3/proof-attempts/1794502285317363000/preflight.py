from pathlib import Path
import hashlib, json, os, re

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def authenticate(path, digest):
    assert SHA(path / "FILES.json") == digest
    files = json.loads((path / "FILES.json").read_text())
    for name, record in files.items():
        expected = record["sha256"] if isinstance(record, dict) else record
        assert SHA(path / name) == expected, name
    return len(files)

def preflight():
    prep = json.loads((BASE / "PREPARATION.json").read_text())
    for name, digest in prep["files"].items():
        assert SHA(BASE / name) == digest, name
    target = REPO / prep["target"]["path"]
    target_files = authenticate(target, prep["target"]["manifest_sha256"])
    root_files = authenticate(REPO / prep["root_review"]["path"], prep["root_review"]["manifest_sha256"])
    for name in ["Target.lean", "Controls.lean", "Types.lean", "DECLARATIONS.json"]:
        assert (BASE / name).read_bytes() == (target / name).read_bytes()
    assert SHA(REPO / prep["lean"]["path"]) == prep["lean"]["sha256"]
    assert SHA(BASE / "lifecycle.py") == "da8875e2b1da2bbee84d64dfb639c1454c9735dbb88fba76d4df90958b6765a4"
    assert prep["limits"] == dict(workers=1, seconds=60, rss_bytes=2147483648)
    assert prep["modules"] == ["Target", "Controls", "Proof", "ControlProof", "Types", "ProofTypes", "Audit"]
    for key in ["LEAN_SYSROOT", "LEAN_OPTS"]:
        assert not os.environ.get(key), key
    new = []
    for name, prefix in [("Proof.lean", "CssNativeHighBit."), ("ControlProof.lean", "CssNativeHighBit.CheckedControls.")]:
        text = (BASE / name).read_text()
        assert not re.search(r"\b(sorry|axiom|unsafe|native_decide)\b", text)
        new += [prefix + n for n in re.findall(r"^theorem (\w+)", text, re.M)]
    plan = json.loads((BASE / "AUDIT-PLAN.json").read_text())
    assert new == plan["new_theorems"] and len(new) == 32
    inherited = json.loads((BASE / "INHERITED-AUDIT.json").read_text())
    assert list(inherited) == plan["inherited_exact_names"]
    assert list(inherited) + new == plan["names"] and len(plan["names"]) == 82
    assert (BASE / "Audit.lean").read_text() == "import ControlProof\n\n" + "".join("#print axioms " + name + "\n" for name in plan["names"])
    return dict(source_preflight=True, protected_target_files=target_files,
                root_review_files=root_files, obligation_fields=15, control_fields=6,
                draft_theorems=32, audits=82, commands=7,
                compiler_started=False, native_cells_checked=0)

if __name__ == "__main__":
    print(json.dumps(preflight(), indent=2))
