import hashlib
import json
import os
from pathlib import Path
import runpy
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
proposal = read(HERE / "PROPOSAL.json")
assert proposal["scope_runtime_numbers"] == [3, 4] and proposal["runtime5_excluded"]
assert sha(HERE / "TARGET-INVENTORY.json") == proposal["target_inventory_sha256"]
assert sha(HERE / "PRESERVED-RECEIPTS.json") == proposal["preserved_receipts_sha256"]
for name, pin in read(HERE / "REFERENCES.json").items():
    assert sha(ROOT / name) == pin, name
for name, pin in read(HERE / "PRESERVED-RECEIPTS.json").items():
    assert sha(ROOT / name) == pin, name
for records in proposal["records"].values():
    for entry in records.values():
        assert sha(ROOT / entry["path"]) == entry["sha256"]
    result = read(ROOT / records["RESULT.json"]["path"])
    terminal = read(ROOT / records["ROOT-REPORTED-TERMINAL.json"]["path"])
    assert terminal["root_observed_terminal"] and terminal["exit"] == 1
    assert terminal["result_sha256"] == records["RESULT.json"]["sha256"]
    assert result["candidate_skipped"] and result["owned_processes_absent"]
    assert result["failure"] is None and result["preservation_error"] is None
    baseline = result["phases"]["baseline"]
    assert baseline["exit"] == 101 and baseline["owned_group_absent"]
    assert baseline["cleanup_error"] is None and baseline["stop_reason"] is None
for process in proposal["processes"]:
    assert sha(ROOT / process["process_receipt"]) == process["sha256"]
    assert read(ROOT / process["process_receipt"])["pgid"] == process["pgid"]
    try:
        os.killpg(process["pgid"], 0)
    except ProcessLookupError:
        pass
    else:
        raise AssertionError(("Process group exists", process["pgid"]))
for number, inventory in read(HERE / "TARGET-INVENTORY.json").items():
    assert number in ("3", "4")
    target = ROOT / inventory["target"]
    assert target == ROOT / ("artifacts/css-contextual-easing-servo-compile-runtime-" + number + "/target")
    info = target.lstat()
    assert stat.S_ISDIR(info.st_mode) and target.resolve() == target
    assert [info.st_dev, info.st_ino] == inventory["identity"]
    assert stat.S_IMODE(info.st_mode) == inventory["mode"] and info.st_mtime_ns == inventory["mtime_ns"]
    actual = {}
    for directory, dirs, names in os.walk(target, followlinks=False):
        for name in dirs + names:
            path = Path(directory) / name
            info = path.lstat()
            assert stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)
            row = {"identity": [info.st_dev, info.st_ino], "mode": stat.S_IMODE(info.st_mode),
                   "size": info.st_size, "mtime_ns": info.st_mtime_ns,
                   "kind": "file" if stat.S_ISREG(info.st_mode) else "directory"}
            if row["kind"] == "file":
                assert info.st_nlink == 1
                row.update(sha256=sha(path), allocated_bytes=info.st_blocks * 512)
            actual[path.relative_to(target).as_posix()] = row
    assert actual == inventory["entries"]
runpy.run_path(str(ROOT / "artifacts/css-contextual-easing-servo-target-cleanup-v1/audit_retained.py"))
print("Runtime3/4 exact target inventories and eight absent groups verified; retained runtime2 audit replay passed; runtime5 excluded; no deletion")
