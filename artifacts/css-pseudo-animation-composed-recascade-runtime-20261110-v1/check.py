import argparse, ast, hashlib, importlib.util, json, re, shutil, subprocess, sys, tempfile, tomllib
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text())
def git_file(revision, name):
    return subprocess.run(['git', '-c', 'core.fsmonitor=false', 'show', revision + ':' + name], cwd=ROOT, capture_output=True)
def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value

def input_names():
    names = [str(p.relative_to(HERE)) for p in HERE.glob('*.py')]
    names += [str(p.relative_to(HERE)) for p in HERE.glob('*.patch')]
    names += ['RUN-PLAN.json', 'SOURCE-ROLES.json', 'EXPECTED-BASELINE.json', 'EXPECTED-CALLBACKS.json', 'EXPECTED-CHANGES.json', 'DRIVER-ASSERTIONS.json', 'RECASCADE-ASSERTIONS.json', 'ORIGINS.json', 'COMPILE-AMENDMENT.json', 'ENUM-AMENDMENT.json', 'MARKER-AMENDMENT.json', 'GEOMETRY-AMENDMENT.json', 'COMPOSED-ORIGIN.json', 'COMPOSED-ASSERTIONS.json']
    for directory in ['source', 'candidate', 'runtime-inputs', 'harness-source']:
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
    origin = load(HERE / 'COMPOSED-ORIGIN.json')
    previous, source = ROOT / origin['runtime'], ROOT / origin['source']
    assert sha(previous / 'RUN-INPUTS.json') == origin['runtime_manifest_sha256']
    previous_manifest = load(previous / 'RUN-INPUTS.json')
    assert all(sha(previous / name) == digest for name, digest in previous_manifest.items())
    assert sha(source / 'SOURCE-ONLY.json') == origin['source_manifest_sha256']
    assert all(sha(source / name) == digest for name, digest in load(source / 'SOURCE-ONLY.json').items())
    assert sha(ROOT / origin['source_review']) == origin['source_review_sha256']
    assert sha(HERE / 'composed.patch') == origin['patch_sha256'] == sha(source / 'driver.patch')
    plan, roles, origins = [load(HERE / n) for n in ['RUN-PLAN.json', 'SOURCE-ROLES.json', 'ORIGINS.json']]
    changed_native = {'dom/base/nsDOMWindowUtils.cpp', 'dom/interfaces/base/nsIDOMWindowUtils.idl', 'dom/base/test/mochitest.toml'}
    changed = {'check.py', 'run.py', 'RUN-PLAN.json', 'SOURCE-ROLES.json', 'runtime-inputs/test-source-pins.json', 'runtime-inputs/retained-build.json'} | {'candidate/' + n for n in changed_native}
    for name, digest in previous_manifest.items():
        if name not in changed:
            assert sha(HERE / name) == digest, ('changed inherited input', name)
    assert len(roles) == 14 and all(not r['install_both'] for r in roles.values())
    old_roles = load(previous / 'SOURCE-ROLES.json')
    assert set(roles) == set(old_roles)
    for name, role in roles.items():
        result = git_file(origins['source_test_pin_revision'], name)
        assert result.returncode == 0 and result.stdout == (HERE / 'source' / name).read_bytes()
        assert sha(HERE / 'source' / name) == role['base'] == old_roles[name]['base']
        assert sha(HERE / 'candidate' / name) == role['candidate']
        if name in changed_native:
            assert (HERE / 'candidate' / name).read_bytes() == (source / 'candidate' / name).read_bytes()
        else:
            assert role == old_roles[name]
    for name, digest in origins['authenticated_files'].items():
        result = git_file(origins['signed_origin'], name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
    old_plan = load(previous / 'RUN-PLAN.json')
    for name in ['suites', 'lint_paths', 'driver_test', 'driver_expected_assertions', 'recascade_test', 'recascade_expected_assertions', 'mozconfig_sha256']:
        assert plan[name] == old_plan[name]
    assert plan['composed_expected_assertions'] == 122 and plan['composed_expected_nonprobes'] == 119
    assert plan['composed_expected_probes'] == 3 and plan['composed_expected_tasks'] == 5
    assert len(plan['suites']) == len(set(plan['suites'])) == 12
    assert plan['fixtures'] == dict(old_plan['fixtures'], **{plan['composed_test']: 'test_missing_pseudo_animation_composed.html'})
    assert plan['candidate_only_fixtures'] == old_plan['candidate_only_fixtures'] + [plan['composed_test']]
    assert len(plan['fixtures']) == 5
    inventory = load(HERE / 'COMPOSED-ASSERTIONS.json')
    assert inventory == load(source / 'ASSERTIONS.json')
    assertions = [a for task in inventory['tasks'] for a in task['assertions']]
    assert len(assertions) == len({a['name'] for a in assertions}) == 122
    assert Counter(a['classification'] for a in assertions) == {'setup': 33, 'result': 86, 'probe': 3}
    assert len(inventory['tasks']) == 5
    pins = load(HERE / 'runtime-inputs/test-source-pins.json')
    assert pins == dict(load(previous / 'runtime-inputs/test-source-pins.json'), **{plan['composed_test']: None})
    for name, digest in pins.items():
        result = git_file(origins['source_test_pin_revision'], name)
        assert result.returncode != 0 if digest is None else result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
    assert (HERE / 'runtime-inputs/test_missing_pseudo_animation_composed.html').read_bytes() == (source / 'test_missing_pseudo_animation_composed.html').read_bytes()
    harness = git_file(origins['source_test_pin_revision'], 'testing/mochitest/tests/SimpleTest/TestRunner.js')
    assert harness.returncode == 0 and harness.stdout == (HERE / 'harness-source/TestRunner.js').read_bytes()
    old_run, new_run = [(p / 'run.py').read_text() for p in [previous, HERE]]
    assert old_run[old_run.index('def restore('):] == new_run[new_run.index('def restore('):]
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    patches = ['query.patch', 'driver.patch', 'manifest-order.patch', 'pref-setup.patch', 'compile-fixes.patch', 'unresolved-seek.patch', 'recascade.patch', 'GEOMETRY-AMENDMENT.patch', 'composed.patch']
    with tempfile.TemporaryDirectory(prefix='composed-runtime-check-') as directory:
        scratch = Path(directory) / 'sources'
        shutil.copytree(HERE / 'source', scratch)
        for name in patches:
            subprocess.run(['patch', '--batch', '-p1', '-i', str(HERE / name)], cwd=scratch, check=True, capture_output=True)
        assert all((scratch / name).read_bytes() == (HERE / 'candidate' / name).read_bytes() for name in roles)
        for name in plan['candidate_only_fixtures']:
            assert (scratch / name).read_bytes() == (HERE / 'runtime-inputs' / plan['fixtures'][name]).read_bytes()
        for name in reversed(patches):
            subprocess.run(['patch', '-R', '--batch', '-p1', '-i', str(HERE / name)], cwd=scratch, check=True, capture_output=True)
        assert all((scratch / name).read_bytes() == (HERE / 'source' / name).read_bytes() for name in roles)
        assert all(not (scratch / name).exists() for name in plan['candidate_only_fixtures'])
        b = module('bundle')
        tree = Path(directory) / 'tree'; tree.mkdir()
        (tree / 'original').write_text('before'); (tree / 'link').symlink_to('original')
        before = b.scan(tree); mapping = b.backup(tree, before, Path(directory) / 'backup')
        (tree / 'original').write_text('candidate'); (tree / 'new').write_text('temporary')
        (tree / 'link').unlink(); (tree / 'link').symlink_to('new')
        b.restore(tree, before, b.scan(tree), Path(directory) / 'backup', mapping)
        assert b.semantic(b.scan(tree)) == b.semantic(before)
    manifest = tomllib.loads((HERE / 'candidate' / plan['driver_manifest']).read_text())
    old_manifest = tomllib.loads((previous / 'candidate' / plan['driver_manifest']).read_text())
    assert manifest == dict(old_manifest, **{Path(plan['composed_test']).name: {}})
    sort_source = HERE / 'runtime-inputs/manifest-sort.py'
    nodes = [node for node in ast.parse(sort_source.read_text()).body if isinstance(node, ast.FunctionDef) and node.name in ['sort_paths_keyfn', 'sort_paths'] or isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ['FILENAME_REGEX', 'DEFAULT_SECTION'] for t in node.targets)]
    namespace = {'re': re}; exec(compile(ast.Module(body=nodes, type_ignores=[]), str(sort_source), 'exec'), namespace)
    names = [n for n in manifest if n != 'DEFAULT']; assert names == namespace['sort_paths'](names)
    baseline = load(HERE / 'EXPECTED-BASELINE.json'); analyzer = module('analyze')
    assert len(analyzer.rows(baseline)) == 130 and len(baseline['harness']) == 12
    assert Counter(r['status'] for r in baseline['subtests']) == {'PASS': 99, 'FAIL': 19}
    controls = {}
    for name, count in [('parser-controls', 30), ('driver-controls', 23), ('recascade-controls', 23), ('composed-controls', 41)]:
        value = json.loads(subprocess.check_output([sys.executable, '-I', '-B', str(HERE / (name + '.py'))]))
        assert value['status'].upper() == 'PASS' and len(value['rejected_controls']) == count
        controls[name] = count
    if args.frozen:
        retained_path = HERE / 'runtime-inputs/retained-build.json'
        assert sha(retained_path) == plan['retained_build_sha256'] == sha(ROOT / plan['retained_build_origin'])
        validate_retained(load(retained_path), plan['head'], plan, origins, roles)
        manifest = load(HERE / 'RUN-INPUTS.json')
        assert set(manifest) == set(input_names()) and all(sha(HERE / n) == h for n, h in manifest.items())
    else:
        assert plan['head'] is None and plan['retained_build_origin'] is None and plan['retained_build_sha256'] is None
        assert not (HERE / 'RUN-INPUTS.json').exists() and not (HERE / 'FREEZE-READY.json').exists()
        assert not (HERE / 'runtime-inputs/retained-build.json').exists()
    print(json.dumps({'status': 'PASS', 'frozen': args.frozen, 'source_roles': 14, 'fixtures': 5,
                      'ordinary_records': 130, 'query_assertions': 208, 'recascade_assertions': 100,
                      'composed_assertions': 122, 'composed_nonprobes': 119, 'composed_setup': 33,
                      'composed_probes': 3, 'composed_tasks': 5, 'controls': controls,
                      'restore_function_byte_identical': True, 'patch_replay_and_reverse': True,
                      'native_compilation': False, 'browser_execution': False}, indent=2))

if __name__ == '__main__':
    main()
