from pathlib import Path
import argparse, hashlib, importlib.util, json

base = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("preflight", base / "preflight.py")
preflight_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight_module)
preflight = preflight_module.preflight
repo = base.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument("attempt")
args = parser.parse_args()
assert args.attempt.isdigit()
attempt = base / "definition-attempts" / args.attempt
preflight()
preparation = json.loads((base / "PREPARATION.json").read_text())
inputs = json.loads((attempt / "INPUTS.json").read_text())
assert inputs["preparation_sha256"] == sha(base / "PREPARATION.json")
assert inputs["source"] == preparation["files"]
assert inputs["limits"] == preparation["limits"]
for name, digest in inputs["source"].items():
    assert sha(base / name) == sha(attempt / name) == digest
lean = repo / preparation["lean"]["path"]
assert inputs["lean_sha256"] == sha(lean) == preparation["lean"]["sha256"]
assert inputs["environment"] == dict(LEAN_PATH=str(attempt / "lib"), PYTHONDONTWRITEBYTECODE="1")
records = json.loads((attempt / "COMMANDS.json").read_text())
assert [record["module"] for record in records] == ["Target", "Controls", "Types", "Audit"]
for index, record in enumerate(records):
    module = record["module"]
    wanted = [str(lean), "-j1", "-M2048", "--root=" + str(attempt)]
    if index < 2:
        wanted += ["-o", str(attempt / "lib" / (module + ".olean"))]
    wanted += [str(attempt / (module + ".lean"))]
    assert record["argv"] == wanted
    assert record["executable_sha256"] == sha(lean)
    assert record["exit"] == 0 and record["group_absent"] is True
    assert record["termination_reason"] is None
    assert record["cleanup_signals"] == record["inspection_errors"] == []
    assert record["seconds"] < 60 and record["peak_rss_bytes"] <= 2147483648
    assert sha(attempt / (module.lower() + ".log")) == record["log_sha256"]
    pid = json.loads((attempt / (module.lower() + "-PID.json")).read_text())
    assert type(pid["pid"]) is int and pid["pid"] == pid["pgid"] and pid["pid"] > 1
for name in ["target.log", "controls.log"]:
    assert (attempt / name).read_bytes() == b""
expected = json.loads((base / "AUDIT-EXPECTED.json").read_text())
wanted = "".join("'" + name + "' does not depend on any axioms\n" for name in expected)
assert (attempt / "audit.log").read_text() == wanted
refusals = {
    "extra-line": wanted + "unexpected\n",
    "duplicate": wanted + wanted.splitlines()[0] + "\n",
    "missing": "\n".join(wanted.splitlines()[1:]) + "\n",
    "reordered": "\n".join(reversed(wanted.splitlines())) + "\n",
    "nonstandard": wanted.replace("does not depend on any axioms", "depends on axioms: [sorryAx]", 1),
    "blank-line": wanted + "\n",
    "missing-final-newline": wanted[:-1],
}
for name, mutated in refusals.items():
    assert mutated != wanted, name
names = json.loads((base / "DECLARATIONS.json").read_text())
types = (attempt / "types.log").read_text()
for family, fields in [("Obligations", names["obligations"]), ("Controls", names["controls"])]:
    for field in fields:
        assert "CssNativeHighBit." + family + "." + field in types
result = json.loads((attempt / "RESULT.json").read_text())
assert result["exit"] == 0 and result["definition_only"] is True
assert result["proofs_checked"] == result["native_cells_checked"] == 0
assert result["fields_elaborated"] == 15 and result["controls_elaborated"] == 6
assert result["declaration_audits"] == 50 and result["source_unchanged"] is True
assert result["types_need_independent_review"] is True
assert result["types_sha256"] == sha(attempt / "types.log")
assert not (attempt / "lib").exists()
print(json.dumps(dict(definition_only=True, commands=4, obligation_fields=15,
                     control_fields=6, exact_empty_axiom_audits=50,
                     transcript_refusals=list(refusals),
                     types_sha256=sha(attempt / "types.log"),
                     parsed_types_need_root_review=True,
                     mathematical_proofs=0, native_cells_checked=0), indent=2))
