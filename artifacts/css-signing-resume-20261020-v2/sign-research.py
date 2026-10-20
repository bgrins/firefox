import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
HELPER = ROOT / "artifacts/css-ahom-lf-partition-probe-v1/commit-item-v2.py"
GIT = ["git", "-c", "core.fsmonitor=false"]

def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)

state = json.loads((ROOT / "artifacts/css-cssom-exact-traversal-standalone-v4/STATE.json").read_text())
assert state["status"] == "terminal"
assert state["candidate_build_exit"] == state["restore_build_exit"] == 0
assert all(state[k] for k in ["exact_oracle_match", "source_restored", "other_native_unchanged", "head_unchanged", "index_unchanged"])
previous = "99a9ca84f08370c1797720db8688bcb3747f6985"
assert git("rev-parse", "HEAD").decode().strip() == previous
recipes = [
    "artifacts/css-cssom-exact-traversal-commit-v3/lifecycle-results.json",
    "artifacts/css-cssom-exact-traversal-commit-v3/runtime-results.json",
    "artifacts/css-cssom-exact-traversal-commit-v4/research-source-draft.json",
    "artifacts/css-cssom-exact-traversal-commit-v4/research-runtime-draft.json",
    "artifacts/css-primary-destruction-ownership-refinement-commit-v1/draft.json",
]
records = []
for number, name in enumerate(recipes, 1):
    assert git("rev-parse", "HEAD").decode().strip() == previous
    source = ROOT / name
    item = json.loads(source.read_text())
    assert set(item["files"]) == set(item["source_pins"])
    assert all(path.startswith("artifacts/") for path in item["files"])
    for path, expected in item["source_pins"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    item["expected_head"] = previous
    finalized = HERE / (str(number) + "-recipe.json")
    assert not finalized.exists()
    finalized.write_text(json.dumps(item, indent=2) + "\n")
    print("Signing " + str(number) + "/5: " + item["message"], flush=True)
    log = HERE / (str(number) + "-signing.log")
    with log.open("w") as output:
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(HELPER), str(finalized)], cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
    receipt_path = HELPER.parent / (item["id"] + "-receipt.json")
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    record = {"recipe": str(finalized.relative_to(ROOT)), "exit": result.returncode, "receipt": receipt}
    records.append(record)
    (HERE / "SIGNING.json").write_text(json.dumps(records, indent=2) + "\n")
    if result.returncode:
        print("Signing stopped; see " + str(log), flush=True)
        raise SystemExit(result.returncode)
    assert receipt["before"] == previous and receipt["signature_present"]
    previous = receipt["after"]
    assert git("rev-parse", "HEAD").decode().strip() == previous
    assert not git("diff", "--cached", "--name-only").strip()
    print("Committed " + previous, flush=True)
print("Research queue complete; no native fixes added.", flush=True)
