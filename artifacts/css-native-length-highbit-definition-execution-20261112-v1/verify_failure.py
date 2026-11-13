from pathlib import Path
import hashlib, json

base = Path(__file__).resolve().parent
repo = base.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(base / "PREPARATION-FILES.json") == "10d32cc15ae205c0de7f3f05e30fa7c30639124949ed70e4f4d578965e4a75ac"
for name, digest in json.loads((base / "PREPARATION-FILES.json").read_text()).items():
    assert sha(base / name) == digest
attempt = base / "definition-attempts/1794500883805717000"
inputs = json.loads((attempt / "INPUTS.json").read_text())
preparation = json.loads((base / "PREPARATION.json").read_text())
assert inputs["preparation_sha256"] == sha(base / "PREPARATION.json")
assert inputs["source"] == preparation["files"]
for name, digest in inputs["source"].items():
    assert sha(attempt / name) == sha(base / name) == digest
records = json.loads((attempt / "COMMANDS.json").read_text())
assert len(records) == 1
record = records[0]
lean = repo / preparation["lean"]["path"]
assert record["argv"] == [str(lean), "-j1", "-M2048", "--root=" + str(attempt), "-o", str(attempt / "lib/Target.olean"), str(attempt / "Target.lean")]
assert record["module"] == "Target" and record["exit"] == 1
assert record["group_absent"] is True and record["termination_reason"] is None
assert record["inspection_errors"] == record["cleanup_signals"] == []
assert record["seconds"] < 60 and record["peak_rss_bytes"] <= 2147483648
assert record["executable_sha256"] == sha(lean) == inputs["lean_sha256"]
assert sha(attempt / "target.log") == record["log_sha256"] == "594339a0cb6b4517be0afcfbc7943bb03fc99ab2d3686c0a95a51a782a01f10e"
assert "unexpected token '!'" in (attempt / "target.log").read_text()
assert not any((attempt / name).exists() for name in ["controls.log", "types.log", "audit.log", "lib"])
pid = json.loads((attempt / "target-PID.json").read_text())
assert pid == dict(pid=9513, pgid=9513)
assert json.loads((attempt / "FRESH-ABSENCE.json").read_text()) == [dict(pid_file="target-PID.json", pgid=9513, members=[])]
result = json.loads((attempt / "RESULT.json").read_text())
assert result["exit"] == 1 and result["definition_only"] is True
assert result["proofs_checked"] == result["native_cells_checked"] == result["removed_owned_compiler_bytes"] == 0
print(json.dumps(dict(definition_only=True, commands_run=1, failure="Unavailable ∃! notation under frozen Std-only import", source_unchanged=True, fresh_group_absence=True, types_printed=False, audits_run=0, proofs=0, native_cells_checked=0), indent=2))
