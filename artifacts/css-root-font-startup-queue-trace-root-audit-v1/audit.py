import copy
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OWNER = ROOT / "artifacts/css-root-font-startup-queue-trace-candidate-browser-v1"
RUNTIME = ROOT / "artifacts/css-root-font-startup-queue-trace-candidate-browser-runtime-v1"
CANONICAL = ROOT / "artifacts/css-registered-number-native-runtime-v1"
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def raw_summary(events, expected):
    rows = [row for row in events if row.get('action') == 'test_status']
    starts = [(i, row) for i, row in enumerate(events) if row.get('action') == 'test_start']
    ends = [(i, row) for i, row in enumerate(events) if row.get('action') == 'test_end']
    suite_starts = [i for i, row in enumerate(events) if row.get('action') == 'suite_start']
    suite_ends = [i for i, row in enumerate(events) if row.get('action') == 'suite_end']
    names = [(row.get('test'), row.get('subtest')) for row in rows]
    wanted = [(page, name) for page, names in expected.items() for name in names]
    exact = Counter(names) == Counter(wanted)
    complete_end = (len(starts) == len(ends) == len(expected)
                    and Counter(row.get('test') for _, row in starts) == Counter(expected.keys())
                    and Counter(row.get('test') for _, row in ends) == Counter(expected.keys())
                    and all(row.get('status') == 'OK' for _, row in ends))
    ordered = complete_end and len(suite_starts) == len(suite_ends) == 1
    if ordered:
        for page in expected:
            start = next(i for i, row in starts if row['test'] == page)
            end = next(i for i, row in ends if row['test'] == page)
            ordered = ordered and suite_starts[0] < start < end < suite_ends[0]
            ordered = ordered and all(start < i < end for i, row in enumerate(events)
                                      if row.get('action') == 'test_status' and row.get('test') == page)
    crashes = [row for row in events if row.get('action') == 'crash' or row.get('status') == 'CRASH']
    valid = exact and ordered and not crashes and all(row.get('status') in ('PASS','FAIL') for row in rows)
    return {'callbacks': len(rows), 'statuses': dict(Counter(row.get('status') for row in rows)), 'expected_names_exact': exact, 'expected_start_and_OK_ending': complete_end, 'ordered_suite': bool(ordered), 'crash_events': len(crashes), 'complete_raw_roster': bool(valid), 'all_callbacks_pass': bool(valid and all(row.get('status') == 'PASS' for row in rows))}


binding = read(HERE / 'BINDINGS.json')
assert binding['execution_enabled'] is True and not binding['pending_owner_terminal']
assert type(binding['outer_group']) is int and binding['outer_group'] > 1
for path, pin in binding['references'].items():
    assert sha(ROOT / path) == pin
assert binding['result_sha256'] == sha(RUNTIME / 'RESULT.json')
assert binding['terminal_sha256'] == sha(RUNTIME / 'ROOT-OWNER-TERMINAL.json')


assert isinstance(binding["owner_manifest_sha256"], str) and len(binding["owner_manifest_sha256"]) == 64
assert sha(OWNER / "FILES.json") == binding["owner_manifest_sha256"]
terminal = read(RUNTIME / "ROOT-OWNER-TERMINAL.json")
result = read(RUNTIME / "RESULT.json")
assert terminal["terminal"] and terminal["exit"] == (0 if result["success"] else 1)
assert terminal["result_sha256"] == sha(RUNTIME / "RESULT.json")
assert terminal['active_manifest'] == binding['owner_manifest_sha256']
assert terminal['launch'] == binding['launch'] and terminal['session'] == binding['session']
assert terminal['terminal_chunk'] == binding['terminal_chunk']
assert terminal['outer_group'] == binding['outer_group']
assert result["restoration_verified"] and result["runtime_controls_unchanged"]
assert result["empty_staging_preserved"] and not result["native_fix_acceptance"]
assert not (CANONICAL / "SOURCE-TRANSITION.lock").exists() and not (CANONICAL / "SOURCE-TRANSITION.lock").is_symlink()
baseline = load("pair_audit_baseline", OWNER / "baseline.py")
policy, ownership, roles = baseline.prepare(sha(OWNER / "FILES.json"))
env = baseline.environment()
capture = baseline.current_capture(policy)
assert set(roles) == {'dom/animation/EffectCompositor.cpp', 'dom/animation/KeyframeEffect.cpp', 'layout/style/GeckoBindings.cpp', 'layout/style/ServoStyleSet.cpp', 'servo/components/style/data.rs', 'servo/components/style/gecko/traversal.rs', 'servo/components/style/matching.rs', 'servo/components/style/traversal.rs', 'servo/components/style/values/specified/length.rs', 'servo/ports/geckolib/glue.rs'}
assert policy['lane_order'] == ['cancellation']
assert sum(policy['wpt_lanes'][lane]['expected_subtest_count'] for lane in policy['lane_order']) == 8
assert sum(policy['wpt_lanes'][lane]['expected_page_count'] for lane in policy['lane_order']) == 1
raw_observation, assessment_replayed = {}, {}
for lane in policy['lane_order']:
    phase = RUNTIME / ('candidate-wpt-' + lane)
    raw_observation[lane] = None
    assessment_replayed[lane] = False
    if (phase / 'raw.jsonl').is_file():
        events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
        raw_observation[lane] = raw_summary(events, policy['wpt_lanes'][lane]['expected_subtests'])
        raw_observation[lane]['raw_sha256'] = sha(phase / 'raw.jsonl')
        if (phase / 'ASSESSMENT.json').is_file():
            assessor = load('audit_wpt_assessor', OWNER / 'assess.py')
            checks = load('audit_wpt_checks', ROOT / policy['wpt']['checks_helper'])
            assessment = assessor.assess(events, read(phase / 'RESULT.json')['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks, run_binding=read(phase / 'APPLICATION-METADATA.json'))
            assert assessment == read(phase / 'ASSESSMENT.json')
            assessment_replayed[lane] = True
    if result['success']:
        assert raw_observation[lane] and raw_observation[lane]['complete_raw_roster'] and assessment_replayed[lane]
processes = []
for path in sorted(RUNTIME.rglob("*PROCESS.json")):
    record = read(path)
    group = record["pgid"]
    ownership.group_absent(group)
    processes.append({"path": str(path.relative_to(RUNTIME)), "pgid": group})
ownership.group_absent(binding['outer_group'])
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
receipt_binding = capture['checkpoint_receipt']
assert sha(ROOT / receipt_binding['path']) == receipt_binding['sha256']
native_receipt = read(ROOT / receipt_binding['path'])
assert native_receipt == capture['checkpoint']
adapter = baseline.load('audit_native_authority', policy['capture_owner']['directory'] + '/baseline.py')
assert receipt_binding['path'] == adapter.binding['native_receipt']
native_head = native_receipt['commit']
assert native_head == policy['head'] == index['head'] == epoch['semantic_index']['head']
assert sha(CANONICAL / 'CURRENT-EPOCH.json') == capture['controls']['CURRENT-EPOCH.json']
baseline.require_role(policy, read(CANONICAL / 'ROLE.json'), epoch)
assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['image_commit'], native_head)
assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['nowrap_commit'], native_head)
assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['language_commit'], native_head)
state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['nowrap_commit'])
state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['language_commit'])
assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['ownership_commit'], native_head)
state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['ownership_commit'])
assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['capacity_commit'], native_head)
state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['capacity_commit'])
state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', adapter.binding['native_parent'])
assert state.h.git(ROOT, env, 'rev-parse', native_head + '^').decode().strip() == adapter.binding['native_parent']
assert state.h.git(ROOT, env, 'diff-tree', '--no-commit-id', '--name-only', '-r', native_head).decode().splitlines() == native_receipt['files']
state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['head'])
for name, source_role in roles.items():
    assert hashlib.sha256(state.h.git(ROOT, env, 'show', native_head + ':' + name)).hexdigest() == source_role['base_sha256']
for name, pin in policy['source_context_pins'].items():
    assert sha(ROOT / name) == pin
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
    assert not (RUNTIME / "backups").exists() and not (RUNTIME / "backups").is_symlink()
else:
    assert bundle.scan(RUNTIME / "backups") == backups["owned_inventory"]
report = {"independent_live_restoration_verified": True, "snapshot": observed,
          "application_and_extras_semantically_restored": True,
          "source_and_binary_hashes_restored": True, "flags_restored": True,
          "controls_unchanged": True, "backup_removed": cleanup["removed"],
          "retained_backup_inventory_verified": not cleanup["removed"],
          "backup_inventory_sha256": sha(RUNTIME / "BACKUPS.json"),
          "independently_absent_process_groups": [p["pgid"] for p in processes] + [binding['outer_group']],
          "process_records": processes, "removed_wpt_temporary_roots": wpt_temporary_roots,
          "restored_application_metadata": application,
          "owner_result_sha256": sha(RUNTIME / "RESULT.json"),
          "audit_script_sha256": sha(Path(__file__)), "owner_terminal": terminal,
          "restored_source_claims": {name: claims[name] for name in roles},
          "raw_wpt_observation": raw_observation, "saved_assessment_replayed": assessment_replayed,
          "owner_success_scope": "complete observation and restoration; callback PASS and baseline comparison are separate",
          "native_acceptance": False, "native_authority_freshly_verified": True}
archive_audit = load('archive_handoff_audit', HERE / 'archive_audit.py')
report['archive_observation'] = archive_audit.verify_archive(ROOT, RUNTIME, policy, roles, claims, result, binding)
with (RUNTIME / "ROOT-LIVE-RESTORATION.json").open("x") as stream:
    json.dump(report, stream, indent=2)
    stream.write("\n")
print("Independent live source, application, index, controls, flags and process restoration verified")
