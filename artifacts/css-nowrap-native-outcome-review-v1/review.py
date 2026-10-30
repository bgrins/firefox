import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OWNER = ROOT / 'artifacts/css-nowrap-native-pair-v1'
RUNTIME = ROOT / 'artifacts/css-nowrap-native-pair-runtime-1'
refs = {}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def read(path):
    refs[str(path.relative_to(ROOT))] = sha(path)
    return json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    refs[str(path.relative_to(ROOT))] = sha(path)
    return module


runtime_manifest = read(RUNTIME / 'FILES.json')
for name, record in runtime_manifest.items():
    assert sha(RUNTIME / name) == record['sha256']
    refs[str((RUNTIME / name).relative_to(ROOT))] = record['sha256']
terminal = read(RUNTIME / 'ROOT-OWNER-TERMINAL.json')
result = read(RUNTIME / 'RESULT.json')
assert terminal['exit'] == 0 and terminal['result_sha256'] == sha(RUNTIME / 'RESULT.json')
assert result['success'] and result['restoration_verified'] and result['error'] is None
assert terminal['session'] == 6129 and terminal['launch'] == 'a1b368' and terminal['terminal'] == 'd6a86a'
assert result['runtime_controls_unchanged'] and result['empty_staging_preserved'] and result['publication_errors'] == []
assert result['native_fix_acceptance'] is False
live = read(RUNTIME / 'ROOT-LIVE-RESTORATION.json')
live_terminal = read(RUNTIME / 'ROOT-LIVE-AUDIT-TERMINAL.json')
assert live_terminal == {'session': 37858, 'launch': 'e162d0', 'terminal': '56b2d4', 'exit': 0, 'audit_sha256': sha(RUNTIME / 'ROOT-LIVE-RESTORATION.json')}
script = ROOT / 'artifacts/css-nowrap-native-live-audit-v1.py'
assert sha(script) == live['audit_script_sha256']
refs[str(script.relative_to(ROOT))] = sha(script)
assert live['owner_result_sha256'] == sha(RUNTIME / 'RESULT.json')
for field in ['independent_live_restoration_verified', 'application_and_extras_semantically_restored', 'source_and_binary_hashes_restored', 'flags_restored', 'controls_unchanged', 'backup_removed']:
    assert live[field] is True
assert live['snapshot'] == read(RUNTIME / 'POST.json')
assert live['native_acceptance'] is False
assert len(set(live['independently_absent_process_groups'])) == 8
restoration = read(RUNTIME / 'RESTORATION.json')
assert restoration['errors'] == [] and restoration['owned_processes'] == {}
cleanup = read(RUNTIME / 'BACKUP-CLEANUP.json')
assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
policy = read(OWNER / 'POLICY.json')
for name, record in read(OWNER / 'FILES.json').items():
    assert sha(OWNER / name) == record['sha256']
    refs[str((OWNER / name).relative_to(ROOT))] = record['sha256']
assert policy['runtime_output'] == str(RUNTIME.relative_to(ROOT))
assert policy['head'] == '10e043823f5fb60317be96ada71e8fd39794e100'
roles = read(OWNER / 'SOURCE-ROLES.json')
assert set(roles) == {'dom/base/nsLineBreaker.cpp'}
comparison = load('nowrap_comparison', OWNER / 'comparison.py')
assessor = load('nowrap_assessor', OWNER / 'assess.py')
checks = load('nowrap_checks', ROOT / policy['wpt']['checks_helper'])
builds = {role: comparison.build_binding(ROOT, OWNER, RUNTIME, policy, role)
          for role in ['original', 'candidate']}
groups = set()
for role in builds:
    groups.add(read(RUNTIME / (role + '-build') / 'build-PROCESS.json')['pgid'])
    groups.add(read(RUNTIME / (role + '-build') / 'WAKE-PROCESS.json')['pgid'])
    for name in ['RESULT.json', 'build-RESULT.json', 'COMMAND.json']:
        read(RUNTIME / (role + '-build') / name)
lanes = {}
port_comparison = load('nowrap_ports', HERE / 'ports.py')
derived_regression = None
for lane in policy['lane_order']:
    settings = policy['wpt_lanes'][lane]
    original = comparison.replay_original(ROOT, OWNER, RUNTIME, policy, lane, assessor, checks)
    observations = {}
    for role in builds:
        phase = RUNTIME / (role + '-wpt-' + lane)
        saved = read(phase / 'RESULT.json')
        assert saved['success'] and saved['preservation_verified'] and saved['execution_error'] is None
        assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json') == builds[role]['application_metadata']
        assert read(phase / 'BINARY-PINS.json') == builds[role]['binaries']
        assert read(phase / 'PRE.json') == read(phase / 'POST.json') == builds[role]['snapshot']
        groups.add(read(phase / 'PROCESS.json')['pgid'])
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        for name, pin in read(phase / 'STAGED-RESOURCES.json').items():
            assert sha(phase / name) == pin
            refs[str((phase / name).relative_to(ROOT))] = pin
        for url, rec in settings['resources'].items():
            assert sha(phase / 'tests' / url[1:]) == rec['sha256']
        for kind, folder in [('portable', 'metadata'), ('mozilla', 'mozilla-metadata')]:
            assert sha(phase / folder / 'MANIFEST.json') == settings['manifests'][kind]['sha256']
            for name, rec in settings['metadata'][kind].items():
                path = phase / folder / name
                assert (not path.exists()) if rec['sha256'] is None else sha(path) == rec['sha256']
        bound = comparison.phase_policy(settings, builds if role == 'candidate' else {'original': builds['original']}, policy['head'])
        assert read(phase / 'ASSESSMENT-POLICY.json') == bound
        raw = phase / 'raw.jsonl'
        refs[str(raw.relative_to(ROOT))] = sha(raw)
        events = [json.loads(line) for line in raw.read_text().splitlines()]
        replay = assessor.assess(events, saved['exit'], bound, checks,
                                 original=original if role == 'candidate' else None,
                                 run_binding=builds[role]['application_metadata'])
        assert replay == read(phase / 'ASSESSMENT.json') and replay['complete']
        observations[role] = replay
    behavior = comparison.behavior(original, observations['candidate'], assessor.signature)
    assert behavior == read(RUNTIME / ('candidate-wpt-' + lane) / 'BEHAVIOR-COMPARISON.json')
    if lane == 'regression':
        assert behavior['errors'] == ['regression identities/status/expectations/intermittents changed'] + [
            'original PASS or ending full signature changed: ' + str((test, 'test_end', '')) for test in sorted(port_comparison.KNOWN)]
    if lane == 'regression':
        derived_regression = port_comparison.compare(RUNTIME, policy, original, observations['candidate'], assessor.signature)
        refs.update({str(Path(path).relative_to(ROOT)): pin for path, pin in derived_regression['pins'].items()})
    lanes[lane] = {
        'original': observations['original']['per_test'],
        'candidate': observations['candidate']['per_test'],
        'original_callback_counts': {s: sum(r['status'] == s for r in original['rows']) for s in ['PASS', 'FAIL']},
        'candidate_callback_counts': {s: sum(r['status'] == s for r in observations['candidate']['rows']) for s in ['PASS', 'FAIL']},
        'signature_count': len(behavior['original_signatures']),
        'comparison_gate': behavior['publication_observation_gate'],
        'all_signatures_equal': behavior['all_signatures_equal'],
        'differences': behavior['differences'],
        'original_PASS_signatures_preserved': all(
            assessor.signature(row) in behavior['candidate_signatures']
            for row in original['rows'] if row['status'] == 'PASS'),
    }
assert groups == set(live['independently_absent_process_groups'])
saved_comparison = read(RUNTIME / 'COMPARISON.json')
assert saved_comparison['publication_observation_gate'] == all(v['comparison_gate'] for v in lanes.values())
output = {'owner_terminal': terminal, 'owner_result': result,
          'builds': {role: {k: build[k] for k in ['native_sources', 'application_metadata', 'binaries']} for role, build in builds.items()},
          'lanes': lanes, 'observation_complete': True,
          'comparison_gate': saved_comparison['publication_observation_gate'],
          'derived_regression_comparison': derived_regression,
          'derived_publication_observation_gate': lanes['target']['comparison_gate'] and derived_regression['derived_regression_gate'],
          'independent_live_restoration_check': False,
          'separate_root_live_authority': {'terminal': live_terminal, 'report': live}, 'native_publication_performed': False}
(HERE / 'OBSERVATIONS.json').write_text(json.dumps(output, indent=2) + '\n')
(HERE / 'REFERENCES.json').write_text(json.dumps(refs, indent=2, sort_keys=True) + '\n')
print(json.dumps({'complete': True, 'lanes': {n: {k:v for k,v in x.items() if k not in ['original','candidate','differences']} for n,x in lanes.items()}, 'comparison_gate': output['comparison_gate'], 'references': len(refs)}))
