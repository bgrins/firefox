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
    sources = [json.loads((HERE / name).read_text()) for name in ["SOURCE.json", "INFRA.json"]]
    library = json.loads((HERE / "LIBRARY.json").read_text())
    frozen = json.loads((HERE / "FREEZE.json").read_text())
    names = sorted(set(frozen["files"]) | set(library["files"]) |
        {source["file"] for source in sources} | {"FREEZE.json", "Bridge.lean", "Examples.lean", "check.py"})
    folder = Path(tempfile.mkdtemp(prefix="source-replay-", dir=HERE))
    for name in names:
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / name, target)
    argv = [sys.executable, "-I", "-B", str(folder / "check.py"), "--lean", str(args.lean.resolve())]
    process = subprocess.run(argv, capture_output=True, text=True)
    (HERE / "replay.log").write_text(process.stdout + process.stderr)
    if process.returncode:
        raise SystemExit(f"Replay failed; source copy retained at {folder}; see replay.log")
    result = json.loads((folder / "RESULT.json").read_text())
    result["source_only_replay"] = {
        "copied_files": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
        "no_generated_or_compiled_inputs_copied": True,
    }
    (HERE / "REPLAY-RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    logs = HERE / "replay-logs"
    if logs.exists():
        shutil.rmtree(logs)
    shutil.copytree(folder / "logs", logs)
    shutil.rmtree(folder)
    print(json.dumps({"passed": True, "copied_files": len(names), "temporary_replay_removed": True}))


if __name__ == "__main__":
    main()
