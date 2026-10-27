import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'artifacts/css-counter-scope-append-comparison-execution-v1'
SOURCE = ROOT / 'artifacts/css-counter-scope-append-comparison-runtime-v1'
INPUTS = ROOT / 'artifacts/css-counter-scope-append-comparison-inputs-v1'
SHA = lambda data: hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['original-initial', 'candidate-first', 'original-restored', 'candidate-final'])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.is_absolute() and not args.output.exists()
    seen = {}

    def body(path):
        data = path.read_bytes()
        seen[str(path.relative_to(ROOT))] = SHA(data)
        return data

    def read(path):
        return json.loads(body(path))

    def ref(binding):
        path = ROOT / binding['path']
        data = body(path)
        assert SHA(data) == binding['sha256']
        return json.loads(data)

    def load(name):
        path = SOURCE / (name + '.py')
        assert SHA(body(path)) == activated['local_pins'][name + '.py']
        spec = importlib.util.spec_from_file_location('counter_archive_' + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    activated = read(RUNTIME / 'INPUTS.json')
    assert activated['ready'] is True
    for name, digest in activated['local_pins'].items():
        assert SHA(body(RUNTIME / name)) == digest
    admission = ref(activated['admission'])
    assert admission['status'] == 'COUNTER_OCOC_EPOCH_VERIFIED' and admission['exit'] == 0
    review = ref(activated['root_review'])
    assert review['status'] == 'COUNTER_OCOC_ROOT_REVIEW_GO' and review['local_pins'] == activated['local_pins']
    epoch = ref(admission['epoch'])
    historical = ref(admission['baseline_probe_run'])
    policy, tests = load('policy'), load('tests')
    config = read(RUNTIME / 'ACTUAL-CONFIG.json')
    expected_config = read(INPUTS / 'CONFIG.json')
    roles = epoch['pins'] | admission['additional_roles']
    expected_config['guard_sources'] = list(roles)
    expected_config['reftests'] = list(expected_config['expected_end_only'])
    assert config == expected_config
    pins = read(INPUTS / 'SOURCE-PINS.json')
    phase = args.phase
    directory = RUNTIME / ('wpt-' + phase)
    run = read(directory / 'RUN.json')
    events = [json.loads(line) for line in body(directory / 'raw.json').decode().splitlines()]
    assert run['rows'] == [x for x in events if x.get('action') == 'test_status']
    assert run['starts'] == [x for x in events if x.get('action') == 'test_start']
    assert run['ends'] == [x for x in events if x.get('action') == 'test_end']
    assert tests.lifecycle(events, config) and not tests.infrastructure_faults(events)
    assert run['complete'] and not run['infrastructure_faults']
    assert tests.exit_matches_results(run['exit'], run['rows'] + run['ends'])
    assert len(run['starts']) == len(run['ends']) == len(config['tests']) == 10
    for test, names in config['expected_subtests'].items():
        assert [x['subtest'] for x in run['rows'] if x['test'] == test] == names
    captures = {}
    if phase != 'original-initial':
        first = read(RUNTIME / 'wpt-original-initial/RUN.json')
        policy.check(first, config, 'original-initial', {}, historical)
        captures['original-initial'] = policy.values(first)
    if phase == 'candidate-final':
        candidate = read(RUNTIME / 'wpt-candidate-first/RUN.json')
        policy.check(candidate, config, 'candidate-first', captures, historical)
        captures['candidate-first'] = policy.values(candidate)
    policy.check(run, config, phase, captures, historical)
    pre = read(RUNTIME / (phase + '-PRE.json'))
    post = read(RUNTIME / (phase + '-POST.json'))
    binaries = admission['binaries']
    if phase != 'original-initial':
        build_pre = read(RUNTIME / (phase + '-BUILD-PRE.json'))
        build_post = read(RUNTIME / (phase + '-BUILD-POST.json'))
        build = read(RUNTIME / (phase + '-build/build-RESULT.json'))
        assert build['exit'] == 0 and build['error'] is None and build['stop_reason'] is None
        assert build['owned_group_absent'] and not build['cleanup_errors']
        for name in ['build-GROUP-CLEANUP.json', 'wake-GROUP-CLEANUP.json']:
            cleanup = read(RUNTIME / (phase + '-build') / name)
            assert cleanup['owned_group_absent']
            if cleanup['method'] == 'direct-process-reap-and-pgid-census':
                assert cleanup['remaining_members'] == []
        binaries = {name: build_post['pins'][name] for name in binaries}
        assert build_post['pins'] == pre['pins']
        assert {k: v for k, v in build_pre['pins'].items() if k not in binaries} == {
            k: v for k, v in build_post['pins'].items() if k not in binaries}
    variant = 'original' if phase.startswith('original') else 'candidate'
    expected = roles | binaries | {name: item[variant + '_sha256'] for name, item in pins.items()}
    assert run['before'] == run['after'] == pre['pins'] == post['pins'] == expected
    for receipt in [pre, post]:
        assert receipt['roles'] == len(expected)
        for group in ['root', 'nested']:
            obs = receipt['index_observations'][group]
            assert obs['semantic_equal'] and obs['flags_before'] == obs['flags_after'] == admission['index_flags'][group]
        assert all(receipt['index'][key] == epoch['semantic_index'][key] for key in ['head', 'entries', 'cached_diff'])
    process = read(directory / 'PROCESS.json')
    assert process['pid'] == process['pgid'] and process['command'] == run['command']
    assert process['cwd'] == str(ROOT)
    assert run['command'][-10:] == config['tests']
    assert '--log-raw=' + str(directory / 'raw.json') in run['command']
    assert '--binary=' + str(ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox') in run['command']
    cleanup = read(directory / 'CLEANUP.json')
    group = read(directory / 'PROCESS-CLEANUP.json')
    assert cleanup == {'owned_group_absent': True, 'errors': []} and group['owned_group_absent']
    if group['method'] == 'direct-process-reap-and-pgid-census':
        assert group['remaining_members'] == []
    assert all(SHA((ROOT / name).read_bytes()) == digest for name, digest in seen.items())
    args.output.mkdir()
    (args.output / 'REFERENCES.json').write_text(json.dumps(seen, indent=2) + '\n')
    check = dict(status='COUNTER_OCOC_PHASE_ARCHIVE_REVIEW_PASS', phase=phase,
                 rows=len(run['rows']), row_counts={status: sum(x['status'] == status for x in run['rows']) for status in ['PASS', 'FAIL']},
                 ends=len(run['ends']), wpt_exit=run['exit'], guarded_roles=len(expected),
                 sources={name: expected[name] for name in pins}, binaries=binaries,
                 raw_rows_replayed=True, source_binary_map_join=True, process_cleanup_archived=True,
                 terminal_review=False, native_acceptance=False, live_verification=False)
    (args.output / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
    print(json.dumps(check))


if __name__ == '__main__':
    main()
