from pathlib import Path
import hashlib, json, os

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def preflight():
    preparation = json.loads((BASE / "PREPARATION.json").read_text())
    for relative, digest in preparation["files"].items():
        assert SHA(BASE / relative) == digest, relative
    prior = REPO / preparation["target"]["path"]
    assert SHA(prior / "FILES.json") == preparation["target"]["manifest_sha256"]
    frozen = json.loads((prior / "FILES.json").read_text())
    for relative, digest in frozen.items():
        assert SHA(prior / relative) == digest, relative
    for name in ["Target.lean", "Controls.lean", "Types.lean", "DECLARATIONS.json"]:
        assert (BASE / name).read_bytes() == (prior / name).read_bytes(), name
    lean = REPO / preparation["lean"]["path"]
    assert SHA(lean) == preparation["lean"]["sha256"]
    assert SHA(BASE / "lifecycle.py") == "da8875e2b1da2bbee84d64dfb639c1454c9735dbb88fba76d4df90958b6765a4"
    for key in ["LEAN_SYSROOT", "LEAN_OPTS"]:
        assert not os.environ.get(key), key
    assert preparation["limits"] == dict(workers=1, seconds=60, rss_bytes=2147483648)
    assert preparation["modules"] == ["Target", "Controls", "Types", "Audit"]
    expected = json.loads((BASE / "AUDIT-EXPECTED.json").read_text())
    assert len(expected) == 50 and all(value == [] for value in expected.values())
    assert (BASE / "Audit.lean").read_text() == "import Controls\n\n" + "".join("#print axioms " + name + "\n" for name in expected)
    return dict(source_preflight=True, target_files=len(frozen), commands=4,
                field_types=15, control_types=6, declaration_audits=50,
                compiler_started=False, native_cells_checked=0)

if __name__ == "__main__":
    print(json.dumps(preflight(), indent=2))
