import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root.parents[1]
prior = repo / "artifacts/css-flex-cross-baseline-boundary-root-v1"
source = root / "candidate-nsFlexContainerFrame.cpp"
pins = json.loads((root / "SOURCE-CHANGE.json").read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest() == pins["candidate"]
s = source.read_text()
a = s.index("void FlexLine::ComputeCrossSizeAndBaseline(")
b = s.index("\nnscoord FlexLine::ExtractBaselineOffset(", a)
body = s[a:b]
old = (prior / "ComputeCrossSizeAndBaseline.cpp").read_text()
driver = (prior / "driver.cpp").read_text()
assert driver.count(old) == 1
driver = driver.replace(old, body).replace("constexpr nscoord nscoord_MIN", "constexpr nscoord nscoord_MAX = 1073741823;\nconstexpr nscoord nscoord_MIN")
(root / "arithmetic-driver.cpp").write_text(driver)
config = json.loads((repo / "artifacts/css-flex-collapsed-allocation-proof-v1/TOOLCHAIN.json").read_text())
records = []
def run(args):
    p = subprocess.run(args, text=True, capture_output=True)
    records.append({"command": list(map(str,args)), "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr})
    (root / "ARITHMETIC-RUN.json").write_text(json.dumps(records,indent=2)+"\n")
    return p
for tool in ["lean","clang"]:
    assert hashlib.sha256(Path(config[tool]).read_bytes()).hexdigest() == config[tool+"_sha256"]
p = run([config["lean"], str(root / "Arithmetic.lean")])
assert p.returncode == 0 and not p.stderr and "sorryAx" not in p.stdout and "Lean.ofReduceBool" not in p.stdout
products=[]
for opt in ["-O0","-O2"]:
    binary = root / ("arithmetic"+opt)
    p = run([config["clang"], "-std=c++17", opt, "-fsanitize=undefined", "-fno-sanitize-recover=undefined", str(root / "arithmetic-driver.cpp"), "-o", str(binary)])
    assert p.returncode == 0
    for mode in range(4):
        p = run([str(binary),str(mode)])
        expected=["1073741823 -1073741823 1073741823", "700000000 -1073741823 1073741823", "-1073741823 2147483646 1073741823", "-1073741823 -1073741823 1073741823"][mode]
        assert p.returncode == 0 and not p.stderr and p.stdout.strip() == expected
    products.append({"path":str(binary),"sha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"size":binary.stat().st_size})
    binary.unlink()
(root / "ARITHMETIC-CLEANUP.json").write_text(json.dumps(products,indent=2)+"\n")
print("PASS: six kernel results and eight corrected extracted-native checks")
