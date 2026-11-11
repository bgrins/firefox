import argparse
import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def git_file(revision, name):
    return subprocess.run(['git', '-c', 'core.fsmonitor=false', 'show', revision + ':' + name], cwd=ROOT, capture_output=True)


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def input_names():
    names = ['run.py', 'analyze.py', 'bundle.py', 'process.py', 'check.py', 'freeze.py', 'derive.py', 'parser-controls.py', 'RUN-PLAN.json', 'SOURCE-ROLES.json', 'EXPECTED-BASELINE.json', 'EXPECTED-CALLBACKS.json', 'EXPECTED-CHANGES.json', 'EXPECTED-CANDIDATE.json', 'EXPECTED-DERIVATION.json', 'ORIGINS.json', 'candidate.patch']
    for directory in ['source', 'candidate', 'runtime-inputs']:
        names += [str(p.relative_to(HERE)) for p in sorted((HERE / directory).rglob('*')) if p.is_file()]
    assert len(names) == len(set(names))
    return sorted(names)


def artifact_bridge(left, right):
    changed = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'diff', '--name-only', left, right], cwd=ROOT, text=True).splitlines()
    assert all(name.startswith('artifacts/') for name in changed), changed
    return len(changed)


def validate_retained(retained, head, plan, origins, roles):
    assert retained['status'] == 'pass' and retained['build_exit'] == 0
    assert retained['final_wpt_pending'] is False
    assert retained['mozconfig_sha256'] == plan['mozconfig_sha256']
    assert retained['tracked_tree_clean'] is True
    assert isinstance(retained['sources'], dict) and retained['sources']
    assert set(retained['binaries']) == {
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
        'objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini'}
    artifact_bridge(origins['source_test_pin_revision'], retained['head'])
    artifact_bridge(retained['head'], head)
    for name, digest in retained['sources'].items():
        result = git_file(retained['head'], name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest, name
    for name, role in roles.items():
        result = git_file(retained['head'], name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == role['base'], name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frozen', action='store_true')
    args = parser.parse_args()
    origins = load(HERE / 'ORIGINS.json')
    plan = load(HERE / 'RUN-PLAN.json')
    roles = load(HERE / 'SOURCE-ROLES.json')
    for name, digest in origins['authenticated_files'].items():
        result = git_file(origins['signed_origin'], name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
        assert sha(ROOT / name) == digest, name
    for name, digest in origins['frozen_files'].items():
        assert sha(ROOT / name) == digest, name
    predecessor = ROOT / origins['wrapper_origin']
    for name in ['bundle.py', 'process.py', 'freeze.py']:
        assert (HERE / name).read_bytes() == (predecessor / name).read_bytes()
    runner = (HERE / 'run.py').read_text()
    assert runner.count('comparison = analyze.compare(baseline, parsed, improvements=True)') == 1
    assert runner.replace('comparison = analyze.compare(baseline, parsed, improvements=True)',
        'comparison = analyze.compare(baseline, parsed)') == (predecessor / 'run.py').read_text()
    assert (HERE / 'analyze.py').read_text().split('def compare(')[0] == (predecessor / 'analyze.py').read_text().split('def compare(')[0]
    for p in HERE.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
    old_plan = load(predecessor / 'RUN-PLAN.json')
    branch_test = 'testing/web-platform/tests/css/css-animations/getkeyframes-specified-branch.html'
    assert plan['suites'] == old_plan['suites'] + [branch_test]
    assert len(plan['suites']) == len(set(plan['suites'])) == 13
    assert len(plan['fixtures']) == 3 and plan['lint_paths'] == list(plan['fixtures'])
    assert set(roles) == {'dom/animation/KeyframeEffect.cpp'} and all(r['install_both'] is False for r in roles.values())
    author = ROOT / origins['candidate_origin']
    assert sha(HERE / 'candidate.patch') == origins['candidate_patch_sha256'] == sha(author / 'candidate.patch')
    for name, role in roles.items():
        result = git_file(origins['source_test_pin_revision'], name)
        assert result.returncode == 0 and result.stdout == (HERE / 'source' / name).read_bytes()
        assert sha(HERE / 'source' / name) == role['base']
        assert (HERE / 'candidate' / name).read_bytes() == (author / 'candidate' / name).read_bytes()
        assert sha(HERE / 'candidate' / name) == role['candidate']
    with tempfile.TemporaryDirectory(prefix='getter-branch-runtime-check-') as directory:
        scratch = Path(directory)
        for name in roles:
            destination = scratch / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / 'source' / name, destination)
        for reverse, expected in [(False, 'candidate'), (True, 'source')]:
            command = ['patch', '--batch', '-p1', '-i', str(HERE / 'candidate.patch')]
            if reverse:
                command.append('-R')
            subprocess.run(command, cwd=scratch, check=True, capture_output=True)
            assert all((scratch / name).read_bytes() == (HERE / expected / name).read_bytes() for name in roles)
    pins = load(HERE / 'runtime-inputs/test-source-pins.json')
    for name, digest in pins.items():
        result = git_file(origins['source_test_pin_revision'], name)
        if digest is None:
            assert result.returncode != 0
        else:
            assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
    for name, fixture in plan['fixtures'].items():
        assert pins[name] is None and pins[name.replace('/tests/', '/meta/', 1) + '.ini'] is None
        original = author / 'tests' / fixture if name == branch_test else predecessor / 'runtime-inputs' / fixture
        assert (HERE / 'runtime-inputs' / fixture).read_bytes() == original.read_bytes()
    tracked_range = 'testing/web-platform/tests/scroll-animations/css/named-range-group-earliest-order.html'
    assert pins[tracked_range] is not None and tracked_range not in plan['fixtures']
    base, evidence = module('derive').derive()
    assert base == load(HERE / 'EXPECTED-BASELINE.json')
    assert evidence == load(HERE / 'EXPECTED-DERIVATION.json')
    a = module('analyze')
    assert len(a.rows(base)) == 135
    assert Counter(r['status'] for r in base['subtests']) == {'PASS': 100, 'FAIL': 22}
    assert len(base['harness']) == 13 and all(r['status'] == 'OK' for r in base['harness'])
    callbacks = load(HERE / 'EXPECTED-CALLBACKS.json')
    assert callbacks == sorted([[r['test'], r['subtest']] for r in base['subtests']], key=repr)
    assert len(callbacks) == 122 and len(set(map(tuple, callbacks))) == 122
    changes = load(HERE / 'EXPECTED-CHANGES.json')
    assert len(changes) == 3 and all(r['kind'] == 'assertion' and r['test'] == '/css/css-animations/getkeyframes-specified-branch.html' and r['baseline'] == 'FAIL' and r['candidate'] == 'PASS' for r in changes)
    predicted = load(HERE / 'EXPECTED-CANDIDATE.json')
    assert (predicted, changes) == module('derive').prediction(base)
    assert Counter(r['status'] for r in predicted['subtests']) == {'PASS': 103, 'FAIL': 19}
    assert a.compare(base, base)['accepted_changes_only']
    assert a.compare(base, predicted, improvements=True)['accepted_changes_only']
    assert not a.compare(base, base, improvements=True)['accepted_changes_only']
    assert not a.compare(base, predicted)['accepted_changes_only']
    for suffix, counts in [('keyframe-attribute-mutation.html', {'PASS': 12}), ('KeyframeEffect-getKeyframes.tentative.html', {'PASS': 31, 'FAIL': 2}), ('named-range-group-earliest-order.html', {'PASS': 3}), ('pseudo-compose-cssom-lifetime.html', {'PASS': 13, 'FAIL': 7}), ('pseudo-compose-underlying.html', {'PASS': 6, 'FAIL': 3})]:
        assert Counter(r['status'] for r in base['subtests'] if r['test'].endswith('/' + suffix)) == counts, suffix
    controls = json.loads(subprocess.check_output([sys.executable, '-I', str(HERE / 'parser-controls.py')]))
    assert controls['status'] == 'pass' and len(controls['rejected_controls']) == 41
    if args.frozen:
        assert isinstance(plan['head'], str) and len(plan['head']) == 40
        assert plan['retained_build_origin'] and plan['retained_build_sha256']
        retained_path = HERE / 'runtime-inputs/retained-build.json'
        assert sha(retained_path) == plan['retained_build_sha256'] == sha(ROOT / plan['retained_build_origin'])
        validate_retained(load(retained_path), plan['head'], plan, origins, roles)
        manifest = load(HERE / 'RUN-INPUTS.json')
        assert set(manifest) == set(input_names())
        assert all(sha(HERE / name) == digest for name, digest in manifest.items())
    else:
        assert plan['head'] is None and plan['retained_build_origin'] is None and plan['retained_build_sha256'] is None
        assert not (HERE / 'runtime-inputs/retained-build.json').exists()
        assert not (HERE / 'RUN-INPUTS.json').exists() and not (HERE / 'FREEZE-READY.json').exists()
    print(json.dumps({'status': 'PASS', 'frozen': args.frozen, 'execution_head': plan['head'], 'native_roles': len(roles), 'temporary_fixtures': 3, 'tracked_named_range_test': True, 'test_source_metadata_pins': len(pins), 'signed_origin_files': len(origins['authenticated_files']), 'frozen_evidence_candidate_files': len(origins['frozen_files']), 'records': 135, 'baseline_callbacks': {'PASS': 100, 'FAIL': 22}, 'predicted_candidate_callbacks': {'PASS': 103, 'FAIL': 19}, 'harness_OK': 13, 'exact_improvements': 3, 'parser_rejection_controls': 41, 'native_browser_execution': False}, indent=2))


if __name__ == '__main__':
    main()
