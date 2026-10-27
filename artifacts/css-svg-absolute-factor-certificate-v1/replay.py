import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(exist_ok=False)
    inputs = json.loads((HERE / "INPUTS.json").read_text())
    for name, digest in inputs.items():
        assert sha(ROOT / name) == digest, name
        if Path(name).name == "FILES.json":
            for child, expected_hash in json.loads((ROOT / name).read_text()).items():
                assert sha((ROOT / name).parent / child) == expected_hash, child
    transfer = json.loads((HERE / "TRANSFER.json").read_text())
    source = (HERE / "Certificate.lean").read_text()
    names = ["px", "cm", "mm", "in", "pt", "pc", "q"]
    for label, data in transfer.items():
        log = ROOT / data["log"]
        assert sha(log) == data["log_sha256"]
        rows = [json.loads(line) for line in log.read_text().splitlines()]
        assert [(r["target"], r["source"]) for r in rows] == [(t, s) for t in names for s in names]
        bits = []
        for row in rows:
            value = row["actual"]
            raw = struct.pack(">f", value)
            assert struct.unpack(">f", raw)[0] == value
            bits.append(int.from_bytes(raw, "big"))
        assert bits == data["bits"]
        declaration = "def " + label + "Bits : List Nat := [\n  " + ", ".join(map(str, bits)) + "]"
        assert declaration in source
    compiler = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
    env = dict(os.environ, LEAN_NUM_THREADS="2", LEAN_PATH=str(ROOT / "artifacts/css-spec-lean/.lake/build/lib/lean"))
    cases = [("main", source, 0),
             ("negative-original", source + "\n#eval decide (∀ row ∈ AbsoluteFactorCertificate.original, AbsoluteFactorCertificate.close row)\n", 0),
             ("negative-exact", source + "\n#eval decide (∀ row ∈ AbsoluteFactorCertificate.candidate, AbsoluteFactorCertificate.decode row.2 = AbsoluteFactorCertificate.oracle row.1)\n", 0)]
    receipts = []
    with tempfile.TemporaryDirectory(prefix="owned-lean-", dir=output) as temporary:
        for name, text, expected in cases:
            path = Path(temporary) / (name + ".lean")
            path.write_text(text)
            run = subprocess.run([str(compiler), str(path)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
            log = run.stdout + run.stderr
            (output / (name + ".log")).write_text(log)
            assert run.returncode == expected, (name, run.returncode, log)
            if name == "main":
                assert "sorryAx" not in log and "error:" not in log
                assert log.count("AbsoluteFactorCertificate.") == 4
            else:
                assert log.strip().endswith("false") and "error:" not in log and "sorryAx" not in log
            receipts.append({"case": name, "exit": run.returncode, "log_sha256": sha(output / (name + ".log"))})
    for name, digest in inputs.items():
        assert sha(ROOT / name) == digest, name
    result = {"source_sha256": sha(HERE / "Certificate.lean"), "compiler_sha256": sha(compiler),
              "binary32_values_transferred": 98, "cases": receipts,
              "threads": 2, "new_target_directories": False, "temporary_products_removed": True}
    (output / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
