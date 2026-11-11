import argparse
import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def git_file(revision, name):
    return subprocess.run(['git', '-c', 'core.fsmonitor=false', 'show', revision + ':' + name], cwd=ROOT, capture_output=True)


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


PREF_SETUP = 'add_setup(async function enable_animation_preferences() {\n  await SpecialPowers.pushPrefEnv({\n    set: [\n      ["layout.css.scroll-driven-animations.enabled", true],\n      ["layout.css.typed-om.enabled", true],\n    ],\n  });\n  const style = document.querySelector("style");\n  const text = style.textContent;\n  style.textContent = text;\n});\n\n'

def amended_test(original):
    marker = 'add_task(async function explicit_endpoints_and_retarget() {'
    assert original.count(marker) == 1 and "add_setup(" not in original
    return original.replace(marker, PREF_SETUP + marker)


def validate_preferences(manifest, original_manifest, fixture, original_fixture):
    assert manifest['test_missing_pseudo_animation_query.html'] == {}
    assert {k: v for k, v in manifest.items() if k != 'test_missing_pseudo_animation_query.html'} == {k: v for k, v in original_manifest.items() if k != 'test_missing_pseudo_animation_query.html'}
    assert fixture == amended_test(original_fixture)


def input_names():
    names = ['run.py', 'analyze.py', 'driver-analyze.py', 'driver-controls.py',
             'bundle.py', 'process.py', 'check.py', 'freeze.py', 'parser-controls.py',
             'RUN-PLAN.json', 'SOURCE-ROLES.json', 'EXPECTED-BASELINE.json',
             'EXPECTED-CALLBACKS.json', 'EXPECTED-CHANGES.json', 'DRIVER-ASSERTIONS.json',
             'ORIGINS.json', 'query.patch', 'driver.patch', 'manifest-order.patch', 'pref-setup.patch', 'compile-fixes.patch', 'COMPILE-AMENDMENT.json']
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
    assert retained['final_wpt_pending'] is False and retained['tracked_tree_clean'] is True
    assert retained['mozconfig_sha256'] == plan['mozconfig_sha256']
    assert set(retained['binaries']) == {
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
        'objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini'}
    artifact_bridge(retained['head'], origins['source_test_pin_revision'])
    artifact_bridge(origins['source_test_pin_revision'], head)
    for name, digest in retained['sources'].items():
        result = git_file(retained['head'], name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
    for name, role in roles.items():
        result = git_file(retained['head'], name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == role['base'], name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frozen', action='store_true')
    args = parser.parse_args()
    origins, plan, roles = [load(HERE / n) for n in ['ORIGINS.json', 'RUN-PLAN.json', 'SOURCE-ROLES.json']]
    for name, digest in origins['authenticated_files'].items():
        result = git_file(origins['signed_origin'], name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
        assert sha(ROOT / name) == digest
    for name, digest in origins['reviewed_frozen_candidate_files'].items():
        assert sha(ROOT / name) == digest
    previous = ROOT / origins['runtime_v1_origin']
    for name, digest in origins['runtime_v1_files'].items():
        assert sha(previous / name) == digest
    previous_v2 = ROOT / origins['runtime_v2_origin']
    assert sha(previous_v2 / 'RUN-INPUTS.json') == origins['runtime_v2_input_manifest_sha256']
    for name, digest in origins['runtime_v2_files'].items():
        assert sha(previous_v2 / name) == digest
    amendments = load(HERE / 'COMPILE-AMENDMENT.json')['replacements']
    assert set(amendments) == {'dom/base/nsDOMWindowUtils.cpp', 'dom/animation/Animation.cpp'}
    for name, pairs in amendments.items():
        expected = (previous_v2 / 'candidate' / name).read_text()
        for old_text, new_text in pairs:
            assert expected.count(old_text) == 1
            expected = expected.replace(old_text, new_text)
        assert expected == (HERE / 'candidate' / name).read_text()
    old = ROOT / origins['wrapper_origin']
    driver = ROOT / origins['driver_origin']
    query = ROOT / origins['query_origin']
    for name in ['bundle.py', 'process.py', 'analyze.py', 'parser-controls.py', 'EXPECTED-BASELINE.json', 'EXPECTED-CALLBACKS.json', 'EXPECTED-CHANGES.json']:
        assert (HERE / name).read_bytes() == (old / name).read_bytes()
    assert (HERE / 'query.patch').read_bytes() == (query / 'candidate.patch').read_bytes()
    assert (HERE / 'driver.patch').read_bytes() == (driver / 'generated/driver.patch').read_bytes()
    assert (HERE / 'DRIVER-ASSERTIONS.json').read_bytes() == (driver / 'ASSERTIONS.json').read_bytes()
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    assert len(roles) == 11 and all(r['install_both'] is False for r in roles.values())
    assert len(plan['suites']) == len(set(plan['suites'])) == 12
    assert len(plan['fixtures']) == 3 and plan['candidate_only_fixtures'] == [plan['driver_test']]
    assert plan['lint_paths'] == [p for p in plan['fixtures'] if p.startswith('testing/web-platform/tests/')]
    for name, role in roles.items():
        result = git_file(origins['source_test_pin_revision'], name)
        assert result.returncode == 0 and result.stdout == (HERE / 'source' / name).read_bytes()
        assert sha(HERE / 'source' / name) == role['base']
        assert sha(HERE / 'candidate' / name) == role['candidate']
        if name != plan['driver_manifest'] and name not in amendments:
            assert (HERE / 'candidate' / name).read_bytes() == (driver / 'generated/candidate' / name).read_bytes()
    with tempfile.TemporaryDirectory(prefix='pseudo-query-runtime-check-') as directory:
        scratch = Path(directory) / 'sources'
        shutil.copytree(HERE / 'source', scratch)
        for name in ['query.patch', 'driver.patch', 'manifest-order.patch', 'pref-setup.patch', 'compile-fixes.patch']:
            subprocess.run(['patch', '--batch', '-p1', '-i', str(HERE / name)], cwd=scratch, check=True, capture_output=True)
        assert all((scratch / name).read_bytes() == (HERE / 'candidate' / name).read_bytes() for name in roles)
        assert (scratch / plan['driver_test']).read_bytes() == (HERE / 'runtime-inputs' / plan['fixtures'][plan['driver_test']]).read_bytes()
        for name in ['compile-fixes.patch', 'pref-setup.patch', 'manifest-order.patch', 'driver.patch', 'query.patch']:
            subprocess.run(['patch', '-R', '--batch', '-p1', '-i', str(HERE / name)], cwd=scratch, check=True, capture_output=True)
        assert all((scratch / name).read_bytes() == (HERE / 'source' / name).read_bytes() for name in roles)
        assert not (scratch / plan['driver_test']).exists()
        b = module('bundle')
        tree = Path(directory) / 'test-tree'
        tree.mkdir()
        (tree / 'original').write_text('before')
        (tree / 'link').symlink_to('original')
        before = b.scan(tree)
        mapping = b.backup(tree, before, Path(directory) / 'backup')
        (tree / 'original').write_text('candidate')
        (tree / 'new').write_text('temporary fixture')
        (tree / 'link').unlink()
        (tree / 'link').symlink_to('new')
        b.restore(tree, before, b.scan(tree), Path(directory) / 'backup', mapping)
        assert b.semantic(b.scan(tree)) == b.semantic(before)
    pins = load(HERE / 'runtime-inputs/test-source-pins.json')
    for name, digest in pins.items():
        result = git_file(origins['source_test_pin_revision'], name)
        assert result.returncode != 0 if digest is None else result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
    for name, filename in plan['fixtures'].items():
        assert pins[name] is None
        origin = driver / 'test.html' if name == plan['driver_test'] else old / 'runtime-inputs' / filename
        assert (HERE / 'runtime-inputs' / filename).read_bytes() == (amended_test(origin.read_text()).encode() if name == plan['driver_test'] else origin.read_bytes())
    manifest = tomllib.loads((HERE / 'candidate' / plan['driver_manifest']).read_text())
    names = [n for n in manifest if n != 'DEFAULT']
    sort_origin = origins['manifest_sort_source']
    sort_source = HERE / 'runtime-inputs/manifest-sort.py'
    assert sha(sort_source) == sort_origin['sha256']
    assert git_file(sort_origin['revision'], sort_origin['path']).stdout == sort_source.read_bytes()
    nodes = [node for node in ast.parse(sort_source.read_text()).body
             if isinstance(node, ast.FunctionDef) and node.name in ['sort_paths_keyfn', 'sort_paths']
             or isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in ['FILENAME_REGEX', 'DEFAULT_SECTION'] for target in node.targets)]
    namespace = {'re': re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(sort_source), 'exec'), namespace)
    assert names == namespace['sort_paths'](names), 'manifest section ordering'
    old_manifest = tomllib.loads((driver / 'generated/candidate' / plan['driver_manifest']).read_text())
    original_test = (driver / 'test.html').read_text()
    fixture = (HERE / 'runtime-inputs' / plan['fixtures'][plan['driver_test']]).read_text()
    validate_preferences(manifest, old_manifest, fixture, original_test)
    preference_controls = []
    for label, changed in [
        ('missing-await', fixture.replace('await SpecialPowers.pushPrefEnv', 'SpecialPowers.pushPrefEnv')),
        ('wrong-pref-value', fixture.replace('["layout.css.typed-om.enabled", true]', '["layout.css.typed-om.enabled", false]')),
        ('missing-reparse', fixture.replace('  style.textContent = text;\n', '')),
        ('changed-assertion', fixture.replace('Explicit half sample', 'Changed sample')),
    ]:
        try:
            validate_preferences(manifest, old_manifest, changed, original_test)
        except AssertionError:
            preference_controls.append(label)
        else:
            raise AssertionError(label + ' accepted')
    for label, changed in [('global-pref', json.loads(json.dumps(manifest))), ('per-test-pref', json.loads(json.dumps(manifest)))]:
        changed['DEFAULT' if label == 'global-pref' else 'test_missing_pseudo_animation_query.html']['prefs'] = ['layout.css.typed-om.enabled=true']
        try:
            validate_preferences(changed, old_manifest, fixture, original_test)
        except AssertionError:
            preference_controls.append(label)
        else:
            raise AssertionError(label + ' accepted')
    assert len(preference_controls) == 6
    a = module('analyze')
    base = load(HERE / 'EXPECTED-BASELINE.json')
    actual = load(old / 'candidate1/TEST-RESULTS.json')
    receipt = load(old / 'candidate1/RESULT.json')
    assert receipt['error'] is None and receipt['restoration_verified']
    assert a.compare(base, actual)['accepted_changes_only']
    assert len(a.rows(base)) == 130 and len(base['harness']) == 12
    assert Counter(r['status'] for r in base['subtests']) == {'PASS': 99, 'FAIL': 19}
    controls = json.loads(subprocess.check_output([sys.executable, '-I', str(HERE / 'parser-controls.py')]))
    assert controls['status'] == 'pass' and len(controls['rejected_controls']) == 30
    direct = json.loads(subprocess.check_output([sys.executable, '-I', '-B', str(HERE / 'driver-controls.py')]))
    assert direct['status'] == 'PASS' and len(direct['rejected_controls']) == 23
    if args.frozen:
        retained_path = HERE / 'runtime-inputs/retained-build.json'
        assert sha(retained_path) == plan['retained_build_sha256'] == sha(ROOT / plan['retained_build_origin'])
        validate_retained(load(retained_path), plan['head'], plan, origins, roles)
        manifest = load(HERE / 'RUN-INPUTS.json')
        assert set(manifest) == set(input_names()) and all(sha(HERE / n) == h for n, h in manifest.items())
    else:
        assert plan['head'] is None and plan['retained_build_origin'] is None and plan['retained_build_sha256'] is None
        assert not (HERE / 'RUN-INPUTS.json').exists() and not (HERE / 'FREEZE-READY.json').exists()
    print(json.dumps({'status': 'PASS', 'frozen': args.frozen, 'native_and_manifest_roles': 11,
                      'fixtures': 3, 'candidate_only_driver': True, 'ordinary_records': 130,
                      'driver_assertions': 208, 'ordinary_parser_controls': 30,
                      'driver_parser_controls': 23, 'preference_amendment_controls': preference_controls, 'mochitest_tree_restore_model': True,
                      'manifest_order_and_pref_setup_preserved': True, 'compile_amendment_native_files': sorted(amendments), 'native_compilation': False,
                      'browser_execution': False}, indent=2))


if __name__ == '__main__':
    main()
