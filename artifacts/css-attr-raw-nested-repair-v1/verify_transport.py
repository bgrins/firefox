import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S -B without optimization")
sys.dont_write_bytecode = True
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

here = Path(__file__).resolve().parent
base = json.loads((here / "BASE.json").read_text())
new_wpt = (here / "NEW-WPT-PATH.txt").read_text().strip()
native = "servo/components/style/properties/cascade.rs"
records = {}
for variant in ("live", "head"):
    with tempfile.TemporaryDirectory(prefix="raw-attr-transport-", dir="/private/tmp") as directory:
        work = Path(directory)
        for name in base["paths"]:
            source = here / ("head-base" if variant == "head" and name == native else "base") / name
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        operations = []
        for arguments in (["--check"], [], ["--reverse", "--check"], ["--reverse"], []):
            command = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                       "apply", *arguments, str(here / "fix.patch")]
            result = subprocess.run(command, cwd=work, capture_output=True, text=True)
            operations.append({"arguments": arguments, "exit": result.returncode,
                               "stdout": result.stdout, "stderr": result.stderr})
            assert result.returncode == 0, operations[-1]
            if arguments in ([], ["--reverse"]):
                candidate = not arguments
                expected = set(base["paths"]) | ({new_wpt} if candidate else set())
                assert {str(f.relative_to(work)) for f in work.rglob("*") if f.is_file()} == expected
                for name in expected:
                    role = "candidate" if candidate else "base"
                    if variant == "head" and name == native:
                        role = "head-" + role
                    assert (work / name).read_bytes() == (here / role / name).read_bytes(), name
        records[variant] = {"operations": operations, "exact_postimages": True,
                            "exact_reverse_preimages": True, "scratch": str(work)}
    records[variant]["scratch_removed"] = not work.exists()
print(json.dumps(records, indent=2))
