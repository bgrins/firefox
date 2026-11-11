import copy
import difflib
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUTHOR = ROOT / 'artifacts/css-pseudo-animation-transient-recascade-runtime-20261110-v1'
PREVIOUS = ROOT / 'artifacts/css-pseudo-animation-query-runtime-20261110-v4'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    assert sha(AUTHOR / 'PREPARATION-FILES.json') == 'cde338c5827ec925c4c8eed44baec0527c76f13deb83ba4c717a64ae2cc07094'
    manifest = read(AUTHOR / 'PREPARATION-FILES.json')
    for name, expected in manifest.items():
        assert sha(AUTHOR / name) == expected, name
    origins = read(AUTHOR / 'ORIGINS.json')
    assert sha(PREVIOUS / 'RUN-INPUTS.json') == origins['runtime_manifest_sha256']
    for name, digest in read(PREVIOUS / 'RUN-INPUTS.json').items():
        assert sha(PREVIOUS / name) == digest, name
    plan = read(AUTHOR / 'RUN-PLAN.json')
    assert plan['head'] is None and plan['retained_build_origin'] is None
    assert not (AUTHOR / 'FREEZE-READY.json').exists() and not (AUTHOR / 'RUN-INPUTS.json').exists()
    old_run = (PREVIOUS / 'run.py').read_text()
    new_run = (AUTHOR / 'run.py').read_text()
    diff = ''.join(difflib.unified_diff(old_run.splitlines(keepends=True), new_run.splitlines(keepends=True),
        fromfile='query-v4/run.py', tofile='recascade-v1/run.py'))
    assert diff == (AUTHOR / 'RUN-DIFF.patch').read_text()
    assert old_run[old_run.index('def restore('):] == new_run[new_run.index('def restore('):]
    for name in ['bundle.py', 'process.py', 'analyze.py', 'driver-analyze.py', 'freeze.py',
                 'EXPECTED-BASELINE.json', 'EXPECTED-CALLBACKS.json', 'EXPECTED-CHANGES.json',
                 'DRIVER-ASSERTIONS.json']:
        assert (AUTHOR / name).read_bytes() == (PREVIOUS / name).read_bytes(), name
    before_plan = read(PREVIOUS / 'RUN-PLAN.json')
    assert plan['suites'] == before_plan['suites'] and plan['lint_paths'] == before_plan['lint_paths']
    baseline = read(AUTHOR / 'EXPECTED-BASELINE.json')
    assert baseline['subtest_count'] == 118 and baseline['test_count'] == 12
    assert read(AUTHOR / 'EXPECTED-CHANGES.json') == []
    assert read(AUTHOR / 'DRIVER-ASSERTIONS.json')['assertion_count'] == 208
    inventory = read(AUTHOR / 'RECASCADE-ASSERTIONS.json')
    html = (AUTHOR / 'runtime-inputs/test_missing_pseudo_animation_recascade.html').read_text()
    chunks = re.split(r'add_task\(async function ([a-z_]+)\(\) \{', html)
    derived = []
    for task, body in zip(chunks[1::2], chunks[2::2]):
        assertions = []
        for line in body.splitlines():
            if re.match(r'\s*accepted\(', line):
                label = re.fullmatch(r'\s*accepted\(result, "([^"]+)"\);', line)[1]
                for suffix in ['admitted', 'exact pseudo identity', 'origin style not replaced', 'no generated pseudo created']:
                    assertions.append(dict(name=label + ': ' + suffix, classification='diagnostic'))
            elif re.match(r'\s*(is|ok)\(', line):
                label = re.search(r', "([^"\\]+)"\);$', line)[1]
                assertions.append(dict(name=label, classification='setup' if label.startswith('Setup: ') else 'result'))
        derived.append(dict(name=task, assertions=assertions))
    assert inventory == dict(assertion_count=100, tasks=derived)
    assert sum(a['classification'] == 'setup' for task in derived for a in task['assertions']) == 6
    roles = read(AUTHOR / 'SOURCE-ROLES.json')
    objects = [(origins['source_test_pin_revision'], name, role['base']) for name, role in roles.items()]
    objects += [(origins['signed_origin'], name, digest) for name, digest in origins['authenticated_files'].items()]
    for revision, name, digest in objects:
        raw = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', '-C', str(ROOT), 'show', revision + ':' + name])
        assert hashlib.sha256(raw).hexdigest() == digest, name
    parser = runpy.run_path(str(AUTHOR / 'recascade-analyze.py'))['parse']
    assertions = [a for task in inventory['tasks'] for a in task['assertions']]
    rows = [{'action': 'suite_start'}, {'action': 'test_start', 'test': plan['recascade_test']}]
    rows += [dict(action='test_status', test=plan['recascade_test'], status='PASS', subtest=None, message=a['name']) for a in assertions]
    rows += [dict(action='test_end', test=plan['recascade_test'], status='PASS'), {'action': 'suite_end'}]
    controls = {}
    bundle = runpy.run_path(str(AUTHOR / 'bundle.py'))
    with tempfile.TemporaryDirectory(prefix='recascade-independent-review-') as directory:
        temp = Path(directory)
        raw = temp / 'raw.jsonl'
        def parse(value):
            raw.write_text(''.join(json.dumps(row) + '\n' for row in value))
            return parser(raw)
        assert parse(rows)['gate_passed']
        for index, assertion in enumerate(assertions):
            if assertion['classification'] != 'setup':
                continue
            altered = copy.deepcopy(rows)
            altered[index + 2]['status'] = 'FAIL'
            altered[index + 2]['message'] += ' - wrong setup'
            result = parse(altered)
            assert not result['gate_passed'] and any(not task['setup_gates_passed'] for task in result['tasks'])
            controls[assertion['name']] = 'setup failure separately classified'
        for label in ['query-suite-substitution', 'post-suite-callback', 'wrong-result-classification']:
            altered = copy.deepcopy(rows)
            if label == 'query-suite-substitution':
                for row in altered:
                    if 'test' in row:
                        row['test'] = plan['driver_test']
            elif label == 'post-suite-callback':
                altered.append(copy.deepcopy(altered[2]))
            else:
                index = next(i+2 for i, a in enumerate(assertions) if a['classification'] == 'result')
                altered[index]['status'] = 'FAIL'
            try:
                result = parse(altered)
            except (AssertionError, ValueError, TypeError, KeyError):
                controls[label] = 'rejected'
            else:
                assert not result['gate_passed']
                if label == 'wrong-result-classification':
                    assert all(task['setup_gates_passed'] for task in result['tasks'])
                controls[label] = 'rejected without blaming setup'
        tree = temp / 'tree'; tree.mkdir()
        target = tree / 'file'; target.write_text('original'); target.chmod(0o640)
        (tree / 'link').symlink_to('file')
        before = bundle['scan'](tree)
        mapping = bundle['backup'](tree, before, temp / 'backup')
        target.write_text('candidate'); target.chmod(0o600)
        post = bundle['scan'](tree)
        target.write_text('concurrent owner change')
        try:
            bundle['restore'](tree, before, post, temp / 'backup', mapping)
        except AssertionError:
            assert target.read_text() == 'concurrent owner change'
            controls['concurrent-restoration-edit'] = 'refused; new contents preserved'
        else:
            raise AssertionError('Concurrent change overwritten')
        bundle['restore'](tree, before, bundle['scan'](tree), temp / 'backup', mapping)
        assert bundle['semantic'](bundle['scan'](tree)) == bundle['semantic'](before)
    for name, digest in manifest.items():
        assert sha(AUTHOR / name) == digest, name
    (HERE / 'CHECK.json').write_text(json.dumps(dict(status='PASS', preparation_manifest_sha256=sha(AUTHOR / 'PREPARATION-FILES.json'),
        authenticated_files=len(manifest), independently_authenticated_git_objects=len(objects),
        source_assertions_reconstructed=100, setup_assertions=6, query_assertions=208, ordinary_records=130,
        controls=controls, exact_runner_delta=True, restoration_body_unchanged=True,
        live_source_or_native_execution=False), indent=2) + '\n')


if __name__ == '__main__':
    main()
