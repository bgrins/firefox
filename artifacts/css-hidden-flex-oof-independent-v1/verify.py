#!/usr/bin/env python3
import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("run nonoptimized python3 -I -S")

import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
PRODUCER_PIN = "4571c5fd5131906fb0bb34a1c5a40c981d40d1ab926edbfaa4be488224cb0d24"
INSERTION = b"    if (aKidFrame->IsHiddenByContentVisibilityOfInFlowParentForLayout()) {\n      aKidFrame->MarkSubtreeDirty();\n    }\n"


def require(value, message):
    if not value:
        raise SystemExit(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticate(root, pin):
    require(sha((root / "FILES.json").read_bytes()) == pin, "manifest pin")
    manifest = json.loads((root / "FILES.json").read_text())
    found = set()
    for path in root.rglob("*"):
        mode = path.lstat().st_mode
        require(stat.S_ISDIR(mode) or stat.S_ISREG(mode), "nonregular input")
        if stat.S_ISREG(mode):
            found.add(path.relative_to(root).as_posix())
    require(found == set(manifest) | {"FILES.json", "FREEZE.json"}, "closed roster")
    for name, digest in manifest.items():
        require(sha((root / name).read_bytes()) == digest, "payload " + name)
    freeze = json.loads((root / "FREEZE.json").read_text())
    require(freeze["files_sha256"] == pin, "freeze binding")
    return len(manifest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-sha", required=True)
    args = parser.parse_args()
    count = authenticate(ROOT, args.manifest_sha)
    producer = ROOT / "producer"
    require(authenticate(producer, PRODUCER_PIN) == 31, "producer count")
    patch = producer / "candidate-v2.patch"
    require(sha(patch.read_bytes()) == "d5f61ccd4db2871e17e96e5d84cc30dcb59ad92ac3574878d3169cc1999acdf3", "patch pin")
    candidate = (producer / "candidate-v2-AbsoluteContainingBlock.cpp").read_bytes()
    require(sha(candidate) == json.loads((producer / "V2-PROPOSAL.json").read_text())["candidate_sha256"], "CPP role")
    require(candidate.count(INSERTION) == 1, "insertion count")
    require(candidate.replace(INSERTION, b"", 1) == (producer / "local-AbsoluteContainingBlock.cpp").read_bytes(), "source delta")
    require(INSERTION + b"    ReflowInput kidReflowInput" in candidate, "pre-input ordering")
    roster = [f"OOF leaf first: {anc}, {offset}, {insert}" for anc in ["one hidden ancestor", "two hidden ancestors"] for offset in ["static position", "explicit offsets"] for insert in ["append", "prepend"]]
    require(roster == json.loads((producer / "EXPECTED-ROSTER.json").read_text()), "eight test roster")
    checks = json.loads((ROOT / "SOURCE-CHECK.json").read_text())
    for row in checks["bases"]:
        base = ROOT / "bases" / row["role"]
        original = (base / "original.cpp").read_bytes()
        expected = (base / "candidate.cpp").read_bytes()
        require(sha(original) == row["original_sha256"] and sha(expected) == row["candidate_sha256"], "base pins")
        require(expected.replace(INSERTION, b"", 1) == original, "base delta")
        with tempfile.TemporaryDirectory(prefix="oof-review-") as directory:
            target = Path(directory) / "layout/generic/AbsoluteContainingBlock.cpp"
            target.parent.mkdir(parents=True)
            target.write_bytes(original)
            for reverse, wanted in [(False, expected), (True, original)]:
                command = ["patch", "--fuzz=0", "-p1", "-i", str(patch)]
                if reverse:
                    command.append("-R")
                result = subprocess.run(command, cwd=directory, capture_output=True, text=True)
                require(result.returncode == 0 and target.read_bytes() == wanted, result.stdout + result.stderr)
    print(json.dumps({"payloads": count, "producer_payloads": 31, "bases": 2, "apply_reverse": "PASS", "test_roster": 8, "native_runtime": "NOT_RUN"}, sort_keys=True))


if __name__ == "__main__":
    main()
