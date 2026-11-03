import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OWNER = ROOT / "artifacts/css-resumable-font-selection-integrated-pair-v1"
RUNTIME = ROOT / "artifacts/css-resumable-font-selection-integrated-pair-runtime-1"
CANONICAL = ROOT / "artifacts/css-registered-number-native-runtime-v1"
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert sha(OWNER / "FILES.json") == "f99a4fb85bdf9e456948ceab63dcea391d84d4d23d07e70851c3ee811b88eb2c"
terminal = read(RUNTIME / "ROOT-OWNER-TERMINAL.json")
result = read(RUNTIME / "RESULT.json")
assert terminal["terminal"] and terminal["exit"] == (0 if result["success"] else 1)
assert terminal["result_sha256"] == sha(RUNTIME / "RESULT.json")
assert result["restoration_verified"] and result["runtime_controls_unchanged"]
assert result["empty_staging_preserved"] and not result["native_fix_acceptance"]
assert not (CANONICAL / "SOURCE-TRANSITION.lock").exists() and not (CANONICAL / "SOURCE-TRANSITION.lock").is_symlink()
baseline = load("pair_audit_baseline", OWNER / "baseline.py")
policy, ownership, roles = baseline.prepare(sha(OWNER / "FILES.json"))
env = baseline.environment()
capture = baseline.current_capture(policy)
processes = []
for path in sorted(RUNTIME.rglob("*PROCESS.json")):
    record = read(path)
    group = record["pgid"]
    ownership.group_absent(group)
    processes.append({"path": str(path.relative_to(RUNTIME)), "pgid": group})
ownership.group_absent(62896)
wpt_temporary_roots = []
for phase in sorted(RUNTIME.glob("*-wpt-*")):
    command = read(phase / "COMMAND.json")
    cleanup = read(phase / "CLEANUP.json")
    temporary = Path(command["temporary_root"])
    assert temporary.parent == Path("/private/tmp")
    assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
    assert not temporary.exists() and not temporary.is_symlink()
    wpt_temporary_roots.append(str(temporary))
for name, pin in policy["controls"].items():
    assert sha(CANONICAL / name) == pin
baseline.metadata_guard(policy)
for name in policy["preserved_absent_metadata"] + policy["preserved_absent_resources"]:
    assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
state = load("pair_audit_state", ROOT / policy["state_helper"])
epoch = read(CANONICAL / "CURRENT-EPOCH.json")
index = state.h.index_state(ROOT, env)
assert state.h.semantic_index(index) == epoch["semantic_index"]
adjusted = copy.deepcopy(epoch)
adjusted["raw_index_observation"]["current"] = index["raw_index"]
observed = state.a.verify_current(state.h, ROOT, env, adjusted)
expected = copy.deepcopy(capture["snapshot"])
expected["index"]["raw_index"] = index["raw_index"]
assert observed == expected == read(RUNTIME / "POST.json")
for label, path in [("root", ROOT), ("nested", ROOT / "artifacts/css-spec-lean")]:
    assert hashlib.sha256(state.h.git(path, env, "ls-files", "-v", "-z")).hexdigest() == capture["flag_hashes"][label]
claims = capture["payload_claims"] | capture["additional_sources"]
restoration = read(RUNTIME / "RESTORATION.json")
assert not restoration["errors"] and not restoration["owned_processes"]
assert set(restoration["sources"]) == set(roles)
for name, role in roles.items():
    claim = claims[name]
    assert ownership.claim(ROOT, name, role["base_sha256"], claim["identity"]) == claim
    assert restoration["sources"][name] == {"sha256": role["base_sha256"], "identity": claim["identity"]}
bundle = load("pair_audit_bundle", ROOT / policy["bundle_helper"])
assert bundle.semantic(bundle.scan(ROOT / policy["bundle_path"])) == bundle.semantic(read(RUNTIME / "APP-PRE.json"))
extras = {name: bundle.entry(ROOT / name) for name in policy["extra_backup_paths"]}
assert bundle.semantic(extras) == bundle.semantic(read(RUNTIME / "EXTRA-PRE.json"))
assert all(sha(ROOT / name) == pin for name, pin in capture["binaries"].items())
metadata = load("pair_audit_metadata", ROOT / policy["wpt"]["metadata_helper"])
application = metadata.application_metadata(ROOT / policy["wpt"]["application_ini"], policy["restored_application_revision"])
semantic = lambda row: {key: value for key, value in row.items() if key not in ("entry_identity", "identity")}
assert semantic(application) == semantic(capture["application_metadata"])
cleanup = read(RUNTIME / "BACKUP-CLEANUP.json")
backups = read(RUNTIME / "BACKUPS.json")
assert cleanup["verified_original_restoration"]
assert cleanup["owned_backup_bytes"] == backups["bytes"] == read(RUNTIME / "PAIR-PRE.json")["owned_backup_bytes"]
assert cleanup["removed"] is result["success"]
if cleanup["removed"]:
    assert not (RUNTIME / "backups").exists()
else:
    assert bundle.scan(RUNTIME / "backups") == backups["owned_inventory"]
report = {"independent_live_restoration_verified": True, "snapshot": observed,
          "application_and_extras_semantically_restored": True,
          "source_and_binary_hashes_restored": True, "flags_restored": True,
          "controls_unchanged": True, "backup_removed": cleanup["removed"],
          "retained_backup_inventory_verified": not cleanup["removed"],
          "backup_inventory_sha256": sha(RUNTIME / "BACKUPS.json"),
          "independently_absent_process_groups": [p["pgid"] for p in processes] + [62896],
          "process_records": processes, "removed_wpt_temporary_roots": wpt_temporary_roots,
          "restored_application_metadata": application,
          "owner_result_sha256": sha(RUNTIME / "RESULT.json"),
          "audit_script_sha256": sha(Path(__file__)), "owner_terminal": terminal,
          "restored_source_claims": {name: claims[name] for name in roles},
          "native_acceptance": False}
with (RUNTIME / "ROOT-LIVE-RESTORATION.json").open("x") as stream:
    json.dump(report, stream, indent=2)
    stream.write("\n")
print("Independent live source, application, index, controls, flags and process restoration verified")
