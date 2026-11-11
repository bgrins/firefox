import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAB = ROOT / 'artifacts/css-named-range-group-order-probe-20261110-v1'


def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(p):
    return json.loads(p.read_text())


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=ROOT)


def main():
    inputs = load(LAB / 'RUN-INPUTS.json')
    assert all(sha(LAB / p) == digest for p, digest in inputs.items())
    origins = load(LAB / 'ORIGINS.json')
    for p, digest in origins['preserved_files'].items():
        data = git('show', origins['runner_origin_commit'] + ':' + origins['runner_origin_directory'] + '/' + p)
        assert data == (LAB / p).read_bytes() and hashlib.sha256(data).hexdigest() == digest
    before_run = git('show', origins['runner_origin_commit'] + ':' + origins['runner_origin_directory'] + '/run.py').decode()
    expected = before_run.replace("assert mode in ['baseline', 'candidate'] and len(prior) == (mode == 'candidate')", "assert mode == 'baseline' and not prior, 'This capsule is baseline-only'")
    old = """        if mode == 'candidate':
            results['lint'] = process.run([PYTHON, './mach', 'lint', '--linter', 'wpt', 'testing/web-platform/tests/css/css-animations/KeyframeEffect-getKeyframes.tentative.html'], output / 'lint.log', env, 600)
            save(output / 'LINT.json', results['lint'])
            assert results['lint']['exit_code'] == 0, 'WPT lint failed'
"""
    new = """        results['lint'] = process.run([PYTHON, './mach', 'lint', '--linter', 'wpt', *plan['suites']], output / 'lint.log', env, 600)
        save(output / 'LINT.json', results['lint'])
        assert results['lint']['exit_code'] == 0, 'WPT lint failed'
        if mode == 'candidate':
"""
    assert old in expected
    assert expected.replace(old, new) == (LAB / 'run.py').read_text()
    assert load(LAB / 'SOURCE-ROLES.json') == {}
    directory = LAB / 'baseline1'
    receipt = load(directory / 'RESULT.json')
    plan = load(LAB / 'RUN-PLAN.json')
    assert receipt['error'] is None and receipt['restoration_verified'] and not receipt['restoration_errors']
    assert receipt['runner_inputs_sha256'] == sha(LAB / 'RUN-INPUTS.json')
    assert receipt['head'] == plan['head']
    assert receipt['commands']['lint']['exit_code'] == 0 and receipt['commands']['wpt']['exit_code'] == 1
    assert receipt['commands']['build']['skipped']
    active = set()
    records = {}
    suites = [0, 0]
    def unique(items):
        result = {}
        for k, v in items:
            assert k not in result
            result[k] = v
        return result
    for line in (directory / 'wpt-raw.jsonl').read_text().splitlines():
        r = json.loads(line, object_pairs_hook=unique)
        action = r.get('action')
        assert action != 'crash'
        assert not (action == 'log' and r.get('level') in ['ERROR', 'CRITICAL'])
        if action == 'suite_start':
            assert suites == [0, 0]
            suites[0] += 1
        elif action == 'test_start':
            assert suites == [1, 0] and not active
            active.add(r['test'])
        elif action in ['test_status', 'test_end']:
            assert r['test'] in active
            key = (action, r['test'], r.get('subtest'))
            assert key not in records
            records[key] = r
            if action == 'test_end':
                active.remove(r['test'])
        elif action == 'suite_end':
            assert suites == [1, 0] and not active
            suites[1] += 1
    assert suites == [1, 1] and len(records) == 3
    callbacks = [r for k, r in records.items() if k[0] == 'test_status']
    endings = [r for k, r in records.items() if k[0] == 'test_end']
    assert len(callbacks) == 2 and len(endings) == 1 and endings[0]['status'] == 'OK'
    assert {(r['test'], r['subtest']) for r in callbacks} == {tuple(x) for x in load(LAB / 'EXPECTED-CALLBACKS.json')}
    assert {r['subtest'].split(':')[0]: r['status'] for r in callbacks} == {'unique-groups': 'PASS', 'repeated-group': 'FAIL'}
    failure = next(r for r in callbacks if r['status'] == 'FAIL')
    assert 'Groups retain earliest source order' in failure['message']
    assert 'got ["linear", "ease-out", "ease-in"]' in failure['message']
    proposed = LAB / 'runtime-inputs/named-range-group-earliest-order.html'
    assert sha(proposed) == origins['proposal_sha256']
    text = proposed.read_text()
    assert text.index('Every group resolves') < text.index('The later declaration') < text.index('Groups retain earliest')
    assert "['repeated-group', '30px']" in text
    spec = importlib.util.spec_from_file_location('review_bundle', LAB / 'bundle.py')
    bundle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bundle)
    before = load(directory / 'BEFORE.json')
    assert bundle.semantic(bundle.scan(ROOT / 'objdir-full.noindex/dist/Nightly.app')) == bundle.semantic(before['app'])
    assert bundle.semantic({p: bundle.entry(ROOT / p) for p in before['extras']}) == bundle.semantic(before['extras'])
    retained = load(LAB / 'runtime-inputs/retained-build.json')
    assert receipt['sampled_binaries'] == retained['binaries']
    assert all(sha(ROOT / p) == digest for p, digest in retained['binaries'].items())
    pins = load(LAB / 'runtime-inputs/test-source-pins.json')
    for p, digest in pins.items():
        if digest is None:
            assert not (ROOT / p).exists() and not (ROOT / p).is_symlink()
        else:
            assert sha(ROOT / p) == digest
    for p in plan['fixtures']:
        for name in [p, p.replace('/tests/', '/meta/', 1) + '.ini']:
            assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
    assert sha(ROOT / 'mozconfig') == plan['mozconfig_sha256']
    assert git('rev-parse', 'HEAD').decode().strip() == plan['head']
    assert hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest() == before['index']
    assert not git('diff', '--name-only').strip() and not git('diff', '--cached', '--name-only').strip()
    assert not (directory / 'backups').exists() and not (LAB / 'runtime.lock').exists()
    processes = (HERE / 'process-snapshot.txt').read_text()
    alive = {int(x[0]) for line in processes.splitlines() if len(x := line.split()) == 3 and not x[1].startswith('Z')}
    pgids = []
    for f in directory.glob('*.process.json'):
        r = load(f)
        assert r['state'] == 'terminal' and r['group_absent'] and r['pgid'] not in alive
        pgids.append(r['pgid'])
    evidence = {str(p.relative_to(ROOT)): sha(p) for p in [*directory.glob('*.json'), *directory.glob('*.jsonl'), LAB/'RUN-INPUTS.json', proposed]}
    (HERE/'INPUTS.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps({'status': 'PASS', 'wrapper_diff_authenticated': True, 'native_roles_empty': True, 'callbacks': 2, 'harness': 1, 'unique_PASS_repeated_FAIL': True, 'finite_offset_and_late_winner_precede_failure': True, 'application_entries': len(before['app']), 'extras': len(before['extras']), 'test_source_pins': len(pins), 'head_index_clean_and_preserved': True, 'owned_process_groups_absent': pgids, 'fixtures_backups_lock_absent': True}, indent=2))


if __name__ == '__main__':
    main()
