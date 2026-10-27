import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "artifacts/css-variables-computed-name-model-v1"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
out = parser.parse_args().output.resolve()
assert not out.exists() and not out.is_symlink()
plan = json.loads((HERE / "PLAN.json").read_text())
for path, pin in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert sha(ROOT / path) == pin, path
for name, pin in json.loads((SOURCE / "FILES.json").read_text()).items():
    assert sha(SOURCE / name) == pin, name
for name, pins in plan["changes"].items():
    assert sha(HERE / "candidate" / name) == pins["after"], name
    original = HERE / "original" / name
    assert (sha(original) if original.exists() else None) == pins["before"], name
old = ast.parse((HERE / "original/check.py").read_text())
new = ast.parse((HERE / "candidate/check.py").read_text())
def case_node(tree):
    return next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "EXECUTABLE_CASES" for t in n.targets))
old_cases = ast.literal_eval(case_node(old).value)
assert ast.literal_eval(case_node(new).value) == old_cases + [tuple(r) for r in plan["cases"]]
case_node(new).value = case_node(old).value
assert ast.dump(new) == ast.dump(old)
for name in ["CssSemantics.lean", "tests/Audit.lean", "tests/RunExamples.lean", "README.md", "ARTIFACT.md", "research/coverage-map.md"]:
    assert (HERE / "candidate" / name).read_bytes().startswith((HERE / "original" / name).read_bytes())
old_cov = json.loads((HERE / "original/coverage.json").read_text())
new_cov = json.loads((HERE / "candidate/coverage.json").read_text())
original_text = (HERE / "original/coverage.json").read_text()
reconstructed = original_text
for edit in sorted(json.loads((HERE / "COVERAGE-INSERTIONS.json").read_text()), key=lambda e: e["position"], reverse=True):
    reconstructed = reconstructed[:edit["position"]] + edit["text"] + reconstructed[edit["position"]:]
assert reconstructed == (HERE / "candidate/coverage.json").read_text()
assert new_cov["features"][:-1] == old_cov["features"]
assert new_cov["specifications"][:-2] == old_cov["specifications"]
for k in old_cov.keys() - {"features", "specifications"}:
    assert old_cov[k] == new_cov[k]
ns = plan["target_namespace"]
transfer = (SOURCE / "Names.lean").read_text().replace("namespace ComputedNames", "namespace " + ns).replace("end ComputedNames", "end " + ns)
assert transfer == (HERE / "candidate/CssSemantics/GuardedNames.lean").read_text()
transfer = (SOURCE / "Examples.lean").read_text().replace("import Names", "import CssSemantics.GuardedNames").replace("namespace ComputedNames.Examples", "namespace " + ns + ".Examples").replace("end ComputedNames.Examples", "end " + ns + ".Examples")
examples = (HERE / "candidate/CssSemantics/GuardedNamesExamples.lean").read_text()
start = examples.index("\ndef checks :")
end = examples.index("end " + ns + ".Examples", start)
assert examples[:start] + examples[end:] == transfer
for claim in plan["claims"]:
    assert "decide (" + claim + ")" in examples
declarations = []
for name in ["GuardedNames.lean", "GuardedNamesExamples.lean"]:
    source = (HERE / "candidate/CssSemantics" / name).read_text()
    namespace = re.search(r"^namespace (.+)$", source, re.M)[1]
    declarations += [namespace + "." + t for t in re.findall(r"^theorem (\S+)", source, re.M)]
assert set(declarations) == {a.removeprefix("#print axioms ") for a in plan["audits"]}
assert len(declarations) == len(set(declarations)) == 25
old_audits = re.findall(r"#print axioms (\S+)", (HERE / "original/tests/Audit.lean").read_text())
assert not set(declarations).intersection(old_audits)
report = json.loads((HERE / "previous-report.json").read_text())
assert sha(HERE / "previous-report.json") == plan["base_report_sha256"]
assert len(old_audits) == len(report["declaration_axioms"]) == plan["existing"]["audits"]
assert old_cases == [(r["name"], r["result"]) for r in report["executable_cases"]]
for key in plan["existing"]:
    assert plan["existing"][key] + plan["delta"][key] == plan["intended"][key]
out.mkdir()
commands = []
with tempfile.TemporaryDirectory(prefix="computed-name-transport-", dir="/private/tmp") as temp:
    scratch = Path(temp)
    shutil.copytree(HERE / "original", scratch, dirs_exist_ok=True)
    for flags in [["--check"], [], ["--reverse", "--check"], ["--reverse"]]:
        command = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "apply", *flags, str(HERE / "library.patch")]
        run = subprocess.run(command, cwd=scratch, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"), text=True, capture_output=True)
        commands.append({"argv": command, "exit": run.returncode, "stdout": run.stdout, "stderr": run.stderr})
        assert run.returncode == 0, commands[-1]
        if not flags:
            for name, pins in plan["changes"].items():
                assert sha(scratch / name) == pins["after"]
    for name, pins in plan["changes"].items():
        assert (sha(scratch / name) if (scratch / name).exists() else None) == pins["before"]
assert not scratch.exists()
result = {"status": "COMPUTED_NAME_LIBRARY_PROPOSAL_STATIC_PASS", "paths": 10,
          "proof_transfer_statements": 25, "old_audit_and_case_prefixes_preserved": True,
          "checker_ast_case_append_only": True, "old_coverage_entries_preserved": True,
          "scratch_transport_reversed": True, "scratch_removed": True,
          "canonical_applied": False, "canonical_execution": False,
          "compiler_execution": False, "commands": commands, "intended": plan["intended"]}
(out / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
