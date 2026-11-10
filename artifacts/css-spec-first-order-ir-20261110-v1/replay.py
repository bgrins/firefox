import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    args = parser.parse_args()
    (HERE / "REPLAY-RESULT.json").unlink(missing_ok=True)
    prior = json.loads((HERE / "PRIOR.json").read_text())
    names = sorted(set(prior["files"]) | {"PRIOR.json", "FirstOrder.lean", "Lowering.lean", "FOBridge.lean",
        "Reusable.lean", "Examples.lean", "generate.py", "check.py"})
    folder = Path(tempfile.mkdtemp(prefix="source-replay-", dir=HERE))
    for name in names:
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / name, target)
    process = subprocess.run([sys.executable, "-I", "-B", str(folder / "check.py"), "--lean", str(args.lean.resolve())], capture_output=True, text=True)
    (HERE / "replay.log").write_text(process.stdout + process.stderr)
    if process.returncode:
        raise SystemExit(f"Replay failed; source copy retained at {folder}; see replay.log")
    result = json.loads((folder / "RESULT.json").read_text())
    copied = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names}
    result["source_only_replay"] = {"copied_files": copied,
        "newly_generated_first_order_or_compiled_inputs_copied": False,
        "prior_reference_source_includes_historical_generated_lean_and_extraction_parameters": True}
    (HERE / "REPLAY-RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "SOURCE-ONLY.json").write_text(json.dumps({"files": copied}, indent=2) + "\n")
    logs = HERE / "replay-logs"
    if logs.exists():
        shutil.rmtree(logs)
    shutil.copytree(folder / "logs", logs)
    shutil.rmtree(folder)
    print(json.dumps({"passed": True, "copied_files": len(names), "temporary_replay_removed": True}))


if __name__ == "__main__":
    main()
