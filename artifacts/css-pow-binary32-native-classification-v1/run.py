import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
here = Path(__file__).resolve().parent
assert len(sys.argv) == 2 and Path(sys.argv[1]).name == sys.argv[1]
out = here / sys.argv[1]
out.mkdir()
launcher = shutil.which("rustc")
compiler = Path(subprocess.check_output([launcher, "--print", "sysroot"], text=True).strip()) / "bin/rustc"
version = subprocess.check_output([str(compiler), "-vV"], text=True)
(out / "rustc-version.txt").write_text(version)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
records = []
with tempfile.TemporaryDirectory(prefix="css-pow-bits-native-") as temporary:
    binary = Path(temporary) / "check"
    commands = [([str(compiler), "--edition=2021", "-O", str(here / "check.rs"), "-o", str(binary)], 60),
                ([str(binary)], 180)]
    for index, (command, timeout) in enumerate(commands):
        start = time.monotonic()
        with (out / f"step-{index}.log").open("x") as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        records.append({"command": command, "exit": result.returncode, "elapsed_seconds": time.monotonic() - start})
        (out / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
        assert result.returncode == 0
    assert (out / "step-1.log").read_text() == "All 4294967296 binary32 encodings matched all three native predicates\n"
    binary_sha = sha(binary)
assert not binary.exists()
(out / "CHECK.json").write_text(json.dumps({
    "success": True, "encodings": 4294967296, "predicates_per_encoding": 3,
    "compiler_path": str(compiler), "compiler_sha256": sha(compiler),
    "binary_sha256": binary_sha, "source_sha256": sha(here / "check.rs"),
    "platform": platform.platform(), "machine": platform.machine(),
    "temporary_binary_removed": True, "native_stylo_compiled": False,
    "formal_native_refinement_proved": False,
}, indent=2, sort_keys=True) + "\n")
print("Exhaustive host classification check passed; temporary binary removed")
