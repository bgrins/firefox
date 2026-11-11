import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAP = ROOT / 'artifacts/css-pseudo-animation-snapshot-runtime-20261110-v1'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def unique(items):
    result = {}
    for k, v in items:
        assert k not in result, ('duplicate JSON key', k)
        result[k] = v
    return result


def load(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), '-c', 'core.fsmonitor=false', *args])


def parse(path, expected_pages):
    rows, active, ended, started = {}, set(), set(), set()
    suite = False
    suite_starts = suite_ends = 0
    warnings = []
    for text in path.read_text().splitlines():
        event = json.loads(text, object_pairs_hook=unique)
        action = event['action']
        assert action != 'crash'
        assert not (action == 'log' and event.get('level') in ['ERROR', 'CRITICAL'])
        if action == 'log' and event.get('level') == 'WARNING':
            warnings.append(event)
        if action == 'suite_start':
            assert not suite and suite_starts == 0
            suite, suite_starts = True, 1
        elif action == 'suite_end':
            assert suite and not active and started == ended
            suite, suite_ends = False, suite_ends + 1
        elif action == 'test_start':
            test = event['test']
            assert suite and test not in started
            started.add(test)
            active.add(test)
        elif action == 'test_status':
            test = event['test']
            assert test in active and event['status'] in ['PASS', 'FAIL']
            key = ('assertion', test, event['subtest'])
            assert key not in rows
            rows[key] = event['status']
        elif action == 'test_end':
            test = event['test']
            assert test in active and event['status'] == 'OK'
            active.remove(test)
            ended.add(test)
            key = ('harness', test, None)
            assert key not in rows
            rows[key] = event['status']
        elif action == 'assertion_count':
            assert event['min_expected'] <= event['count'] <= event['max_expected']
    assert not suite and not active and suite_starts == suite_ends == 1
    assert started == ended == expected_pages
    assert all(any(k[0] == 'assertion' and k[1] == page for k in rows) for page in expected_pages)
    return rows, warnings


def main():
    assert (CAP / 'candidate1/RESULT.json').is_file(), 'candidate not terminal'
    plan = load(CAP / 'RUN-PLAN.json')
    sources = load(CAP / 'RUN-INPUTS.json')
    for name, expected in sources.items():
        assert sha(CAP / name) == expected
    pages = {'/' + p.removeprefix('testing/web-platform/tests/') for p in plan['suites']}
    variants, warnings, pins, owned_groups = {}, {}, {}, set()
    for name in ['baseline1', 'candidate1']:
        result = load(CAP / name / 'RESULT.json')
        assert result['error'] is None and result['restoration_verified'] and not result['restoration_errors']
        assert result['head'] == plan['head'] and result['runner_inputs_sha256'] == sha(CAP / 'RUN-INPUTS.json')
        for command in result['commands'].values():
            if not command.get('skipped'):
                assert command['group_absent']
                owned_groups.add(command['pgid'])
        assert result['commands']['wpt']['exit_code'] in [0, 1]
        if name == 'candidate1':
            assert result['commands']['build']['exit_code'] == 0
            assert result['comparison']['identical_callback_statuses_and_inventory']
        restored = load(CAP / name / 'RESTORED.json')
        assert all(restored[k] for k in ['source_and_application_restored', 'index_preserved', 'temporary_fixtures_removed', 'backup_removed'])
        assert not (CAP / name / 'backups').exists()
        rows, warning = parse(CAP / name / 'wpt-raw.jsonl', pages)
        variants[name], warnings[name] = rows, warning
        assert len(rows) == 125 and Counter(rows.values()) == {'PASS': 94, 'FAIL': 20, 'OK': 11}
        saved = load(CAP / name / 'TEST-RESULTS.json')
        saved_rows = {(kind, row['test'], row.get('subtest')): row['status']
                      for kind, field in [('assertion', 'subtests'), ('harness', 'harness')]
                      for row in saved[field]}
        assert rows == saved_rows and len(rows) == len(saved['subtests']) + len(saved['harness'])
        for file in ['RESULT.json', 'BUILD.json', 'SAMPLED-BINARIES.json', 'BEFORE.json', 'RESTORED.json', 'wpt-raw.jsonl', 'wpt.log']:
            pins[name + '/' + file] = sha(CAP / name / file)
    assert variants['baseline1'] == variants['candidate1']
    process_rows = subprocess.check_output(['ps', '-axo', 'pgid=,stat=,pid='], text=True)
    survivors = [line for line in process_rows.splitlines()
                 if len(parts := line.split()) == 3 and int(parts[0]) in owned_groups
                 and not parts[1].startswith('Z')]
    assert not survivors, survivors
    assert not (CAP / 'runtime.lock').exists()
    coverage = {}
    for page in sorted(pages):
        coverage[page] = dict(Counter(v for k, v in variants['candidate1'].items() if k[0] == 'assertion' and k[1] == page))
    attr = '/css/css-animations/keyframe-attribute-mutation.html'
    assert coverage[attr] == {'PASS': 12}
    ranges = [v for p, v in coverage.items() if p.startswith('/scroll-animations/')]
    assert sum(v.get('PASS', 0) for v in ranges) == 6 and all(set(v) == {'PASS'} for v in ranges)
    roles = load(CAP / 'SOURCE-ROLES.json')
    build = load(CAP / 'candidate1/BUILD.json')
    assert build['source_sha256'] == {p: role['candidate'] for p, role in roles.items()}
    assert build['mozconfig_sha256'] == plan['mozconfig_sha256']
    assert build['binaries'] == load(CAP / 'candidate1/SAMPLED-BINARIES.json')
    for name, role in roles.items():
        assert sha(ROOT / name) == role['base']
    retained = load(CAP / 'runtime-inputs/retained-build.json')
    assert load(CAP / 'baseline1/SAMPLED-BINARIES.json') == retained['binaries']
    for name, expected in retained['binaries'].items():
        assert sha(ROOT / name) == expected
    for name, expected in load(CAP / 'runtime-inputs/test-source-pins.json').items():
        path = ROOT / name
        if expected is None:
            assert not path.exists() and not path.is_symlink()
        else:
            assert sha(path) == expected
    for name in plan['fixtures']:
        path = ROOT / name
        assert not path.exists() and not path.is_symlink()
    assert sha(ROOT / 'mozconfig') == plan['mozconfig_sha256']
    assert git('rev-parse', 'HEAD').decode().strip() == plan['head']
    assert not git('diff', '--name-only').strip() and not git('diff', '--cached', '--name-only').strip()
    before = load(CAP / 'candidate1/BEFORE.json')
    assert hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest() == before['index']
    app = ROOT / 'objdir-full.noindex/dist/Nightly.app'
    paths = {'.'}
    for directory, dirs, files in os.walk(app, followlinks=False):
        paths.update(str((Path(directory) / n).relative_to(app)) for n in dirs + files)
    assert paths == set(before['app'])
    for name, row in list(before['app'].items()) + list(before['extras'].items()):
        path = (ROOT if name in before['extras'] else app) / name
        info = path.lstat()
        assert stat.S_IMODE(info.st_mode) == row['mode']
        if row['kind'] == 'file':
            assert stat.S_ISREG(info.st_mode) and info.st_size == row['size'] and sha(path) == row['sha256']
        elif row['kind'] == 'symlink':
            assert stat.S_ISLNK(info.st_mode) and os.readlink(path) == row['target']
        else:
            assert stat.S_ISDIR(info.st_mode)
    report = {'status': 'pass', 'result_rows_per_variant': 125, 'subtests_per_variant': 114,
              'statuses_per_variant': dict(Counter(variants['candidate1'].values())),
              'per_page_subtest_statuses': coverage, 'raw_warnings': warnings,
              'source_files_restored': len(roles), 'app_entries_restored': len(paths),
              'extras_restored': len(before['extras']), 'head_and_index_restored': True,
              'owned_process_groups_absent': sorted(owned_groups), 'runtime_lock_removed': True,
              'retained_binary_samples_restored': True, 'test_metadata_and_config_restored': True,
              'candidate_samples_differ_from_baseline': build['binaries'] != retained['binaries'],
              'evidence_sha256': pins, 'browser_tests_run_by_reviewer': False,
              'missing_pseudo_debug_gate_closed': False}
    (HERE / 'RUNTIME-CHECK.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: 125 distinct rows preserved; attribute/range coverage; full application/extras/source/index restoration')


if __name__ == '__main__':
    main()
