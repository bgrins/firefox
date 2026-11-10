import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(destination):
    manifest = json.loads((HERE / "REPLAY-INPUTS.json").read_text())
    assert all(sha(HERE / path) == digest for path, digest in manifest["files"].items())
    roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
    for path in roles:
        target = destination / "base" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(
            subprocess.check_output(
                [
                    "git",
                    "-c",
                    "core.fsmonitor=false",
                    "show",
                    manifest["base_revision"] + ":" + path,
                ],
                cwd=ROOT,
            )
        )
    logs = []
    for source, target, patch in [
        ("base", "semantic", "semantic.patch"),
        ("semantic", "candidate", "instrumentation.patch"),
    ]:
        shutil.copytree(destination / source, destination / target)
        result = subprocess.run(
            ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(HERE / patch)],
            cwd=destination / target,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "offset" not in result.stdout and "fuzz" not in result.stdout
        logs.append(result.stdout)
    for path, record in roles.items():
        for stage, digest in record.items():
            assert sha(destination / stage / path) == digest
    return {
        "base_revision": manifest["base_revision"],
        "source_hashes_checked": len(roles) * 3,
        "patch_logs": logs,
        "live_sources_modified": False,
    }


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Run with python -I and without -O")
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="css-named-timeline-replay-") as scratch:
        destination = Path(scratch)
        result = prepare(destination)
        if args.materialize:
            for stage in ["base", "semantic", "candidate"]:
                assert not (HERE / stage).exists()
            for stage in ["base", "semantic", "candidate"]:
                shutil.copytree(destination / stage, HERE / stage)
    result["temporary_replay_removed"] = not destination.exists()
    result["materialized"] = args.materialize
    (HERE / "REPLAY.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
