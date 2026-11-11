import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def git_file(revision, name):
    return subprocess.run(['git', '-c', 'core.fsmonitor=false', 'show', revision + ':' + name], cwd=ROOT, capture_output=True)


def input_names():
    names = ['run.py', 'analyze.py', 'observe.py', 'bundle.py', 'process.py', 'check.py', 'freeze.py', 'prepare.py', 'parser-controls.py', 'RUN-PLAN.json', 'SOURCE-ROLES.json', 'EXPECTED-BASELINE.json', 'EXPECTED-CALLBACKS.json', 'EXPECTED-CHANGES.json', 'OBSERVATION-SCHEMA.json', 'ORIGINS.json', 'ORDINARY-CONTROL-PINS.json']
    names += [str(p.relative_to(HERE)) for p in sorted((HERE / 'runtime-inputs').rglob('*')) if p.is_file()]
    names += [str(p.relative_to(HERE)) for p in sorted((HERE / 'source-evidence').rglob('*')) if p.is_file()]
    assert len(names) == len(set(names))
    return sorted(names)


def artifact_bridge(left, right):
    names = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'diff', '--name-only', left, right], cwd=ROOT, text=True).splitlines()
    assert all(name.startswith('artifacts/') for name in names), names


def validate_retained(retained, head, plan, origins, roles):
    assert roles == {}
    assert retained['status'] == 'pass' and retained['build_exit'] == 0
    assert retained['final_wpt_pending'] is False and retained['tracked_tree_clean'] is True
    assert retained['mozconfig_sha256'] == plan['mozconfig_sha256']
    assert set(retained['binaries']) == {'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox', 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL', 'objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini'}
    assert len(retained['sources']) == 7
    artifact_bridge(origins['source_test_pin_revision'], retained['head'])
    artifact_bridge(retained['head'], head)
    for name, digest in retained['sources'].items():
        for rev in [retained['head'], head]:
            result = git_file(rev, name)
            assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest, name


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    parser = argparse.ArgumentParser()
    parser.add_argument('--frozen', action='store_true')
    args = parser.parse_args()
    evidence = load(HERE / 'ORDINARY-CONTROL-PINS.json')
    for name, digest in evidence['sources'].items():
        result = git_file(evidence['revision'], name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
        assert sha(HERE / 'source-evidence' / name) == digest
    origins = load(HERE / 'ORIGINS.json')
    plan = load(HERE / 'RUN-PLAN.json')
    roles = load(HERE / 'SOURCE-ROLES.json')
    assert roles == {} and load(HERE / 'EXPECTED-CHANGES.json') == []
    for name, digest in origins['origin_hashes'].items():
        result = git_file(origins['signed_origin'], origins['origin_directory'] + '/' + name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
        if name != 'run.py':
            assert (HERE / name).read_bytes() == result.stdout, name
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    run = (HERE / 'run.py').read_text()
    assert "assert mode == 'baseline' and not prior" in run
    assert "'build', 'binaries'" not in run and "mode == 'candidate'" not in run
    assert len(plan['suites']) == len(plan['fixtures']) == 1
    assert plan['suites'] == plan['lint_paths'] == list(plan['fixtures'])
    fixture = HERE / 'runtime-inputs' / next(iter(plan['fixtures'].values()))
    assert sha(fixture) == origins['runtime_fixture_sha256']
    assert sha(ROOT / origins['proposal_origin']) == origins['proposal_sha256']
    pins = load(HERE / 'runtime-inputs/test-source-pins.json')
    for name, digest in pins.items():
        result = git_file(origins['source_test_pin_revision'], name)
        assert result.returncode != 0 if digest is None else result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest, name
    for name in plan['fixtures']:
        assert pins[name] is None and pins[name.replace('/tests/', '/meta/', 1) + '.ini'] is None
    expected = load(HERE / 'EXPECTED-BASELINE.json')
    assert len(expected['subtests']) == 7 and all(r['status'] == 'PASS' for r in expected['subtests'])
    assert len(expected['harness']) == 1 and expected['harness'][0]['status'] == 'OK'
    assert load(HERE / 'EXPECTED-CALLBACKS.json') == [[r['test'], r['subtest']] for r in expected['subtests']]
    schema = load(HERE / 'OBSERVATION-SCHEMA.json')
    assert len(set(schema['ids'])) == 6 and schema['phases'] == ['created', 'quarter', 'three-quarters'] and schema['records'] == 18
    assert len(set(schema['style_properties'])) == 10 and 'margin-left' in schema['style_properties']
    controls = json.loads(subprocess.check_output([sys.executable, '-I', str(HERE / 'parser-controls.py')]))
    assert controls['status'] == 'PASS' and len(controls['rejected_controls']) >= 35
    retained_path = HERE / 'runtime-inputs/retained-build.json'
    assert sha(retained_path) == origins['retained_build_sha256']
    if args.frozen:
        assert isinstance(plan['head'], str) and len(plan['head']) == 40
        assert sha(retained_path) == plan['retained_build_sha256'] == sha(ROOT / plan['retained_build_origin'])
        validate_retained(load(retained_path), plan['head'], plan, origins, roles)
        manifest = load(HERE / 'RUN-INPUTS.json')
        assert set(manifest) == set(input_names())
        assert all(sha(HERE / name) == digest for name, digest in manifest.items())
    else:
        assert plan['head'] is None
        assert not (HERE / 'RUN-INPUTS.json').exists() and not (HERE / 'FREEZE-READY.json').exists()
        validate_retained(load(retained_path), origins['source_test_pin_revision'], plan, origins, roles)
    print(json.dumps({'status': 'PASS', 'frozen': args.frozen, 'execution_head': plan['head'], 'native_roles': 0, 'temporary_fixtures': 1, 'test_source_metadata_pins': len(pins), 'callbacks_PASS': 7, 'harness_OK': 1, 'observations': 18, 'style_fields': 10, 'parser_rejection_controls': len(controls['rejected_controls']), 'native_browser_execution': False}, indent=2))


if __name__ == '__main__':
    main()
