import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
source = (HERE / "candidate/servo/components/style/values/generics/calc.rs").read_text()
start = source.index("fn pow(")
end = source.index("\n}\n", start) + 3
helper = source[start:end]
assert helper in (HERE / "arithmetic-check.rs").read_text()
print("exact proposed helper sha256", hashlib.sha256(helper.encode()).hexdigest(), flush=True)
subprocess.run(["rustc", "--version"], check=True)
with tempfile.TemporaryDirectory(prefix="css-pow-arithmetic-") as temporary:
    binary = Path(temporary) / "check"
    subprocess.run(["rustc", "--edition=2021", "-O", str(HERE / "arithmetic-check.rs"), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print(json.dumps({"temporary_binary_removed": True, "native_stylo_compiled": False,
                  "repository_source_modified": False}))
