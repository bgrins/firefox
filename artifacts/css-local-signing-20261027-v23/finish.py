import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PREVIOUS = ROOT / 'artifacts/css-local-signing-20261027-v22'
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=ENV)


assert not sys.flags.optimize
assert not any(os.environ.get(k) for k in ['GIT_DIR', 'GIT_INDEX_FILE', 'GIT_WORK_TREE'])
spec = importlib.util.spec_from_file_location('number_state', RUNTIME / 'state.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
epoch = read(HERE / 'CURRENT-EPOCH.json')
s.a.verify_current(s.h, ROOT, ENV, epoch)
previous = read(PREVIOUS / 'FINAL-CHECK.json')
previous_receipt = read(PREVIOUS / 'checkpoint-receipt.json')
assert previous['head'] == previous_receipt['commit'] and previous_receipt['signature_verified']
assert previous['signatures_verified'] and previous['staging_empty']
assert previous['accepted_fixes'] == 137 and previous['candidate_accepted'] is False
assert sha(RUNTIME / 'CURRENT-EPOCH.json') == previous['current_epoch_sha256']
control_bytes = {name: (RUNTIME / name).read_bytes() for name in ['ROLE.json', 'OWNED.json', 'CURRENT-EPOCH.json']}
assert read(HERE / 'INITIAL-EPOCH.json')['semantic_index']['head'] == previous['head']
receipt = read(HERE / 'research-receipt.json')
selection = read(HERE / 'research-selection.json')
assert receipt['parent'] == previous['head'] and receipt['signature_verified']
assert receipt['commit'] == epoch['semantic_index']['head'] == git('rev-parse', 'HEAD').decode().strip()
assert git('rev-parse', receipt['commit'] + '^').decode().strip() == previous['head']
assert git('rev-parse', receipt['commit'] + '^{tree}').decode().strip() == receipt['tree']
assert set(selection['files']) == set(receipt['files']) == set(selection['source_pins'])
assert all(name.startswith('artifacts/') for name in selection['files'])
for name, pin in selection['source_pins'].items():
    assert sha(ROOT / name) == pin
    assert hashlib.sha256(git('show', receipt['commit'] + ':' + name)).hexdigest() == pin
packages = {
    'artifacts/css-registered-writing-mode-readiness-model-v1': '7e2d87e9cb87a8ec8e9468e0cb281b72ac37c179d6058d74f2f1f2244d3a453e',
    'artifacts/css-registered-container-unzoomed-source-wpt-draft-v1': '9ce6326a5b64c09dc28588ca5b2603e697d25ad69070377cd276af0780559e01',
    'artifacts/css-registered-staged-observation-wpt-v1': '2867a6ea15f00f3b524d166b972556fb4fc1a50c0ddadd706732ec83ed3a9663',
}
expected_files = set()
for directory, pin in packages.items():
    package = ROOT / directory
    assert sha(package / 'FILES.json') == pin
    expected_files.add(directory + '/FILES.json')
    for name, item in read(package / 'FILES.json').items():
        assert sha(package / name) == item['sha256']
        expected_files.add(directory + '/' + name)
assert expected_files == set(selection['files'])
model = read(ROOT / 'artifacts/css-registered-writing-mode-readiness-model-v1/validation-final/CHECK.json')
assert len(model['axioms']) == 11 and [r['exit'] for r in model['records']] == [0, 0, 0, 1, 1]
assert not model['native_refinement'] and model['canonical_coverage_credit'] == model['accepted_bug_credit'] == 0
fixture = read(ROOT / 'artifacts/css-registered-container-unzoomed-source-wpt-draft-v1/CHECK.json')
assert fixture['unique_named_tests'] == 16 and not fixture['browser_executed']
assert read(ROOT / 'artifacts/css-registered-staged-observation-wpt-v1/POLICY.json')['execution_enabled'] is False
native = previous['dirty_native_source_pins']
roles = read(ROOT / 'artifacts/css-registered-zoom-normalization-proposal-v3/SOURCE-ROLES.json')
assert len(native) == 7 and native == {name: role['candidate_sha256'] for name, role in roles.items()}
assert epoch['modified_native_paths'] == sorted(native)
assert set(git('diff', '--name-only').decode().splitlines()) == set(native)
assert not git('diff', '--cached', '--name-only')
assert not git('diff', previous['head'], receipt['commit'], '--', 'servo', 'layout', 'dom', 'testing')
for name, pin in native.items():
    assert sha(ROOT / name) == pin
for name in ['servo/components/style/custom_properties.rs', 'servo/components/style/properties/cascade.rs']:
    assert sha(ROOT / name) == hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest()
assert epoch['registered_number_transition'] == read(PREVIOUS / 'CURRENT-EPOCH.json')['registered_number_transition']
assert epoch['registered_number_transition']['compiled'] is True
assert epoch['registered_number_transition']['accepted'] is False
ledger_names = ['artifacts/stylo-bloom-tools/CURRENT-COMMITS.json', 'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md']
prior_update = read(PREVIOUS / 'ROADMAP-UPDATE.json')
before = {name: sha(ROOT / name) for name in ledger_names}
assert before == prior_update['after']
(HERE / 'ledger-preimages').mkdir()
(HERE / 'ledger-postimages').mkdir()
for name in ledger_names:
    (HERE / 'ledger-preimages' / Path(name).name).write_bytes((ROOT / name).read_bytes())
ledger = read(ROOT / ledger_names[0])
assert ledger['committed_native_fixes'] == 137
ledger.setdefault('research_signing_history', []).append(copy.deepcopy(ledger['latest_research_signing']))
ledger['latest_research_signing'] = {'status': 'SIGNED_VERIFIED_LOCAL', 'commits': {'research': receipt['commit']}, 'directory': str(HERE.relative_to(ROOT))}
research = ledger['latest_registered_number_research']
previous_observation = copy.deepcopy(research['latest_standalone_zoom_observation'])
research.setdefault('writing_mode_followup', {})['provider_readiness_model'] = {
    'artifact': 'artifacts/css-registered-writing-mode-readiness-model-v1',
    'audited_declarations': 11, 'decisive_false_controls': 2,
    'native_refinement_proved': False, 'browser_reproduction_claimed': False,
    'canonical_coverage_increment': 0, 'accepted_bug_increment': 0,
}
research.setdefault('zoom_followup_checkpoint', {})['unzoomed_source_container_controls'] = {
    'artifact': 'artifacts/css-registered-container-unzoomed-source-wpt-draft-v1',
    'prepared_tests': 16, 'planned_snapshots': 160, 'browser_executed': False,
    'scope': 'Unzoomed source containers and target zoom; no nonunit source-zoom oracle',
}
research['zoom_followup_checkpoint']['disabled_observation_preparation'] = {
    'artifact': 'artifacts/css-registered-staged-observation-wpt-v1',
    'execution_enabled': False, 'browser_executed': False, 'post_signing_successor_required': True,
}
assert research['latest_standalone_zoom_observation'] == previous_observation
research['runner_head_rebind_required'] = True
ledger['latest_verified_working_epoch']['runner_head_rebind_required'] = True
(ROOT / ledger_names[0]).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
title, rest = (ROOT / ledger_names[1]).read_text().split('\n\n', 1)
paragraph = ('Research checkpoint: the provider-readiness model has 11 audited declarations and two decisive false controls; '
             'it proves a conditional scheduling/cache witness, not native refinement or a browser reproduction. '
             'Sixteen container target-zoom tests are prepared with unzoomed source containers and remain unexecuted. '
             'The observation-runner preparation is archived disabled and requires a successor. '
             'Prior standalone seven-file browser findings, raw reftest comparison and separate port adjudication remain unchanged. '
             'The seven native edits remain unaccepted, the admission overlay remains parked, and the accepted-fix count stays 137. '
             'Further execution requires a runner bound to the new signed HEAD.')
(ROOT / ledger_names[1]).write_text(title + '\n\n' + paragraph + '\n\n' + rest)
for name in ledger_names:
    (HERE / 'ledger-postimages' / Path(name).name).write_bytes((ROOT / name).read_bytes())
current = copy.deepcopy(epoch)
for name in ledger_names:
    for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
        if name in current[key]:
            assert current[key][name] == before[name]
            current[key][name] = sha(ROOT / name)
state = s.h.index_state(ROOT, ENV)
current['semantic_index'] = s.h.semantic_index(state)
current['raw_index_observation']['current'] = state['raw_index']
s.a.verify_current(s.h, ROOT, ENV, current)
(HERE / 'CURRENT-EPOCH.json').write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
save(HERE / 'ROADMAP-UPDATE.json', {'before': before, 'after': {name: sha(ROOT / name) for name in ledger_names},
    'prior_authorized_ledger_update': str((PREVIOUS / 'ROADMAP-UPDATE.json').relative_to(ROOT)),
    'accepted_fixes': 137, 'dirty_native_source_pins': native, 'actual_browser_findings_changed': False})
save(HERE / 'PRE-CHECKPOINT-EPOCH.json', current)
save(HERE / 'PREVIOUS-FINAL-CHECK.json', previous)
(HERE / 'CHECKPOINT.md').write_text('# Research checkpoint\n\n' + paragraph + '\n\nResearch commit: ' + receipt['commit'] + '\n')
files = [HERE / name for name in ['commit.py', 'finish.py', 'INITIAL-EPOCH.json', 'BEFORE.json',
    'PRE-CHECKPOINT-EPOCH.json', 'PREVIOUS-FINAL-CHECK.json', 'ROADMAP-UPDATE.json', 'CHECKPOINT.md',
    'research-selection.json', 'research-receipt.json', 'research-signature.log']]
files += list((HERE / 'ledger-preimages').iterdir()) + list((HERE / 'ledger-postimages').iterdir())
files += [ROOT / name for name in ledger_names]
pins = {str(path.relative_to(ROOT)): sha(path) for path in files}
save(HERE / 'checkpoint-selection.json', {'id': 'checkpoint',
    'message': 'No bug - Checkpoint readiness proof and pending container zoom controls. r?#firefox-style-system-reviewers',
    'files': sorted(pins), 'source_pins': pins})
with (HERE / 'checkpoint-driver.log').open('x') as stream:
    subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE / 'commit.py'), str(HERE / 'checkpoint-selection.json')],
                   cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
final = read(HERE / 'checkpoint-receipt.json')
assert final['signature_verified'] and final['parent'] == receipt['commit']
current = read(HERE / 'CURRENT-EPOCH.json')
s.a.verify_current(s.h, ROOT, ENV, current)
assert not git('diff', '--cached', '--name-only')
assert set(git('diff', '--name-only').decode().splitlines()) == set(native)
for name, pin in native.items():
    assert sha(ROOT / name) == pin
for name, pin in pins.items():
    assert hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest() == pin
assert all((RUNTIME / name).read_bytes() == data for name, data in control_bytes.items())
(RUNTIME / 'CURRENT-EPOCH.json').write_bytes((HERE / 'CURRENT-EPOCH.json').read_bytes())
result = copy.deepcopy(previous)
result.update(head=final['commit'], commits={'research': receipt['commit'], 'checkpoint': final['commit']},
    signatures_verified=True, staging_empty=True, tracked_tree_clean=False, dirty_native_source_pins=native,
    accepted_fixes=137, canonical_coverage_increment=0, candidate_accepted=False,
    current_epoch_sha256=sha(RUNTIME / 'CURRENT-EPOCH.json'), runtime_epoch_synchronized=True,
    runner_head_rebind_required=True, readiness_model_audited_declarations=11,
    readiness_model_false_controls=2, container_controls_prepared=16, container_controls_executed=False,
    prior_browser_findings_unchanged=True)
save(HERE / 'FINAL-CHECK.json', result)
print((HERE / 'FINAL-CHECK.json').read_text(), flush=True)
