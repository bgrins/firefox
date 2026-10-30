import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-language-partition-native-pair-runtime-1'
references = {}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def read(path):
    references[str(path.relative_to(ROOT))] = sha(path)
    return json.loads(path.read_bytes())
manifest = read(RUNTIME / 'FILES.json')
assert sha(RUNTIME / 'FILES.json') == '0431e823d34f2eed271b387dd79d603680b93e56bb7295cc598066c54da7812d'
for relative, record in manifest.items():
    path = RUNTIME / relative
    assert path.is_file() and not path.is_symlink()
    assert sha(path) == record['sha256'] and path.stat().st_size == record['bytes']
    references[str(path.relative_to(ROOT))] = record['sha256']
assert len(read(RUNTIME / 'SYMLINKS.json')) == 6
binding = read(ROOT / 'artifacts/css-language-partition-native-publication-pair-binding-v1.json')
owner = ROOT / binding['owner_directory']
assert sha(owner / 'FILES.json') == binding['owner_manifest_sha256']
for relative, record in read(owner / 'FILES.json').items():
    path = owner / relative
    assert sha(path) == record['sha256']
    references[str(path.relative_to(ROOT))] = record['sha256']
policy = read(owner / 'POLICY.json')
roles = read(owner / 'SOURCE-ROLES.json')
assert list(roles) == ['dom/base/nsLineBreaker.cpp']
spec = importlib.util.spec_from_file_location('signature', owner / 'assess.py')
assessor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assessor)
summary, signatures, builds = {}, {}, {}
for role in ('original', 'candidate'):
    build = read(RUNTIME / (role + '-build') / 'RESULT.json')
    assert build['command_success'] and build['preservation_verified']
    assert build['application_metadata']['revision'] == policy['head']
    assert build['native_sources'] == {path: value['base_sha256' if role == 'original' else 'candidate_sha256'] for path, value in roles.items()}
    builds[role] = build['application_metadata']
    summary[role], signatures[role] = {}, {}
    for lane in ('target', 'regression', 'context'):
        events = [json.loads(line) for line in (RUNTIME / (role + '-wpt-' + lane) / 'raw.jsonl').read_text().splitlines()]
        rows = [row for row in events if row.get('action') == 'test_status']
        ends = [row for row in events if row.get('action') == 'test_end']
        summary[role][lane] = {'callbacks': dict(collections.Counter(row['status'] for row in rows)), 'endings': dict(collections.Counter(row['status'] for row in ends))}
        signatures[role].update({(row['test'], row['subtest']): assessor.signature(row) for row in rows})
assert len(signatures['original']) == len(signatures['candidate']) == 897
assert signatures['original'].keys() == signatures['candidate'].keys()
prior_pass = 0
for key, value in signatures['original'].items():
    if value['status'] == 'PASS':
        assert signatures['candidate'][key] == value
        prior_pass += 1
assert prior_pass == 806
targets = {(page, name) for lane in ('regression', 'context') for page, names in policy['wpt_lanes'][lane]['target_subtests'].items() for name in names}
assert len(targets) == 368
assert all(signatures['candidate'][key]['status'] == 'PASS' for key in targets)
controls = signatures['original'].keys() - targets
assert len(controls) == 529 and all(signatures['candidate'][key] == signatures['original'][key] for key in controls)
assert summary['original']['regression']['callbacks'] == {'PASS': 637, 'FAIL': 83}
assert summary['candidate']['regression']['callbacks'] == {'PASS': 666, 'FAIL': 54}
assert summary['original']['context']['callbacks'] == {'FAIL': 8}
assert summary['candidate']['context']['callbacks'] == {'PASS': 8}
assert all(summary[role]['target']['callbacks'] == {'PASS': 169} for role in summary)
root_replay = read(ROOT / 'artifacts/css-language-partition-publication-evidence-root-v1.json')
assert root_replay['pair_binding_sha256'] == sha(ROOT / 'artifacts/css-language-partition-native-publication-pair-binding-v1.json')
assert (root_replay['language_target_PASS'], root_replay['context_target_PASS'], root_replay['preserved_other_callbacks'], root_replay['preserved_endings'], root_replay['complete_signatures']) == (360, 8, 529, 23, 920)
assert root_replay['derived_gate'] and not root_replay['stored_raw_gate']
spec = importlib.util.spec_from_file_location('ports', owner / 'port_comparison.py')
ports = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ports)
derived = ports.compare(ROOT, RUNTIME, policy, read(RUNTIME / 'original-wpt-regression/ASSESSMENT.json'), read(RUNTIME / 'candidate-wpt-regression/ASSESSMENT.json'), assessor.signature)
assert derived['derived_language_gate'] and derived['errors'] == [] and derived['preserved_signatures'] == 381
stored = read(RUNTIME / 'DERIVED-COMPARISON.json')
assert stored == dict(derived, publication_observation_gate=True, native_acceptance=False)
terminal = read(RUNTIME / 'ROOT-OWNER-TERMINAL.json')
assert terminal['session'] == 73082 and terminal['terminal'] is True and terminal['terminal_chunk'] == '848c63' and terminal['exit'] == 0
assert terminal['result_sha256'] == sha(RUNTIME / 'RESULT.json')
result = read(RUNTIME / 'RESULT.json')
assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
live_terminal = read(RUNTIME / 'ROOT-LIVE-AUDIT-TERMINAL.json')
assert live_terminal['session'] == 37056 and live_terminal['terminal'] is True and live_terminal['terminal_chunk'] == '3d6457' and live_terminal['exit'] == 0
assert live_terminal['audit_sha256'] == sha(RUNTIME / 'ROOT-LIVE-RESTORATION.json')
live = read(RUNTIME / 'ROOT-LIVE-RESTORATION.json')
assert live['independent_live_restoration_verified'] and live['backup_removed'] and len(live['independently_absent_process_groups']) == 10
script = ROOT / 'artifacts/css-language-partition-native-live-audit-v1.py'
assert sha(script) == live['audit_script_sha256']
references[str(script.relative_to(ROOT))] = sha(script)
context = read(ROOT / 'artifacts/css-language-context-original-observation-v1.json')
assert context['raw_sha256'] == sha(RUNTIME / 'original-wpt-context/raw.jsonl')
assert sum(row['first_failure_in_unknown_context_comparison'] for row in context['observations']) == 4
observations = {'summary': summary, 'callbacks': 897, 'endings': 23, 'signatures': 920,
    'prior_PASS_full_signatures_exact': prior_pass, 'fewer_failing_callbacks': 37,
    'primary_improvements': 29, 'context_improvements': 8,
    'original_context_failure_kinds': {'calibration': 4, 'target_independence': 4},
    'remaining_hyphenation_ownership_failures': 54, 'candidate_PASS_pixel_values_archived': False,
    'build_metadata': builds, 'root_publication_replay': root_replay,
    'root_live_audit_authority': live_terminal, 'saved_only_review': True,
    'native_publication_performed': False, 'accepted_fix_increment': 0}
(HERE / 'OBSERVATIONS.json').write_text(json.dumps(observations, indent=2) + '\n')
(HERE / 'REFERENCES.json').write_text(json.dumps(references, indent=2, sort_keys=True) + '\n')
print(json.dumps({'references': len(references), 'callbacks': 897, 'signatures': 920,
    'prior_PASS_signatures_exact': prior_pass, 'fewer_failing_callbacks': 37,
    'root_live_authority_not_reexecuted': True, 'native_actions': False}))
