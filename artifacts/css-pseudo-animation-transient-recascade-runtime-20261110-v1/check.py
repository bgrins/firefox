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
    names += ['RUN-PLAN.json', 'SOURCE-ROLES.json', 'EXPECTED-BASELINE.json', 'EXPECTED-CALLBACKS.json', 'EXPECTED-CHANGES.json', 'DRIVER-ASSERTIONS.json', 'RECASCADE-ASSERTIONS.json', 'ORIGINS.json', 'COMPILE-AMENDMENT.json']
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
    parser = argparse.ArgumentParser(); parser.add_argument('--frozen', action='store_true'); args = parser.parse_args()
    origins, plan, roles = [load(HERE / n) for n in ['ORIGINS.json', 'RUN-PLAN.json', 'SOURCE-ROLES.json']]
    previous = ROOT / origins['runtime_origin']; candidate = ROOT / origins['candidate_origin']
    assert sha(previous / 'RUN-INPUTS.json') == origins['runtime_manifest_sha256']
    for name, digest in load(previous / 'RUN-INPUTS.json').items(): assert sha(previous / name) == digest
    assert sha(candidate / 'SOURCE-ONLY.json') == origins['candidate_manifest_sha256']
    for name, digest in load(candidate / 'SOURCE-ONLY.json').items(): assert sha(candidate / name) == digest
    for name, digest in origins['authenticated_files'].items():
        result = git_file(origins['signed_origin'], name)
        assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest and sha(ROOT / name) == digest
    preserved = ['bundle.py', 'process.py', 'analyze.py', 'parser-controls.py', 'driver-analyze.py', 'driver-controls.py', 'freeze.py', 'EXPECTED-BASELINE.json', 'EXPECTED-CALLBACKS.json', 'EXPECTED-CHANGES.json', 'DRIVER-ASSERTIONS.json', 'COMPILE-AMENDMENT.json']
    patches = ['query.patch', 'driver.patch', 'manifest-order.patch', 'pref-setup.patch', 'compile-fixes.patch', 'unresolved-seek.patch']
    for name in preserved + patches: assert (HERE / name).read_bytes() == (previous / name).read_bytes()
    assert sha(HERE / 'recascade.patch') == origins['recascade_patch_sha256'] == sha(candidate / 'extension.patch')
    expected_analyzer = (previous / 'driver-analyze.py').read_text().replace('DRIVER-ASSERTIONS.json', 'RECASCADE-ASSERTIONS.json').replace("plan['driver_expected_assertions']", "plan['recascade_expected_assertions']").replace("plan['driver_test']", "plan['recascade_test']")
    assert (HERE / 'recascade-analyze.py').read_text() == expected_analyzer
    expected_controls = (previous / 'driver-controls.py').read_text().replace('driver-analyze', 'recascade-analyze').replace('DRIVER-ASSERTIONS.json', 'RECASCADE-ASSERTIONS.json').replace("plan['driver_test']", "plan['recascade_test']").replace("'positive_assertions': 208", "'positive_assertions': 100")
    assert (HERE / 'recascade-controls.py').read_text() == expected_controls
    prior_run, this_run = [(d / 'run.py').read_text() for d in [previous, HERE]]
    assert prior_run[prior_run.index('def restore('):] == this_run[this_run.index('def restore('):]
    for p in HERE.glob('*.py'): ast.parse(p.read_text(), filename=str(p))
    assert len(roles) == 14 and all(r['install_both'] is False for r in roles.values())
    assert len(plan['suites']) == len(set(plan['suites'])) == 12
    assert len(plan['fixtures']) == 4 and plan['candidate_only_fixtures'] == [plan['driver_test'], plan['recascade_test']]
    assert plan['lint_paths'] == [n for n in plan['fixtures'] if n.startswith('testing/web-platform/tests/')]
    for name, role in roles.items():
        result = git_file(origins['source_test_pin_revision'], name)
        assert result.returncode == 0 and result.stdout == (HERE / 'source' / name).read_bytes()
        assert sha(HERE / 'source' / name) == role['base']
        assert sha(HERE / 'candidate' / name) == role['candidate'] == sha(candidate / 'candidate' / name)
    source_inventory = load(candidate / 'ASSERTIONS.json')
    recascade_inventory = load(HERE / 'RECASCADE-ASSERTIONS.json')
    expected_inventory = {'assertion_count': source_inventory['assertion_count'], 'tasks': [{'name': t, 'assertions': [{'name': r['label'], 'classification': 'setup' if r['kind'] == 'setup' else 'diagnostic' if r['kind'] == 'admission_preservation' else 'result'} for r in source_inventory['rows'] if r['task'] == t]} for t in source_inventory['tasks']]}
    assert recascade_inventory == expected_inventory and recascade_inventory['assertion_count'] == 100
    assert sum(a['classification'] == 'setup' for t in recascade_inventory['tasks'] for a in t['assertions']) == 6
    assert plan['driver_expected_assertions'] == 208 and plan['recascade_expected_assertions'] == 100
    with tempfile.TemporaryDirectory(prefix='transient-recascade-runtime-check-') as directory:
        scratch = Path(directory) / 'sources'; shutil.copytree(HERE / 'source', scratch)
        for name in patches + ['recascade.patch']:
            subprocess.run(['patch', '--batch', '-p1', '-i', str(HERE / name)], cwd=scratch, check=True, capture_output=True)
        assert all((scratch / name).read_bytes() == (HERE / 'candidate' / name).read_bytes() for name in roles)
        for name in [plan['driver_test'], plan['recascade_test']]:
            assert (scratch / name).read_bytes() == (HERE / 'runtime-inputs' / plan['fixtures'][name]).read_bytes()
        for name in reversed(patches + ['recascade.patch']):
            subprocess.run(['patch', '-R', '--batch', '-p1', '-i', str(HERE / name)], cwd=scratch, check=True, capture_output=True)
        assert all((scratch / name).read_bytes() == (HERE / 'source' / name).read_bytes() for name in roles)
        assert all(not (scratch / name).exists() for name in plan['candidate_only_fixtures'])
        b = module('bundle'); tree = Path(directory) / 'test-tree'; tree.mkdir()
        (tree / 'original').write_text('before'); (tree / 'link').symlink_to('original')
        before = b.scan(tree); mapping = b.backup(tree, before, Path(directory) / 'backup')
        (tree / 'original').write_text('candidate'); (tree / 'new').write_text('temporary fixture')
        (tree / 'link').unlink(); (tree / 'link').symlink_to('new')
        b.restore(tree, before, b.scan(tree), Path(directory) / 'backup', mapping)
        assert b.semantic(b.scan(tree)) == b.semantic(before)
    pins = load(HERE / 'runtime-inputs/test-source-pins.json')
    old_pins = load(previous / 'runtime-inputs/test-source-pins.json')
    assert pins == dict(old_pins, **{plan['recascade_test']: None})
    for name, digest in pins.items():
        result = git_file(origins['source_test_pin_revision'], name)
        assert result.returncode != 0 if digest is None else result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
    for name, filename in plan['fixtures'].items():
        assert pins[name] is None
        original = candidate / filename if name == plan['recascade_test'] else previous / 'runtime-inputs' / filename
        assert (HERE / 'runtime-inputs' / filename).read_bytes() == original.read_bytes()
    old_manifest = tomllib.loads((previous / 'candidate' / plan['driver_manifest']).read_text())
    manifest = tomllib.loads((HERE / 'candidate' / plan['driver_manifest']).read_text())
    assert manifest == dict(old_manifest, **{Path(plan['recascade_test']).name: {}})
    sort_source = HERE / 'runtime-inputs/manifest-sort.py'
    assert sort_source.read_bytes() == (previous / 'runtime-inputs/manifest-sort.py').read_bytes()
    nodes = [node for node in ast.parse(sort_source.read_text()).body if isinstance(node, ast.FunctionDef) and node.name in ['sort_paths_keyfn', 'sort_paths'] or isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ['FILENAME_REGEX', 'DEFAULT_SECTION'] for t in node.targets)]
    namespace = {'re': re}; exec(compile(ast.Module(body=nodes, type_ignores=[]), str(sort_source), 'exec'), namespace)
    names = [n for n in manifest if n != 'DEFAULT']; assert names == namespace['sort_paths'](names)
    base = load(HERE / 'EXPECTED-BASELINE.json'); a = module('analyze')
    assert len(a.rows(base)) == 130 and len(base['harness']) == 12
    assert Counter(r['status'] for r in base['subtests']) == {'PASS': 99, 'FAIL': 19}
    previous_result = load(previous / 'candidate1/RESULT.json')
    assert previous_result['error'] is None and previous_result['restoration_verified']
    assert a.compare(base, load(previous / 'candidate1/TEST-RESULTS.json'))['accepted_changes_only']
    controls = {}
    for name, count in [('parser-controls', 30), ('driver-controls', 23), ('recascade-controls', 23)]:
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
    print(json.dumps({'status': 'PASS', 'frozen': args.frozen, 'source_roles': 14, 'fixtures': 4, 'ordinary_records': 130, 'query_assertions': 208, 'recascade_assertions': 100, 'recascade_setup_checks': 6, 'controls': controls, 'restore_function_byte_identical': True, 'patch_replay_and_reverse': True, 'manifest_order_verified': True, 'native_compilation': False, 'browser_execution': False}, indent=2))
if __name__ == '__main__': main()
