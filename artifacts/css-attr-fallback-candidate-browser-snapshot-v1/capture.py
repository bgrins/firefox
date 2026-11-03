import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RUNTIME = ROOT / "artifacts/css-attr-fallback-candidate-browser-runtime-v2"
APP = ROOT / "objdir-full.noindex/dist/Nightly.app"
SOURCE = ROOT / "servo/components/style/custom_properties.rs"
EXPECTED = "099e4bb5febe0e0519b54f6f08c8af68ac2d242aca824bb6d27b72addd605cc7"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
receipt_path = RUNTIME / "candidate-build/RESULT.json"
deadline = time.monotonic() + 2400
assert not (OUT / "RESULT.json").exists()
while not receipt_path.is_file():
    assert time.monotonic() < deadline, "Candidate build receipt timeout"
    assert not (RUNTIME / "RESULT.json").exists(), "Owner terminated before successful build receipt"
    time.sleep(1)
receipt_bytes = receipt_path.read_bytes()
receipt = json.loads(receipt_bytes)
assert receipt["command_success"] and receipt["browser_build_performed"]
assert receipt["native_sources"] == {str(SOURCE.relative_to(ROOT)): EXPECTED}
assert receipt["application_metadata"]["source_role"] == "candidate"
assert receipt["application_metadata"]["revision"] == "e86b64866cdc5e2260ba9be08c45756fd96e21bb"
assert sha(SOURCE) == EXPECTED
assert all(sha(ROOT / name) == pin for name, pin in receipt["binaries"].items())
assert shutil.disk_usage(ROOT).free > 27 * 1024**3


def inventory(app):
    result = {}
    for directory, _, names in os.walk(app, followlinks=True):
        for name in names:
            path = Path(directory) / name
            assert path.is_file(), path
            result[str(path.relative_to(app))] = {
                "bytes": path.stat().st_size,
                "mode": stat.S_IMODE(path.stat().st_mode),
                "sha256": sha(path),
            }
    return result


owned = None
try:
    before = inventory(APP)
    assert sha(SOURCE) == EXPECTED
    owned = Path(tempfile.mkdtemp(prefix="css-fallback-candidate-browser-"))
    copy = owned / "Nightly.app"
    print("Copying completed candidate application", flush=True)
    shutil.copytree(APP, copy, symlinks=False)
    copied = inventory(copy)
    after = inventory(APP)
    assert before == copied == after
    assert all(not path.is_symlink() for path in copy.rglob("*"))
    assert sha(SOURCE) == EXPECTED
    assert receipt_path.read_bytes() == receipt_bytes
    assert all(sha(ROOT / name) == pin for name, pin in receipt["binaries"].items())
    record = {
        "captured": True, "application": str(copy), "owned_directory": str(owned),
        "source_role": "candidate", "native_sources": receipt["native_sources"],
        "application_metadata": receipt["application_metadata"],
        "build_receipt": str(receipt_path.relative_to(ROOT)),
        "build_receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "files": copied, "bytes": sum(row["bytes"] for row in copied.values()),
        "purpose": "Supplemental selected-empty and unused-fallback regression tests; remove after validation",
        "active_source_application_index_changed": False,
    }
    (OUT / "SNAPSHOT.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    (OUT / "RESULT.json").write_text(json.dumps({"captured": True, "application": str(copy),
                                                "files": len(copied), "bytes": record["bytes"],
                                                "snapshot_sha256": sha(OUT / "SNAPSHOT.json")}, indent=2) + "\n")
    print("Verified candidate archive", len(copied), "files", str(copy), flush=True)
except BaseException as error:
    if owned is not None:
        shutil.rmtree(owned)
    (OUT / "RESULT.json").write_text(json.dumps({"captured": False, "error": repr(error),
                                                "traceback": traceback.format_exc(),
                                                "owned_copy_removed": owned is None or not owned.exists()}, indent=2) + "\n")
    raise
