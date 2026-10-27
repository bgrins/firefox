import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'artifacts/css-quote-scope-append-coc-execution-v2'


def read(name):
    return json.loads((RUNTIME / name).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observation(row):
    return {k: v for k, v in [
        ('status', row['status']), ('expected', row.get('expected') or row['status']),
        ('message', row.get('message')), ('known_intermittent', row.get('known_intermittent') or [])]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phases', type=int, choices=[2, 3], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    inputs = read('INPUTS.json')
    for path, sha in inputs['local_pins'].items():
        assert digest(RUNTIME / path) == sha, path
    for path, sha in read('REFERENCES.json').items():
        assert digest(ROOT / path) == sha, path
    admission_ref = inputs['admission']
    assert digest(ROOT / admission_ref['path']) == admission_ref['sha256']
    admission = json.loads((ROOT / admission_ref['path']).read_text())
    for binding in [admission['epoch'], *admission['evidence'], inputs['root_review']]:
        assert digest(ROOT / binding['path']) == binding['sha256']
    before = read('BEFORE.json')
    proposal = ROOT / 'artifacts/css-quote-scope-append-coc-inputs-v1'
    for name, expected in json.loads((proposal / 'FILES.json').read_text()).items():
        assert digest(proposal / name) == (expected['sha256'] if isinstance(expected, dict) else expected)
    fixture = 'testing/web-platform/tests/css/css-contain/quote-scoping-append-invalidation.html'
    assert digest(proposal / 'fixture' / fixture) == before['pins'][fixture]
    config = read('ACTUAL-CONFIG.json')
    sources = read('SOURCE-PINS.json')
    binary_names = set(admission['binaries'])
    assert before['roles'] == len(before['pins']) == 1177
    names = {(test, name) for test, roster in config['expected_subtests'].items() for name in roster}
    historical = {(r['test'], r['subtest']): observation(r) for r in read('HISTORICAL-OBSERVATIONS.json')['original']}
    assert len(names) == 64 and names == set(historical)
    summaries, prior, all_pins = {}, None, {}
    phases = ['candidate-initial', 'scoped-original', 'candidate-restored'][:args.phases]
    for phase in phases:
        directory = RUNTIME / ('wpt-' + phase)
        events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
        run = json.loads((directory / 'RUN.json').read_text())
        rows = [e for e in events if e.get('action') == 'test_status']
        starts = [e for e in events if e.get('action') == 'test_start']
        ends = [e for e in events if e.get('action') == 'test_end']
        assert rows == run['rows'] and starts == run['starts'] and ends == run['ends']
        assert len(rows) == 64 and len(starts) == len(ends) == 19
        assert Counter(e['test'] for e in starts) == Counter(e['test'] for e in ends)
        observed = {(r['test'], r['subtest']): observation(r) for r in rows}
        terminal = {e['test']: observation(e) for e in ends}
        assert set(observed) == names and len(terminal) == 19
        assert run['complete'] is True and not run['infrastructure_faults']
        assert run['before'] == run['after'] == read(phase + '-PRE.json')['pins'] == read(phase + '-POST.json')['pins']
        assert run['exit'] == (1 if phase == 'scoped-original' else 0)
        command = run['command']
        assert '--headless' in command and '--processes=1' in command and './mach' in command
        assert command[command.index('--no-manifest-download') + 1:] == config['tests']
        assert json.loads((directory / 'PROCESS.json').read_text())['command'] == command
        cleanup = json.loads((directory / 'CLEANUP.json').read_text())
        assert cleanup == {'owned_group_absent': True, 'errors': []}
        assert json.loads((directory / 'PROCESS-CLEANUP.json').read_text())['owned_group_absent'] is True
        for test, expected in config['expected_end_only'].items():
            assert terminal[test]['status'] == terminal[test]['expected'] == expected
            assert not terminal[test]['known_intermittent']
        for test in config['expected_subtests']:
            assert terminal[test]['status'] == terminal[test]['expected'] == 'OK'
        if phase == 'candidate-initial':
            assert all(v['status'] == v['expected'] == 'PASS' for v in observed.values())
            prior = observed, terminal
        elif phase == 'scoped-original':
            assert observed == historical
            assert all(v == prior[0][key] for key, v in observed.items() if v['status'] == 'PASS')
            assert terminal == prior[1]
            for (test, name), row in observed.items():
                if row['status'] != 'FAIL':
                    continue
                prefix = 'assert_equals: Inserted quote updates child scope: '
                assert row['message'].startswith(prefix)
                history, end = json.JSONDecoder().raw_decode(row['message'][len(prefix):])
                assert set(history) == {'initial', 'mutated', 'fresh', 'afterFresh', 'restored'}
                assert history['mutated'] == history['afterFresh'] == history['initial'] == history['restored']
                assert history['fresh'] != history['mutated']
                assert row['message'][len(prefix) + end:] == f" expected {history['fresh']} but got {history['mutated']}"
                assert 'trailing quote=false; insert before=true' in name
        else:
            assert (observed, terminal) == prior
        expected_pins = dict(before['pins'])
        expected_pins.update({n: run['before'][n] for n in binary_names})
        expected_pins.update({n: v['scoped_original_sha256' if phase == 'scoped-original' else 'candidate_sha256'] for n, v in sources.items()})
        assert run['before'] == expected_pins
        all_pins[phase] = run['before']
        summaries[phase] = {'rows': dict(Counter(r['status'] for r in rows)),
                            'ends': dict(Counter(e['status'] for e in ends)), 'wpt_exit': run['exit'],
                            'raw_sha256': digest(directory / 'raw.json'), 'run_sha256': digest(directory / 'RUN.json')}
        if phase != 'candidate-initial':
            build = RUNTIME / (phase + '-build')
            result = json.loads((build / 'build-RESULT.json').read_text())
            assert result['exit'] == 0 and result['error'] is None and result['stop_reason'] is None
            assert not result['cleanup_errors'] and result['owned_group_absent'] is True
            assert json.loads((build / 'build-PROCESS.json').read_text())['command'][1:] == ['./mach', 'build', '-j', '2']
            assert json.loads((build / 'build-GROUP-CLEANUP.json').read_text())['owned_group_absent'] is True
            wake = json.loads((build / 'WAKE-RESULT.json').read_text())
            assert wake['exit'] == 0 and wake['owned_group_absent'] is True
            assert read(phase + '-BUILD-POST.json')['pins'] == run['before']
    for path in sorted(RUNTIME.glob('*-PRE.json')) + sorted(RUNTIME.glob('*-POST.json')):
        receipt = json.loads(path.read_text())
        assert receipt['roles'] == len(receipt['pins']) == 1177
        for key in ['head', 'entries', 'cached_diff']:
            assert receipt['index'][key] == before['index'][key]
        for domain in ['root', 'nested']:
            obs = receipt['index_observations'][domain]
            assert obs['semantic_equal'] is True and obs['flags_before'] == obs['flags_after'] == admission['index_flags'][domain]
    if args.phases == 3:
        outer = read('OUTER-EXECUTION.json')
        assert outer == {'session_id': 32733, 'launch_chunk_id': '718d05',
                         'terminal_chunk_id': '8c6823', 'terminal': True, 'exit_code': 0}
        result = read('RESULT.json')
        assert result['success'] is True and result['error'] is None and not result['recovery_errors']
        assert result['captured_phases'] == phases and result['outstanding_processes'] == {} and result['wpt_group'] is None
        assert result['source_transitions'] == [{'path': n, 'variant': variant} for variant in ['scoped-original', 'candidate-restored'] for n in sources]
        final = read('FINAL.json')
        assert final['pins'] == all_pins['candidate-restored']
        assert final['index']['working_diff'] == before['index']['working_diff']
        assert final['modified_native_paths'] == before['modified_native_paths']
    args.output.write_text(json.dumps({'status': 'ARCHIVE_JOINS_PASS' if args.phases == 3 else 'PENDING_RESTORED_AND_OUTER_TERMINAL',
                                      'phases': summaries, 'repairs': 12, 'live_checks': False,
                                      'outer_terminal_authenticated': args.phases == 3}, indent=2) + '\n')


if __name__ == '__main__':
    main()
