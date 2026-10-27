import argparse
import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / 'artifacts/css-central-baseline-origin-runtime-v1'

def read(p):
    return json.loads(p.read_text())

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def authenticate(base, mapping):
    for name, value in mapping.items():
        p = base / name
        assert not p.is_symlink() and p.is_file() and digest(p) == value, name

parser = argparse.ArgumentParser()
parser.add_argument('--seal', required=True)
args = parser.parse_args()
assert digest(RUN / 'FILES.json') == args.seal
manifest = read(RUN / 'FILES.json')
authenticate(RUN, manifest)
authenticate(RUN, read(RUN / 'DRAFT-FILES.json'))
authenticate(ROOT, read(RUN / 'REFERENCES.json'))
c = read(RUN / 'CONFIG.json')
draft = ROOT / 'artifacts/css-central-baseline-origin-comparison-v1'
draft_config = read(draft / 'CONFIG.json')
assert c == {**draft_config, 'ready_for_execution': True}
for name, value in read(draft / 'DRAFT-FILES.json').items():
    if name not in ['CONFIG.json', 'REFERENCES.json']:
        assert digest(RUN / name) == value, name
state = read(RUN / 'STATE.json')
receipt = read(RUN / 'ROOT-FINAL-CHECK.json')
assert state['status'] == 'terminal' and state['restored']
assert state['restore_build_exit'] == 0 and not state['recovery_errors'] and 'failure' not in state
assert state['paired_preservation_passed'] and state['accepted_native_repair'] is False
before, final = read(RUN / 'BEFORE.json'), read(RUN / 'FINAL.json')
assert before == final
assert before['head'] == c['head'] and before['sources'] == c['source_pins']
assert len(before['sources']) == 44 and len(c['sources']) == 32
for name in c['sources']:
    assert digest(RUN / 'original' / name) == before['sources'][name], name
for key in ['state_sha256', 'final_sha256']:
    assert receipt[key] == digest(RUN / ('STATE.json' if key == 'state_sha256' else 'FINAL.json'))
assert receipt['restored_binary_pins'] == state['restored_binary_pins']
assert receipt['status'] == 'CENTRAL_COMPARISON_PASS_RESTORATION_VERIFIED'
assert receipt['draft_sha256'] == digest(RUN / 'DRAFT-FILES.json')
assert receipt['staged_paths'] == 925 and receipt['source_guards'] == 44
assert receipt['saved_source_bodies'] == 32 and receipt['existing_tests'] == 61
assert receipt['resource_guards'] == 232 and receipt['candidate_paths'] == 1
assert receipt['restored'] and receipt['restore_build_exit'] == 0
assert receipt['new_accepted_fixes'] == 0 and receipt['native_range_obligation_open']
assert state['lint_exit'] == read(RUN / 'fixture-lint.json')['exit'] == 0
resources = read(RUN / 'RESOURCES.json')
owned = next(iter(c['install']))
phase_resources = {**resources, owned: digest(RUN / c['install'][owned])}
assert resources[owned] is None
assert len(resources) == 232
records = {}
result = {'runtime_seal': args.seal, 'runtime_payloads': len(manifest), 'phases': {}}
for phase in ['baseline', 'candidate']:
    directory = RUN / phase
    observed = read(directory / 'RUN.json')
    events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
    rows = [e for e in events if e.get('action') == 'test_status']
    starts = [e for e in events if e.get('action') == 'test_start']
    ends = [e for e in events if e.get('action') == 'test_end']
    assert rows == observed['rows'] and starts == observed['starts'] and ends == observed['ends']
    assert observed['complete'] and not observed['infrastructure_faults']
    assert observed['before'] == observed['after']
    expected_urls = set(c['expected_subtests']) | {c['reference_test']}
    assert len(starts) == len(ends) == len(expected_urls) == 14
    assert {e['test'] for e in starts} == {e['test'] for e in ends} == expected_urls
    assert len(rows) == len({(e['test'], e['subtest']) for e in rows}) == 216
    assert all(e['status'] in ['PASS', 'FAIL'] for e in rows)
    for url, names in c['expected_subtests'].items():
        assert [e['subtest'] for e in rows if e['test'] == url] == names
    for e in ends:
        assert e['status'] == ('PASS' if e['test'] == c['reference_test'] else 'OK')
    assert sum(e.get('action') == 'suite_start' for e in events) == 1
    assert sum(e.get('action') == 'suite_end' for e in events) == 1
    assert not any(e.get('action') in ['crash', 'suite_abort', 'test_abort'] or
                   (e.get('action') == 'log' and e.get('level', '').upper() in ['ERROR', 'CRITICAL'])
                   for e in events)
    namespace = {}
    exec(compile((RUN / 'tests.py').read_text(), 'reviewed-tests.py', 'exec'), namespace)
    assert not namespace['infrastructure_faults'](events)
    cleanup = read(directory / 'CLEANUP.json')
    assert cleanup == {'owned_group_absent': True, 'errors': []}
    phase_state = state['phases'][phase]
    assert phase_state['build_exit'] == read(RUN / (phase + '-build.json'))['exit'] == 0
    snap = phase_state['source_before_build']
    assert snap == phase_state['source_after_build']
    for key in ['head', 'index_diff_sha256', 'index_entries_sha256']:
        assert snap[key] == before[key]
    expected_sources = {**c['head_pins'], **(c['candidate_pins'] if phase == 'candidate' else {})}
    assert snap['sources'] == expected_sources
    assert observed['before'] == {**phase_resources, **expected_sources, **phase_state['binary_pins']}
    selected = rows + [e for e in ends if e['test'] == c['reference_test']]
    records[phase] = {(e['test'], e.get('subtest')): {k: e.get(k) for k in ['status', 'message', 'expected', 'known_intermittent']} for e in selected}
    result['phases'][phase] = {'exit': observed['exit'], 'subtests': dict(collections.Counter(e['status'] for e in rows)),
                               'reference': 'PASS', 'failures': [e for e in rows if e['status'] == 'FAIL'],
                               'binary_pins': phase_state['binary_pins']}
old, new = records['baseline'], records['candidate']
assert old.keys() == new.keys()
repaired = [list(key) for key in old if old[key]['status'] == 'FAIL' and new[key]['status'] == 'PASS']
retained = [key for key in old if new[key]['status'] == 'FAIL']
assert len(repaired) == len(retained) == 4
assert all(old[key] == new[key] for key in retained)
assert all(new[key]['status'] == 'PASS' for key in old if old[key]['status'] == 'PASS')
main = next(iter(c['expected_subtests']))
assert all(key[0] == main for key in repaired)
assert all(new[(main, name)]['status'] == 'PASS' for name in c['expected_subtests'][main])
assert read(RUN / 'COMPARISON.json') == {'regressions': [], 'changed_failures': [], 'repaired': repaired, 'native_acceptance': False}
assert result['phases']['baseline']['subtests'] == {'PASS': 208, 'FAIL': 8}
assert result['phases']['candidate']['subtests'] == {'PASS': 212, 'FAIL': 4}
assert receipt['subtests'] == {phase: result['phases'][phase]['subtests'] for phase in ['baseline', 'candidate']}
assert receipt['repaired'] == 4 and receipt['regressions'] == receipt['changed_retained_failures'] == 0
assert receipt['reference_pass_both']
build_notes = {}
for name in ['baseline-build.log', 'candidate-build.log', 'restore-build.log']:
    text = (RUN / name).read_text(errors='replace')
    assert 'Your build was successful!' in text
    build_notes[name] = {'tracebacks': text.count('Traceback (most recent call last):'),
                        'export_keyerrors': text.count("KeyError: 'export'")}
result.update(status='PASS', repaired=repaired, retained_failure_count=4, root_receipt=receipt,
              build_diagnostics=build_notes, live_state_checked=False, native_browser_build_index_actions=False)
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['phases', 'root_receipt']}, indent=2))
