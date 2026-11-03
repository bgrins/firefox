from collections import Counter
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-attr-fallback-archived-original-runtime-v1'
refs = {}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    refs[str(path.relative_to(ROOT))] = sha(path)
    return json.loads(path.read_text())


raw = RUNTIME / 'raw.jsonl'
refs[str(raw.relative_to(ROOT))] = sha(raw)
events = [json.loads(line) for line in raw.read_text().splitlines()]
roster = read(ROOT / 'artifacts/css-attr-own-fallback-fix-v1/ROSTER.json')
page, names = next(iter(roster.items()))
assert len(roster) == 1 and len(names) == len(set(names)) == 24
selected = {action: [event for event in events if event['action'] == action] for action in
            ['suite_start', 'test_start', 'test_status', 'test_end', 'suite_end', 'crash']}
assert not selected['crash']
assert all(len(selected[action]) == 1 for action in ['suite_start', 'test_start', 'test_end', 'suite_end'])
assert selected['test_start'][0]['test'] == selected['test_end'][0]['test'] == page
assert selected['test_end'][0]['status'] == 'OK'
statuses = selected['test_status']
assert len(statuses) == 24 and Counter(event['subtest'] for event in statuses) == Counter(names)
assert all(event['test'] == page and event['status'] in ['PASS', 'FAIL'] for event in statuses)
assert events.index(selected['suite_start'][0]) < events.index(selected['test_start'][0])
assert events.index(selected['test_start'][0]) < min(events.index(event) for event in statuses)
assert max(events.index(event) for event in statuses) < events.index(selected['test_end'][0]) < events.index(selected['suite_end'][0])
assert not [event for event in events if event['action'] == 'log' and event.get('level') in ['ERROR', 'CRITICAL']]
failed = {event['subtest'] for event in statuses if event['status'] == 'FAIL'}
assert failed == {mode + ': ' + case for mode in ['direct', 'unregistered', 'registered']
                  for case in ['missing-raw-fallback', 'invalid-typed-fallback', 'missing-typed-fallback']}
for event in statuses:
    if event['status'] == 'FAIL':
        assert 'Only values produced by attr() are rejected as URLs' in event['message']
        assert 'data:image/gif;base64,' in event['message']
result = read(RUNTIME / 'RESULT.json')
assert result['success'] and result['exit'] == 1 and result['execution_error'] is None
assert result['archive_preserved'] and result['staged_preserved'] and not result['native_fix_acceptance']
assessment = read(RUNTIME / 'ASSESSMENT.json')
assert assessment['complete'] and assessment['subtests'] == statuses and assessment['endings'] == selected['test_end']
assert assessment['counts'] == dict(Counter(event['status'] for event in statuses))
pre, post = read(RUNTIME / 'ARCHIVE-PRE.json'), read(RUNTIME / 'ARCHIVE-POST.json')
assert pre == post
snapshot = read(ROOT / 'artifacts/css-original-e86-browser-snapshot-v1/SNAPSHOT.json')
app = Path(snapshot['application'])
assert not app.is_symlink() and not app.parent.is_symlink()
actual = {}
for path in app.rglob('*'):
    assert not path.is_symlink()
    if path.is_file():
        actual[str(path.relative_to(app))] = {'bytes': path.stat().st_size,
                                            'mode': stat.S_IMODE(path.stat().st_mode), 'sha256': sha(path)}
assert actual == snapshot['files'] and len(actual) == pre['files'] == 8326
assert hashlib.sha256(json.dumps(actual, sort_keys=True).encode()).hexdigest() == pre['manifest_sha256']
build = read(ROOT / snapshot['build_receipt'])
assert refs[snapshot['build_receipt']] == snapshot['build_receipt_sha256']
assert build['command_success'] and build['native_sources'] == snapshot['native_sources']
run_info = selected['suite_start'][0]['run_info']
assert run_info['browser_build_id'] == snapshot['build_id'] == build['application_metadata']['browser_build_id']
assert run_info['revision'] == snapshot['native_head']
staged = read(RUNTIME / 'STAGED.json')
assert all(sha(RUNTIME / name) == digest for name, digest in staged.items())
trees = read(RUNTIME / 'STAGED-TREES.json')
for name, files in trees.items():
    folder = RUNTIME / name
    current = {str(path.relative_to(folder)): sha(path) for path in folder.rglob('*')
               if path.is_file() and not path.is_symlink()}
    assert current == files
assert (RUNTIME / 'tests/tools').is_symlink()
assert (RUNTIME / 'tests/tools').resolve() == ROOT / 'testing/web-platform/tests/tools'
cleanup = read(RUNTIME / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
command = read(RUNTIME / 'COMMAND.json')
assert not Path(command['temporary']).exists()
assert '--binary=' + str(app / 'Contents/MacOS/firefox') in command['command']
process = read(RUNTIME / 'PROCESS.json')
observation = {'counts': assessment['counts'], 'failed_names': sorted(failed), 'callbacks': 24,
               'page': page, 'test_starts': 1, 'page_ending': 'OK', 'suite_starts': 1, 'suite_ends': 1,
               'explicit_crash_events': 0, 'error_or_critical_logs': 0,
               'wpt_exit': 1, 'owner_recorded_observation_success': True,
               'source_role': 'archived-original', 'native_head': snapshot['native_head'],
               'browser_build_id': snapshot['build_id'], 'current_archive_files_authenticated': len(actual),
               'archive_bytes': snapshot['bytes'], 'staged_files_authenticated': len(staged),
               'staged_tree_count': len(trees), 'cleanup': cleanup, 'temporary_currently_absent': True,
               'pgid': process['pgid'], 'independent_live_process_census_performed': False,
               'outer_owner_terminal': None, 'new_browser_or_build_execution': False,
               'candidate_validation': False, 'native_fix_acceptance': False}
(HERE / 'OBSERVATIONS.json').write_text(json.dumps(observation, indent=2) + '\n')
(HERE / 'REFERENCES.json').write_text(json.dumps(refs, indent=2, sort_keys=True) + '\n')
print(json.dumps(observation))
