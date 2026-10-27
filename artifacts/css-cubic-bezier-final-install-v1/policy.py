import hashlib
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def archived_candidate(root, tests, binding):
    directory = root / binding['directory']
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    read = lambda p: json.loads(p.read_text())
    need(sha(directory / 'FILES.json') == binding['manifest_sha256'], 'historical runtime manifest')
    for name, digest in read(directory / 'FILES.json').items():
        part = Path(name)
        need(not part.is_absolute() and '..' not in part.parts, 'historical relative path')
        need(sha(directory / name) == digest, 'historical payload ' + name)
    execution = read(directory / 'ROOT-EXECUTION.json')
    need(execution == binding['execution'] and execution['outer_exit'] == 0, 'actual historical terminal')
    result = read(directory / 'RESULT.json')
    need(result['success'] and result['error'] is None and not result['recovery_errors']
         and not result['outstanding_processes'] and result['wpt_group'] is None, 'historical comparison restored')
    run = read(directory / 'wpt-candidate/RUN.json')
    config = read(directory / 'CONFIG.json')
    events = [json.loads(line) for line in (directory / 'wpt-candidate/raw.json').read_text().splitlines()]
    rows = [e for e in events if e.get('action') == 'test_status']
    ends = [e for e in events if e.get('action') == 'test_end']
    starts = [e for e in events if e.get('action') == 'test_start']
    need(run['complete'] and run['before'] == run['after'], 'historical candidate resources stable')
    need(run['rows'] == rows and run['starts'] == starts and run['ends'] == ends, 'historical raw/RUN join')
    need(tests.lifecycle(events, config) and not tests.infrastructure_faults(events), 'historical lifecycle')
    need(tests.exit_matches_results(run['exit'], rows + ends), 'historical exit')
    need(len(rows) == 113 and len(ends) == len(starts) == 5
         and all(e['status'] == e.get('expected', e['status']) == 'OK' and not e.get('known_intermittent') for e in ends), 'historical complete harnesses')
    for test, names in config['expected_subtests'].items():
        need([r['subtest'] for r in rows if r['test'] == test] == names, 'historical exact roster')
    return rows


def compare(old_rows, new_rows, policy):
    def keyed(rows):
        value = {(r['test'], r['subtest']): r for r in rows}
        need(len(value) == len(rows) == 113, 'exact unique 113 rows')
        return value
    old, new = keyed(old_rows), keyed(new_rows)
    required = {(r['test'], r['subtest']) for r in policy['candidate_mandatory_pass']}
    controls = {(r['test'], r['subtest']) for r in policy['exact_fresh_control_identities']}
    need(len(required) == 38 and len(controls) == 75 and not required & controls
         and set(old) == set(new) == required | controls, 'exact historical and installed identities')
    metadata_targets = {k for k in old if k[0] in (
        '/css/css-easing/timing-functions-syntax-computed.html',
        '/css/css-easing/timing-functions-syntax-valid.html') and (
        'steps(calc(1), jump-none)' in k[1] or
        'cubic-bezier(calc(-2), calc(0.7 / 2), calc(1.5), calc(0))' in k[1])}
    need(len(metadata_targets) == 4, 'exact four metadata changes')
    for key, a in old.items():
        b = new[key]
        need(all(a.get(f) == b.get(f) for f in ('status', 'message', 'known_intermittent')), 'historical raw result ' + str(key))
        if key in metadata_targets:
            need(a['status'] == b['status'] == 'PASS' and a.get('expected', a['status']) == 'FAIL'
                 and b.get('expected', b['status']) == 'PASS', 'only known metadata FAIL to PASS')
        else:
            need(a.get('expected') == b.get('expected'), 'unrelated expectation ' + str(key))
        if key in required:
            need(b['status'] == 'PASS' and b.get('message') in (None, '') and not b.get('known_intermittent'), '38 target PASS')
    need(sum(r['status'] == 'PASS' for r in new_rows) == 110
         and sum(r['status'] == 'FAIL' for r in new_rows) == 3, 'actual historical candidate outcomes reproduced')
    return {'rows': 113, 'target_pass': 38, 'PASS': 110, 'FAIL': 3,
            'metadata_changes': [list(k) for k in sorted(metadata_targets)],
            'all_other_observations_and_expectations_exact': True}
