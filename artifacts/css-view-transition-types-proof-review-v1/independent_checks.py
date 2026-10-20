import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("use -I -S")
sys.dont_write_bytecode = True
import hashlib, itertools, json, os, shutil, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "capsule"
records = []
with tempfile.TemporaryDirectory(prefix="vt-independent-") as temporary:
    work = Path(temporary)
    tests = ["optimized", "double-optimized", "nonisolated-shadow", "site-enabled",
             "extra-directory", "extra-fifo", "source-change", "symlink-source",
             "duplicate-json", "duplicate-path", "path-escape", "internal-output"]
    for name in tests:
        capsule = work / name
        shutil.copytree(SRC, capsule)
        output = work / (name + "-output")
        marker = work / (name + "-import-marker")
        flags = ["-I", "-S"]
        if name == "optimized": flags += ["-O"]
        if name == "double-optimized": flags += ["-OO"]
        if name == "site-enabled": flags = ["-I"]
        if name == "nonisolated-shadow":
            flags = ["-S"]
            (capsule / "json.py").write_text("open(" + repr(str(marker)) + ", 'w').write('executed')\n")
        if name == "extra-directory": (capsule / "extra").mkdir()
        if name == "extra-fifo": os.mkfifo(capsule / "pipe")
        if name == "source-change":
            with (capsule / "lean/LiveAtoms.lean").open("a") as f: f.write("\n")
        if name == "symlink-source":
            path = capsule / "lean/LiveAtoms.lean"
            path.unlink(); path.symlink_to(SRC / "lean/LiveAtoms.lean")
        if name == "duplicate-json":
            path = capsule / "FILES.json"
            path.write_text(path.read_text().replace('"path":', '"path":"fake", "path":', 1))
        if name in ["duplicate-path", "path-escape"]:
            path = capsule / "FILES.json"; rows = json.loads(path.read_text())
            if name == "duplicate-path": rows.append(rows[0])
            else: rows[0]["path"] = "../escape"
            path.write_text(json.dumps(rows))
        if name == "internal-output": output = capsule / "generated"
        command = [sys.executable, *flags, str(capsule / "check.py"), "--output", str(output)]
        result = subprocess.run(command, text=True, capture_output=True)
        passed = result.returncode != 0 and not output.exists() and not marker.exists()
        records.append(dict(name=name, exit=result.returncode, output_created=output.exists(),
                            shadow_executed=marker.exists(), passed=passed,
                            stderr=result.stderr))
        if not passed: raise RuntimeError(name)
(ROOT / "INTEGRITY.json").write_text(json.dumps(records, indent=2) + "\n")
cases = json.loads((SRC / "native/CASES.json").read_text())
inputs = [list(xs) for n in range(4) for xs in itertools.product(range(3), repeat=n)]
ops = [[0,0], [0,1], [1,0], [1,1], [2,0], [3,0]]
sequences = [list(xs) for n in range(3) for xs in itertools.product(ops, repeat=n)]
expected = [(xs, sequence) for xs in inputs for sequence in sequences]
actual = [(c['initial'], c['ops']) for c in cases[21:1741]]
if actual != expected: raise RuntimeError("matrix roster")
if len(cases) != 1755 or len({c['name'] for c in cases}) != 1755: raise RuntimeError("closed case roster")
(ROOT / "CORPUS-RECONSTRUCTION.json").write_text(json.dumps(dict(
    total=1755, historical=21, matrix_inputs=len(inputs), matrix_sequences=len(sequences),
    matrix_cases=len(expected), code_unit_cases=12, absent_option_cases=2,
    exact_matrix_reconstructed=True), indent=2) + "\n")
print("12 negative guards and independent 1720-case roster reconstruction passed")
