import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
here = Path(__file__).resolve().parent
root = here.parents[1]
pins = json.loads((here / "BITFLAGS-SOURCE-PINS.json").read_text())
for name, pin in pins.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == pin, name
with tempfile.TemporaryDirectory(prefix="css-bitflags-replay-", dir="/private/tmp") as temp:
    temp = Path(temp)
    lib = temp / "libbitflags.rlib"
    binary = temp / "probe"
    subprocess.run(["rustc", "--crate-name", "bitflags", "--crate-type", "rlib", "--edition", "2021",
                    str(root / "third_party/rust/bitflags/src/lib.rs"), "-o", str(lib)], check=True)
    subprocess.run(["rustc", "--edition", "2021", str(here / "bitflags_probe.rs"),
                    "--extern", "bitflags=" + str(lib), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
for name, pin in pins.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == pin, name
