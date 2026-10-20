import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
CAPSULE = HERE / "capsule"
lean = Path(json.loads((CAPSULE / "LEAN-TOOLCHAIN.json").read_text())["root"]) / "bin/lean"
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
out = parser.parse_args().output.resolve()
out.mkdir(exist_ok=False)
records = []
for name, axiom in [("sorry", "sorryAx"), ("custom", "MaskedSticky.auditForbidden")]:
    with tempfile.TemporaryDirectory(prefix="sticky-axiom-control-") as temporary:
        work = Path(temporary)
        shutil.copytree(CAPSULE / "lean", work / "lean")
        for filename in ["check_lean.py", "AUDIT-ROSTER.json"]:
            shutil.copy2(CAPSULE / filename, work / filename)
        source = work / "lean/MaskedSticky.lean"
        text = source.read_text()
        original = "native auto none n l = n := rfl"
        assert text.count(original) == 1
        if name == "sorry":
            text = text.replace(original, "native auto none n l = n := by sorry")
        else:
            text = text.replace("theorem missing_identity", "axiom auditForbidden : False\n\ntheorem missing_identity")
            text = text.replace(original, "native auto none n l = n := False.elim auditForbidden")
        source.write_text(text)
        (out / (name + ".lean")).write_text(text)
        target = out / name
        command = [sys.executable, "-I", "-S", str(work / "check_lean.py"),
                   "--lean", str(lean), "--output", str(target)]
        result = subprocess.run(command, cwd=work, capture_output=True, text=True)
        (out / (name + ".log")).write_text(result.stdout + result.stderr)
        assert result.returncode != 0 and "unsupported axiom" in result.stderr
        assert axiom in (target / "Audit.log").read_text()
        assert not (target / "FAILED.json").exists() and not (target / "RESULT.json").exists()
        for module in ["MaskedSticky", "StickyComposition", "StickyLifecycle", "Audit"]:
            assert "error:" not in (target / (module + ".log")).read_text()
        records.append({"name": name, "rejected_axiom": axiom, "exit": result.returncode,
                        "compilation_completed": True, "rejected_during_axiom_audit": True})
(out / "RESULT.json").write_text(json.dumps({"status": "pass", "controls": records,
    "temporary_source_and_compiler_products_removed": True}, indent=2) + "\n")
print(json.dumps({"status": "pass", "controls": len(records)}))
