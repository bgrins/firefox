import hashlib
import json
import os
from pathlib import Path
import stat
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CAP = ROOT / 'artifacts/css-clip-auto-runtime-20261110-v2'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    def pairs(items):
        result = {}
        for k, v in items:
            assert k not in result, ('duplicate key', k)
            result[k] = v
        return result
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def read_trace(path, flavor):
    events = [json.loads(line) for line in path.read_text().splitlines()]
    active, closed, rows, observations, messages = set(), set(), {}, {}, {}
    occurrences = Counter()
    suite = 0
    starts = ends = 0
    for event in events:
        action = event['action']
        assert action != 'crash'
        if action == 'suite_start':
            assert suite == 0 and starts == 0
            suite, starts = 1, 1
        elif action == 'suite_end':
            assert suite == 1 and not active
            suite, ends = 0, ends + 1
        elif action == 'test_start':
            test = event['test']
            assert suite == 1 and test not in active | closed
            active.add(test)
        elif action == 'test_status':
            test, name = event['test'], event['subtest']
            assert test in active
            key = (test, name)
            index = occurrences[key]
            if flavor == 'wpt':
                assert index == 0
            occurrences[key] += 1
            rows[(flavor, test, name, index, 'callback')] = event['status']
            if flavor == 'mochitest':
                messages[(test, index)] = event.get('message')
            if flavor == 'mochitest':
                assert event['status'] == event.get('expected', event['status'])
                assert event['status'] in ['PASS', 'FAIL']
        elif action == 'test_end':
            test = event['test']
            assert test in active
            active.remove(test)
            closed.add(test)
            assert event['status'] == ('OK' if flavor == 'wpt' else 'PASS')
            rows[(flavor, test, None, 0, 'harness')] = event['status']
        elif action == 'process_output' and 'CLIP_SMIL_OBSERVATION ' in event.get('data', ''):
            assert flavor == 'wpt'
            text = event['data']
            assert text.count('CLIP_SMIL_OBSERVATION ') == 1
            value = json.loads(text.split('CLIP_SMIL_OBSERVATION ', 1)[1])
            assert value['id'] not in observations
            observations[value['id']] = value
    assert starts == ends == 1 and not active and suite == 0
    assert len(closed) == (3 if flavor == 'wpt' else 4)
    logs = [e for e in events if e['action'] == 'log' and e.get('level') in ['ERROR', 'CRITICAL', 'WARNING']]
    return rows, observations, logs, messages


def main():
    assert (CAP / 'candidate1/RESULT.json').is_file(), 'candidate not complete'
    inputs = load(CAP / 'RUN-INPUTS.json')
    for name, expected in inputs.items():
        assert digest(CAP / name) == expected
    results, obs, issues, messages = {}, {}, {}, {}
    for mode in ['baseline1', 'candidate1']:
        result = load(CAP / mode / 'RESULT.json')
        assert result['error'] is None and result['restoration_verified'] and not result['restoration_errors']
        assert result['runner_inputs_sha256'] == digest(CAP / 'RUN-INPUTS.json')
        assert result['commands']['mochitest']['exit_code'] == 0
        assert result['commands']['wpt']['exit_code'] in [0, 1]
        for command in result['commands'].values():
            if not command.get('skipped'):
                assert command['group_absent']
        assert not (CAP / mode / 'backups').exists()
        assert all(load(CAP / mode / 'RESTORED.json')[k] for k in ['source_and_application_restored', 'index_preserved', 'temporary_fixtures_removed', 'backup_removed'])
        results[mode], obs[mode], issues[mode], messages[mode] = {}, {}, {}, {}
        for flavor in ['wpt', 'mochitest']:
            rows, observations, logs, labels = read_trace(CAP / mode / (flavor + '-raw.jsonl'), flavor)
            results[mode].update(rows)
            obs[mode].update(observations)
            issues[mode][flavor] = logs
            messages[mode].update(labels)
    baseline, candidate = results['baseline1'], results['candidate1']
    assert set(baseline) == set(candidate) and len(baseline) == len(candidate) == 5116
    assert len(messages['baseline1']) == 5061 and messages['baseline1'] == messages['candidate1']
    changes = [{'key': list(k), 'baseline': baseline[k], 'candidate': candidate[k]}
               for k in baseline if baseline[k] != candidate[k]]
    assert len(changes) == 4
    assert all(r['baseline'] == 'FAIL' and r['candidate'] == 'PASS' and r['key'][0] == 'wpt' for r in changes)
    assert {r['key'][2] for r in changes} == {
        'Iteration composition: matching auto components accumulate',
        'Effect composition add: matching auto components combine',
        'Effect composition accumulate: matching auto components combine',
        'iteration composition of incompatible clip rects (accumulation skipped at 0%, allowed at 50%)'}
    assert len(obs['baseline1']) == 12 and obs['baseline1'] == obs['candidate1']
    for value in obs['candidate1'].values():
        assert value['paused'] is True
    candidate_build = load(CAP / 'candidate1/BUILD.json')
    assert candidate_build['command_result']['exit_code'] == 0
    roles = load(CAP / 'SOURCE-ROLES.json')
    assert candidate_build['source_sha256'] == {p: r['candidate'] for p, r in roles.items()}
    assert candidate_build['binaries'] == load(CAP / 'candidate1/SAMPLED-BINARIES.json')
    assert candidate_build['binaries'] != load(CAP / 'baseline1/SAMPLED-BINARIES.json')
    for path, row in roles.items():
        assert digest(ROOT / path) == row['base']
    retained = load(CAP / 'runtime-inputs/retained-build.json')
    for path, expected in retained['binaries'].items():
        assert digest(ROOT / path) == expected
    for path, expected in load(CAP / 'runtime-inputs/test-source-pins.json').items():
        assert digest(ROOT / path) == expected
    plan = load(CAP / 'RUN-PLAN.json')
    assert digest(ROOT / 'mozconfig') == plan['mozconfig_sha256']
    for path in plan['fixtures']:
        assert not (ROOT / path).exists()
        assert not (ROOT / (path.replace('/tests/', '/meta/', 1) + '.ini')).exists()
    before = load(CAP / 'candidate1/BEFORE.json')
    app = ROOT / 'objdir-full.noindex/dist/Nightly.app'
    actual_paths = {'.'}
    for directory, dirs, files in os.walk(app, followlinks=False):
        actual_paths.update(str((Path(directory) / name).relative_to(app)) for name in dirs + files)
    assert actual_paths == set(before['app'])
    for path, row in list(before['app'].items()) + list(before['extras'].items()):
        target = (ROOT if path in before['extras'] else app) / path
        info = target.lstat()
        assert stat.S_IMODE(info.st_mode) == row['mode']
        if row['kind'] == 'file':
            assert stat.S_ISREG(info.st_mode) and info.st_size == row['size'] and digest(target) == row['sha256']
        elif row['kind'] == 'symlink':
            assert stat.S_ISLNK(info.st_mode) and os.readlink(target) == row['target']
        else:
            assert stat.S_ISDIR(info.st_mode)
    receipts = {}
    for mode in ['baseline1', 'candidate1']:
        for name in ['RESULT.json', 'BUILD.json', 'RESTORED.json', 'wpt-raw.jsonl', 'mochitest-raw.jsonl', 'wpt.log', 'mochitest.log']:
            receipts[mode + '/' + name] = digest(CAP / mode / name)
    report = {'status': 'pass', 'runtime_inputs_sha256': digest(CAP / 'RUN-INPUTS.json'),
              'rows_per_variant': len(baseline), 'changes': changes, 'svg_observations_unchanged': 12,
              'mochitest_message_inventory_unchanged': 5061,
              'author_comparison_masked_first_callbacks': 4,
              'restored_app_entries_verified': len(actual_paths), 'restored_extras_verified': len(before['extras']),
              'restored_source_files_verified': len(roles), 'raw_log_warnings_errors': issues,
              'receipts_sha256': receipts, 'debug_run': False, 'direct_count_zero_native_run': False}
    (HERE / 'CHECK.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: independent 5116-row comparison, four CSS improvements, twelve unchanged SVG observations, complete app/source restoration')


if __name__ == '__main__':
    main()
