import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
here = Path(__file__).resolve().parent
root = here.parents[1]
compiler = root / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
assert hashlib.sha256(compiler.read_bytes()).hexdigest() == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
scratch = Path(tempfile.mkdtemp(prefix="css-stepped-witness-", dir="/private/tmp"))
records = []
try:
    for name in ("Stepped.lean", "NegativeZero.lean", "NegativeKnowledge.lean"):
        shutil.copyfile(here / name, scratch / name)
    env = dict(os.environ, LEAN_PATH=str(scratch))
    for name in ("Stepped.lean", "NegativeZero.lean", "NegativeKnowledge.lean"):
        command = [str(compiler), str(scratch / name)]
        if name == "Stepped.lean":
            command += ["-o", str(scratch / "Stepped.olean")]
        result = subprocess.run(command, cwd=scratch, env=env, text=True, capture_output=True)
        records.append(dict(source=name, exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
    assert records[0]["exit"] == 0
    assert records[0]["stdout"].count("does not depend on any axioms") == 3
    assert records[0]["stdout"].count("depends on axioms: [propext]") == 2
    assert "sorryAx" not in records[0]["stdout"]
    for record in records[1:]:
        assert record["exit"] != 0 and "is false" in record["stdout"]
finally:
    shutil.rmtree(scratch)
    (args.output / "RESULT.json").write_text(json.dumps(dict(records=records, scratch_removed=not scratch.exists()), indent=2) + "\n")
