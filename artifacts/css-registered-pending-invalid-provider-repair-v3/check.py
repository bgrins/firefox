import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
for name, expected in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
for name, pins in roles.items():
    for role in ["base", "candidate"]:
        assert hashlib.sha256((HERE / role / name).read_bytes()).hexdigest() == pins[role + "_sha256"]
for name in roles:
    flags = ["--config", "reorder_imports=false"] if name.endswith("cascade.rs") else []
    subprocess.run(["rustfmt", "--check", "--edition", "2024", *flags,
                    "--config-path", str(ROOT / "servo/rustfmt.toml"),
                    str(HERE / "candidate" / name)], check=True)
with tempfile.TemporaryDirectory(prefix="provider-v3-transport-") as tmp:
    scratch = Path(tmp)
    for name in roles:
        output = scratch / name
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / "base" / name, output)
    for flags, role in [([], "candidate"), (["-R"], "base"), ([], "candidate")]:
        result = subprocess.run(["patch", "--fuzz=0", "-p1", *flags,
                                 "-i", str(HERE / "native.patch")], cwd=scratch,
                                text=True, capture_output=True, check=True)
        assert "offset" not in result.stdout and "fuzz" not in result.stdout
        assert {str(f.relative_to(scratch)) for f in scratch.rglob("*") if f.is_file()} == set(roles)
        for name in roles:
            assert (scratch / name).read_bytes() == (HERE / role / name).read_bytes()
print(json.dumps({"references_authenticated": True, "native_paths": len(roles),
                  "transport": "exact forward/reverse/reapply, no fuzz or offset",
                  "rustfmt": "passed", "owned_scratch": "removed",
                  "compiled": False, "browser_tested": False}))
