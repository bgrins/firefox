import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root.parents[1]
source = repo / "artifacts/css-flex-collapsed-allocation-proof-v1/source/nsFlexContainerFrame.cpp"
assert hashlib.sha256(source.read_bytes()).hexdigest() == "138d027000eecc30ec74ddda2653787c383eecf805c733b9022181c085d75d79"
s = source.read_text()
a = s.index("void FlexLine::ComputeCrossSizeAndBaseline(")
b = s.index("\nnscoord FlexLine::ExtractBaselineOffset(", a)
assert root.joinpath("ComputeCrossSizeAndBaseline.cpp").read_text() == s[a:b]
assert root.joinpath("driver.cpp").read_text().count(s[a:b]) == 1
config = json.loads((repo / "artifacts/css-flex-collapsed-allocation-proof-v1/TOOLCHAIN.json").read_text())
for tool in ["lean", "clang"]:
    assert hashlib.sha256(Path(config[tool]).read_bytes()).hexdigest() == config[tool + "_sha256"]
records = []
def run(args):
    p = subprocess.run(args, text=True, capture_output=True)
    record = {"command": list(map(str,args)), "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    records.append(record)
    root.joinpath("RUN.json").write_text(json.dumps(records, indent=2) + "\n")
    return p
p = run([config["lean"], str(root / "Boundary.lean")])
assert p.returncode == 0 and "sorryAx" not in p.stdout and "Lean.ofReduceBool" not in p.stdout
products = []
for opt in ["-O0", "-O2"]:
    binary = root / ("native" + opt)
    p = run([config["clang"], "-std=c++17", opt, "-fsanitize=undefined", "-fno-sanitize-recover=undefined", str(root / "driver.cpp"), "-o", str(binary)])
    assert p.returncode == 0
    for mode in range(4):
        p = run([str(binary), str(mode)])
        if mode in [0,2]:
            assert p.returncode != 0 and "signed integer overflow" in p.stderr
            assert "1073741823 + 2147483646" in p.stderr
        elif mode == 1:
            assert p.returncode == 0 and p.stdout.strip() == "700000000 -1073741823 2100000000" and not p.stderr
        else:
            assert p.returncode == 0 and p.stdout.strip() == "-1073741823 -1073741823 1073741823" and not p.stderr
    products.append({"path": str(binary), "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "size": binary.stat().st_size})
    binary.unlink()
root.joinpath("CLEANUP.json").write_text(json.dumps(products, indent=2) + "\n")
print("PASS: four Lean boundary results, eight extracted-native checks; no browser reachability claim")
