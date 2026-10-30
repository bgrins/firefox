import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAN = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(LEAN) == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
assert len(sys.argv) == 2 and Path(sys.argv[1]).name == sys.argv[1]
output = HERE / sys.argv[1]
output.mkdir()
names = re.findall(r"^theorem (\w+)", (HERE / "Language.lean").read_text(), re.M)
false_cases = {
 "FailureStoresLanguage": "recordedLanguage 7 none = recordedLanguage 7 (some false)",
 "InvalidCacheIsSafe": "(query (fun _ => some false) (some (7, true)) 7).1 = some false",
 "FailureRetainsOldScript": "(beginWord true 7 none).script = true",
}



records = []
(output / "TOOLCHAIN.txt").write_bytes(subprocess.check_output([str(LEAN), "--version"]))
with tempfile.TemporaryDirectory(prefix="css-language-lean-") as temporary:
    scratch = Path(temporary)
    (output / "SCRATCH.json").write_text(json.dumps({"path": str(scratch)}) + "\n")
    env = dict(os.environ, LEAN_PATH=str(scratch))
    shutil.copyfile(HERE / "Language.lean", scratch / "Language.lean")
    (scratch / "Audit.lean").write_text("import Language\n" + "".join(
        "#print axioms LanguageContext." + name + "\n" for name in names))
    for name, claim in false_cases.items():
        (scratch / (name + ".lean")).write_text(
            "import Language\nopen LanguageContext\nexample : " + claim + " := by decide\n")
    for source in scratch.rglob("*.lean"):
        target = output / source.relative_to(scratch)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for name, expected in [(name, True) for name in ["Language", "Audit"]] + [(n, False) for n in false_cases]:
        result = subprocess.run([str(LEAN), "-o", name + ".olean", name + ".lean"],
                                cwd=scratch, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=60)
        log = output / (name + ".log")
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_bytes(result.stdout)
        records.append({"module": name, "command": [str(LEAN), "-o", name + ".olean", name + ".lean"], "exit": result.returncode, "expected_success": expected})
        (output / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
        assert (result.returncode == 0) == expected, name
        if not expected:
            assert b"Tactic `decide` proved that the proposition" in result.stdout
            assert b"is false" in result.stdout
    audit = (output / "Audit.log").read_text()
    assert audit.count("depends on axioms:") + audit.count("does not depend on any axioms") == len(names)
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
    axioms = {n.strip() for group in re.findall(r"axioms: \[(.*?)\]", audit)
              for n in group.split(",") if n.strip()}
    assert axioms <= {"propext", "Quot.sound", "Classical.choice"}
assert not scratch.exists()
(output / "CHECK.json").write_text(json.dumps({
    "success": True, "audited_theorems": names, "false_controls_rejected": len(false_cases),
    "source_sha256": sha(HERE / "Language.lean"), "lean_sha256": sha(LEAN),
    "scratch_removed": True, "canonical_coverage_increment": 0,
    "native_refinement_proved": False,
    "pointer_or_scanner_refinement_proved": False,
}, indent=2, sort_keys=True) + "\n")
print(f"{len(names)} theorems audited; {len(false_cases)} false controls rejected")
