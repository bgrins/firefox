from pathlib import Path
import hashlib, json, re

base = Path(__file__).resolve().parent
repo = base.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
basis = json.loads((base / "BASIS.json").read_text())
evidence = repo / basis["evidence"]
assert sha(evidence / "FILES.json") == basis["manifest_sha256"]
frozen = json.loads((evidence / "FILES.json").read_text())
assert len(frozen) == basis["author_files"] == 41
for relative, digest in frozen.items():
    assert sha(evidence / relative) == digest, relative
assert sha(evidence / "PREPARATION-FILES.json") == "791b092caa95e23556cc0a39307707ed4a60f3ecb43c988e527a4971565959e2"
for relative, digest in json.loads((evidence / "PREPARATION-FILES.json").read_text()).items():
    assert sha(evidence / relative) == digest
attempt = evidence / "definition-attempts" / basis["attempt"]
preparation = json.loads((evidence / "PREPARATION.json").read_text())
target = repo / preparation["target"]["path"]
assert sha(target / "FILES.json") == preparation["target"]["manifest_sha256"]
for relative, digest in json.loads((target / "FILES.json").read_text()).items():
    assert sha(target / relative) == digest
for name in ["Target.lean", "Controls.lean", "Types.lean", "DECLARATIONS.json"]:
    assert (target / name).read_bytes() == (evidence / name).read_bytes()
inputs = json.loads((attempt / "INPUTS.json").read_text())
assert inputs["preparation_sha256"] == sha(evidence / "PREPARATION.json")
assert inputs["source"] == preparation["files"]
for name, digest in inputs["source"].items():
    assert sha(attempt / name) == sha(evidence / name) == digest
assert inputs["limits"] == preparation["limits"] == dict(workers=1, seconds=60, rss_bytes=2147483648)
assert inputs["environment"] == dict(LEAN_PATH=str(attempt / "lib"), PYTHONDONTWRITEBYTECODE="1")
lean = repo / preparation["lean"]["path"]
assert sha(lean) == inputs["lean_sha256"] == preparation["lean"]["sha256"]
records = json.loads((attempt / "COMMANDS.json").read_text())
assert [r["module"] for r in records] == ["Target", "Controls", "Types", "Audit"]
absence = []
for index, r in enumerate(records):
    module = r["module"]
    command = [str(lean), "-j1", "-M2048", "--root=" + str(attempt)]
    if index < 2:
        command += ["-o", str(attempt / "lib" / (module + ".olean"))]
    command += [str(attempt / (module + ".lean"))]
    assert r["argv"] == command and r["executable_sha256"] == sha(lean)
    assert r["exit"] == 0 and r["group_absent"] is True and r["termination_reason"] is None
    assert r["inspection_errors"] == r["cleanup_signals"] == []
    assert 0 <= r["seconds"] < 60 and 0 <= r["peak_rss_bytes"] <= 2147483648
    assert sha(attempt / (module.lower() + ".log")) == r["log_sha256"]
    pid_file = module.lower() + "-PID.json"
    pid = json.loads((attempt / pid_file).read_text())
    assert type(pid["pid"]) is int and pid["pid"] == pid["pgid"] and pid["pid"] > 1
    absence.append(dict(pid_file=pid_file, pgid=pid["pgid"], members=[]))
assert len({row["pgid"] for row in absence}) == 4
assert json.loads((attempt / "FRESH-ABSENCE.json").read_text()) == sorted(absence, key=lambda r: r["pid_file"])
assert (attempt / "target.log").read_bytes() == b""
expected_audits = json.loads((base / "AUDIT-EXPECTED.json").read_text())
assert list(expected_audits) == list(json.loads((evidence / "AUDIT-EXPECTED.json").read_text()))
assert len(expected_audits) == 50
for axes in expected_audits.values():
    assert axes in [[], ["propext"], ["propext", "Quot.sound"]]
wanted_audits = "".join("'" + name + "' " + ("depends on axioms: [" + ", ".join(axes) + "]" if axes else "does not depend on any axioms") + "\n" for name, axes in expected_audits.items())
wanted_warnings = (base / "WARNINGS-EXPECTED.txt").read_text()
blocks = []
for row in basis["allowed_warning_bindings"]:
    b = row["binder"]
    blocks.append(str(attempt / "Controls.lean") + ":" + str(row["line"]) + ":" + str(row["column"]) + ": warning: Variable name `" + b + "` is not explicitly referenced.\n\nHint: The binding can be removed (if unused) or named `_` (if used implicitly). Alternatively, prefix the name with `_` to silence this warning:\n  [apply] _" + b + "\n\nNote: This linter can be disabled with `set_option linter.unusedVariables false`\n")
assert len(blocks) == 4 and "".join(blocks) == wanted_warnings

def audit_parse(text):
    assert text == wanted_audits
    parsed = []
    for line in text.splitlines():
        match = re.fullmatch(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]+)\])", line)
        assert match
        parsed.append((match[1], match[2].split(", ") if match[2] else []))
    assert parsed == list(expected_audits.items())

def warning_parse(text):
    assert text == wanted_warnings

audit_parse((attempt / "audit.log").read_text())
warning_parse((attempt / "controls.log").read_text())
assert sha(attempt / "types.log") == basis["types_sha256"]
refusals = []
def refuse(name, parser, mutated):
    try:
        parser(mutated)
    except AssertionError:
        refusals.append(name)
    else:
        raise AssertionError("Control was accepted: " + name)

lines = wanted_audits.splitlines(keepends=True)
for name, altered in {
    "audit-missing": "".join(lines[1:]),
    "audit-extra": wanted_audits + "unexpected\n",
    "audit-duplicate": wanted_audits + lines[0],
    "audit-reordered": "".join(reversed(lines)),
    "audit-forbidden-axiom": wanted_audits.replace("propext", "sorryAx", 1),
    "audit-unobserved-standard-axiom": wanted_audits.replace("propext", "Classical.choice", 1),
    "audit-malformed": wanted_audits.replace("depends on axioms:", "depends axioms:", 1),
    "audit-missing-newline": wanted_audits[:-1],
}.items():
    refuse(name, audit_parse, altered)
for name, altered in {
    "warning-missing": "".join(blocks[1:]),
    "warning-extra": wanted_warnings + "unexpected\n",
    "warning-duplicate": wanted_warnings + blocks[0],
    "warning-reordered": "".join(reversed(blocks)),
    "warning-wrong-binder": wanted_warnings.replace("name `b`", "name `x`", 1),
    "warning-wrong-location": wanted_warnings.replace(":59:7:", ":58:7:", 1),
    "warning-forbidden-kind": wanted_warnings.replace("Variable name `b` is not explicitly referenced.", "declaration uses sorry", 1),
    "warning-missing-newline": wanted_warnings[:-1],
}.items():
    refuse(name, warning_parse, altered)
result = json.loads((attempt / "RESULT.json").read_text())
assert result["exit"] == 1 and result["failure"] == "AssertionError()"
assert result["definition_only"] is True and result["proofs_checked"] == result["native_cells_checked"] == 0
assert result["removed_owned_compiler_bytes"] == 396984 and not (attempt / "lib").exists()
assert wanted_warnings != ""
old_expected = "".join("'" + name + "' does not depend on any axioms\n" for name in expected_audits)
assert old_expected != wanted_audits
print(json.dumps(dict(retained_interpretation=True, original_wrapper_exit=1,
                     executed_wrapper_refusal="controls.log expected empty",
                     audit_expectation_mismatch="Observed; original check not executed",
                     compiler_commands_exit_zero=4, obligation_types=15, control_types=6,
                     exact_warnings=4, exact_ordered_audits=50,
                     audit_axioms={"empty":17, "propext":1, "propext,Quot.sound":32},
                     types_sha256=basis["types_sha256"], fresh_groups_absent=4,
                     parser_refusals=refusals, new_compiler_invocations=0,
                     mathematical_proofs=0, native_cells_checked=0), indent=2))
