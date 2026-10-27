import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / 'artifacts/css-finite-mod-rem-comparison-data-v1'
COMPARISON = ROOT / 'artifacts/css-finite-mod-rem-comparison-runtime-v1'
read = lambda p: json.loads(p.read_text())


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(exist_ok=False)
    inputs = read(HERE / 'INPUTS.json')
    assert inputs['ready_for_execution'] is False
    assert all(inputs[k] is None for k in ('controller_review', 'actual_session', 'actual_exit'))
    assert inputs['install_sha256'] == sha(HERE / 'install.py')
    manifests = dict(inputs['manifests'])
    for field in ('terminal_review', 'acceptance'):
        manifests[inputs[field]['path']] = inputs[field]['manifest_sha256']
    for name, digest in manifests.items():
        manifest = ROOT / name / 'FILES.json'
        assert sha(manifest) == digest, name
        for member, value in read(manifest).items():
            assert not Path(member).is_absolute() and '..' not in Path(member).parts
            path = manifest.parent / member
            assert stat.S_ISREG(path.lstat().st_mode) and sha(path) == value, str(path)
    for name, digest in inputs['helper_pins'].items():
        assert sha(ROOT / name) == digest, name
    final = read(COMPARISON / 'FINAL.json')
    assert final['pins'] == read(COMPARISON / 'FINAL-PINS.json')
    assert len(final['pins']) == 628 and len(final['snapshot']['sources']) == 72
    assert len(final['installed_tests']) == 24
    maps = read(DATA / 'SOURCE-MAPS.json')
    assert maps['baseline'] == maps['restored'] == final['snapshot']['sources']
    bodies = read(DATA / 'CANDIDATE.json')['native_paths']
    assert len(bodies) == 1
    for name, paths in bodies.items():
        assert sha(ROOT / paths['original']) == maps['baseline'][name]
        assert sha(ROOT / paths['candidate']) == maps['candidate'][name]
    path = 'testing/web-platform/tests/css/css-values/mod-rem-exact-finite-remainder.html'
    url = '/css/css-values/mod-rem-exact-finite-remainder.html'
    item = read(DATA / 'CANDIDATE.json')['fixture'][path]
    assert final['pins'][path] is None and sha(ROOT / item['source']) == item['sha256']
    policy = read(DATA / 'POLICY.json')
    archived = {(x['test'], x['subtest']): x for x in read(COMPARISON / 'baseline_capture-OUTCOMES.json') if x['test'] == url}
    landing = {(test, subtest) for test, names in policy['mandatory_candidate_pass'].items() for subtest in names}
    repairs = {(x['test'], x['subtest']) for x in policy['observed_repair_identities']}
    assert len(archived) == 24 and set(archived) == landing and len(repairs) == 16
    source = (HERE / 'install.py').read_text()
    tree = ast.parse(source)
    compile(tree, 'install.py', 'exec')
    previous = ROOT / 'artifacts/css-name-repeat-context-install-runtime-v2'
    previous_tree = ast.parse((previous / 'install.py').read_text())
    comparison_tree = ast.parse((COMPARISON / 'compare.py').read_text())
    definitions = lambda t: {n.name: ast.dump(n) for n in t.body if isinstance(n, ast.FunctionDef)}
    defs, old_defs, comparison_defs = definitions(tree), definitions(previous_tree), definitions(comparison_tree)
    inherited = {}
    for name in defs:
        if name in ('verify', 'build'):
            assert defs[name] == old_defs[name], name
            inherited[name] = '127v2 installer'
        elif name != 'capture':
            assert defs[name] == comparison_defs[name], name
            inherited[name] = 'ModRem comparison'
    old_flow = next(n for n in previous_tree.body if isinstance(n, ast.Try))
    actual_flow = next(n for n in tree.body if isinstance(n, ast.Try))
    adapted_flow = ast.unparse(old_flow).replace("len(final['installed_tests']) == 24 and len(final['pins']) == 611",
        "len(final['installed_tests']) == 25 and len(final['pins']) == 628").replace("'fix': 127", "'fix': acceptance['fix']")
    assert ast.dump(ast.parse(adapted_flow).body[0]) == ast.dump(actual_flow)
    names = ('need', 'assess', 'outcomes', 'write_source', 'restore_sources', 'cleanup_fixtures')
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert len(functions) == len(names)
    env = {'observed': archived, 'baseline_outcomes': archived, 'expected_keys': landing, 'landing_keys': landing, 'repair_keys': repairs,
           'stat': stat, 'sha': sha, 'save': lambda *args: None, 'config': {'reftests': []}}
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<selected functions>', 'exec'), env)
    normalize = env['outcomes']
    captured = {}
    for phase in ('candidate', 'restored'):
        result = read(COMPARISON / ('wpt-' + phase) / 'RUN.json')
        selected = {**result, 'rows': [r for r in result['rows'] if r['test'] == url], 'ends': []}
        captured[phase] = normalize(selected)
    assert captured['restored'] == archived
    assert all(v['status'] == 'PASS' for v in captured['candidate'].values())
    assess = env['assess']
    assert not assess(captured['candidate'], 'candidate')[2]
    assert not assess(archived, 'restored')[2]
    decisions = 2
    for key in landing:
        bad = copy.deepcopy(captured['candidate'])
        bad[key]['status'] = 'FAIL'
        assert assess(bad, 'candidate')[2]
        decisions += 1
    for field, value in [('effective_expected', 'FAIL'), ('known_intermittent', ['FAIL'])]:
        bad = copy.deepcopy(captured['candidate'])
        bad[next(iter(repairs))][field] = value
        assert assess(bad, 'candidate')[2]
        decisions += 1
    for field, value in [('message', 'different failure'), ('status', 'PASS'), ('expected', 'FAIL')]:
        bad = copy.deepcopy(archived)
        bad[next(iter(repairs))][field] = value
        assert assess(bad, 'restored')[2]
        decisions += 1
    bad = copy.deepcopy(captured['candidate'])
    bad.pop(next(iter(landing)))
    try:
        assess(bad, 'candidate')
    except RuntimeError:
        decisions += 1
    else:
        raise AssertionError('missing landing result accepted')

    with tempfile.TemporaryDirectory(prefix='finite-mod-rem-install-check-') as name:
        scratch = Path(name)
        for key in ('a', 'b'):
            (scratch / key).write_bytes(('original ' + key).encode())
            (scratch / (key + '.original')).write_bytes(('original ' + key).encode())
            (scratch / (key + '.candidate')).write_bytes(('candidate ' + key).encode())
        original = {key: sha(scratch / key) for key in ('a', 'b')}
        proposed = {key: sha(scratch / (key + '.candidate')) for key in ('a', 'b')}
        env.update(ROOT=scratch, bodies={key: {'original': key + '.original', 'candidate': key + '.candidate'} for key in ('a', 'b')},
                   maps={'baseline': original, 'candidate': proposed}, current_sources=dict(original),
                   source_identities={key: [(scratch / key).stat().st_dev, (scratch / key).stat().st_ino] for key in ('a', 'b')},
                   mutation_started=False, transitions=[])
        env['write_source']('a', 'candidate')
        assert len(env['transitions']) == 1
        assert not env['restore_sources']()
        assert all(sha(scratch / key) == original[key] for key in original)
        env['write_source']('a', 'candidate')
        env['write_source']('b', 'candidate')
        (scratch / 'a').write_bytes(b'unknown edit')
        errors = env['restore_sources']()
        assert len(errors) == 1 and (scratch / 'a').read_bytes() == b'unknown edit' and sha(scratch / 'b') == original['b']
        (scratch / 'a').write_bytes((scratch / 'a.original').read_bytes())
        (scratch / 'replacement').write_bytes((scratch / 'a.original').read_bytes())
        os.replace(scratch / 'replacement', scratch / 'a')
        assert len(env['restore_sources']()) == 1
        for key in ('owned', 'edited', 'replaced'):
            (scratch / key).write_bytes(b'fixture')
        env['owned'] = {key: {'identity': [(scratch / key).stat().st_dev, (scratch / key).stat().st_ino], 'sha256': sha(scratch / key)} for key in ('owned', 'edited', 'replaced')}
        (scratch / 'edited').write_bytes(b'unknown fixture')
        (scratch / 'newfixture').write_bytes(b'fixture')
        os.replace(scratch / 'newfixture', scratch / 'replaced')
        removed, errors = env['cleanup_fixtures']()
        assert removed == ['owned'] and len(errors) == 2
        assert (scratch / 'edited').read_bytes() == b'unknown fixture' and (scratch / 'replaced').read_bytes() == b'fixture'

    bound_config = read(COMPARISON / 'CONFIG.json')
    bound_config.update(tests=[path], expected_subtests={url: read(DATA / 'ROSTER.json')['expected_subtests'][url]},
                        expected_total=24, files_expected_count=1, reftests=[])
    helper = ROOT / 'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py'
    run_node = next(n for n in ast.parse(helper.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    stop = next(i for i, n in enumerate(run_node.body) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'process' for t in n.targets))
    dispatch_checks = []
    with tempfile.TemporaryDirectory(prefix='modrem-install-dispatch-', dir='/private/tmp') as directory:
        resources = {'source': 'digest'}
        fake = SimpleNamespace(CONFIG=bound_config, HERE=Path(directory), BINARIES=[],
                               pins=lambda names: {n: resources.get(n) for n in names}, need=env['need'])
        for label in ('candidate', 'restored'):
            context = {'wpt': fake, 'phase': label, 'resources': resources}
            exec(compile(ast.Module(body=run_node.body[:stop], type_ignores=[]), '<actual helper dispatch>', 'exec'), context)
            assert context['c']['tests'] == [path] and context['c']['expected_subtests'] == bound_config['expected_subtests']
            assert sum(map(len, context['c']['expected_subtests'].values())) == 24
            dispatch_checks.append({'label': label, 'subtests': 24, 'files': 1})
    activation_gate = next(n for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                          and ast.unparse(n.value).startswith("need(inputs['ready_for_execution']"))
    for field in ('ready_for_execution', 'actual_session', 'actual_exit'):
        probe = dict(inputs, ready_for_execution=True)
        probe[field] = False if field == 'ready_for_execution' else 123
        try:
            exec(compile(ast.Module(body=[activation_gate], type_ignores=[]), '<actual readiness gate>', 'exec'),
                 {'inputs': probe, 'need': env['need']})
        except RuntimeError:
            pass
        else:
            raise AssertionError('activation gate accepted ' + field)

    start = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'inputs' for t in n.targets))
    stop = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'prior' for t in n.targets))
    prefix = ast.Module(body=tree.body[start:stop], type_ignores=[])
    assert 'load(' not in ast.unparse(prefix) and 'lstat(' not in ast.unparse(prefix)
    binding_decisions = []
    faults = (None, 'missing-acceptance', 'peer-status', 'peer-runtime', 'peer-root',
              'peer-completion-reference', 'actual-exit', 'acceptance-patch', 'acceptance-scope',
              'acceptance-session', 'acceptance-fix-type', 'acceptance-peer-reference')
    for fault in faults:
        proposed = copy.deepcopy(inputs)
        proposed['ready_for_execution'] = True
        proposed['controller_review'] = read(COMPARISON / 'INPUTS.json')['controller_review']
        if fault == 'missing-acceptance':
            proposed['acceptance'] = None
        review_binding = {'status': 'FINITE_MOD_REM_INSTALL_ROOT_BINDING_GO',
            'inputs_sha256': sha(HERE / 'INPUTS.json'), 'install_sha256': inputs['install_sha256'],
            'controller_review_manifest_sha256': proposed['controller_review']['manifest_sha256']}
        def archived_read(file):
            assert file.is_relative_to(ROOT / 'artifacts'), str(file)
            if file == HERE / 'INPUTS.json':
                return proposed
            if file == HERE / 'ROOT-REVIEW-BINDING.json':
                return review_binding
            value = read(file)
            if file == ROOT / inputs['terminal_review']['path'] / 'CHECK.json':
                if fault == 'peer-status': value['status'] = 'WRONG'
                if fault == 'peer-runtime': value['runtime_manifest'] = 'WRONG'
                if fault == 'peer-root': value['root_receipt'] = 'WRONG'
            if file == ROOT / inputs['terminal_review']['path'] / 'REFERENCES.json' and fault == 'peer-completion-reference':
                value[str((COMPARISON / 'ROOT-COMPLETION.json').relative_to(ROOT))] = 'WRONG'
            if file == COMPARISON / 'ROOT-COMPLETION.json' and fault == 'actual-exit':
                value['actual_exit'] = 1
            if file == ROOT / inputs['acceptance']['path'] / 'ACCEPTANCE.json':
                if fault == 'acceptance-patch': value['patch_sha256'] = 'WRONG'
                if fault == 'acceptance-scope': value['native_paths'].append('unrelated')
                if fault == 'acceptance-session': value['comparison_session'] = 0
                if fault == 'acceptance-fix-type': value['fix'] = True
            if file == ROOT / inputs['acceptance']['path'] / 'REFERENCES.json' and fault == 'acceptance-peer-reference':
                value[inputs['terminal_review']['path'] + '/FILES.json'] = 'WRONG'
            return value
        prefix_env = dict(ROOT=ROOT, HERE=HERE, DATA=DATA, BASELINE=COMPARISON,
                          sha=sha, stat=stat, Path=Path, read=archived_read)
        definitions_for_binding = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('need', 'authenticate')]
        exec(compile(ast.Module(body=definitions_for_binding, type_ignores=[]), '<pure binding helpers>', 'exec'), prefix_env)
        try:
            exec(compile(prefix, '<actual archive binding before helper load>', 'exec'), prefix_env)
        except RuntimeError as error:
            assert fault is not None, str(error)
            binding_decisions.append({'fault': fault, 'rejected': True})
        else:
            assert fault is None
            assert prefix_env['before'] == final and len(prefix_env['restoration']) == 628
            assert prefix_env['config']['tests'] == [path] and prefix_env['config']['expected_total'] == 24
            binding_decisions.append({'fault': None, 'accepted_archive_binding': True})

    main_try = [n for n in tree.body if isinstance(n, ast.Try)]
    assert len(main_try) == 1
    flow_results = []
    for fault in (None, 'write-a', 'write-b', 'build-candidate', 'capture-candidate', 'build-restored', 'capture-restored',
                  'publish-FINAL.json', 'publish-FINAL-PINS.json', 'publish-CLEANUP.json', 'publish-RESULT.json'):
        with tempfile.TemporaryDirectory(prefix='finite-mod-rem-install-flow-') as directory:
            scratch = Path(directory)
            (scratch / 'fixture-source').write_bytes(b'fixture')
            records, calls = {}, []
            state = {'ROOT': scratch, 'HERE': scratch, 'owned_plan': {'temporary_fixtures': {'fixture': {'source': 'fixture-source', 'sha256': sha(scratch / 'fixture-source')}}},
                     'restoration': {'fixture': None}, 'owned': {}, 'bodies': {'a': {}, 'b': {}},
                     'current_binaries': {}, 'source_transitions': [], 'transitions': [],
                     'captured': [], 'completed': [], 'mutation_started': False, 'candidate_ready': False, 'installed': False,
                     'failure': None, 'recovery_errors': [], 'final': None, 'sha': sha, 'need': env['need'], 'acceptance': {'fix': 999999}}
            def action(kind, label):
                calls.append(kind + '-' + label)
                if fault == kind + '-' + label or (fault in ('build-restored', 'capture-restored') and kind + '-' + label == 'capture-candidate'):
                    raise RuntimeError('injected ' + kind + '-' + label)
            def write(name, phase):
                action('write', name)
            def build(label, phase, active=True):
                action('build', label)
            def capture(label, phase):
                action('capture', label)
                state['captured'].append(label)
                state['completed'].append(label)
            def restore():
                calls.extend(['restore-a', 'restore-b'])
                return []
            def cleanup():
                calls.append('cleanup')
                (scratch / 'fixture').unlink()
                return ['fixture'], []
            def save(name, value):
                if fault == 'publish-' + name:
                    (scratch / name).write_text('{"incomplete":')
                    raise OSError('injected partial publication ' + name)
                with (scratch / name).open('x') as stream:
                    stream.write(json.dumps(value))
                records[name] = copy.deepcopy(value)
            state.update(write_source=write, build=build, capture=capture, restore_sources=restore,
                         cleanup_fixtures=cleanup, save=save,
                         verify=lambda *a, **kw: {'pins': dict.fromkeys(range(628)), 'installed_tests': dict.fromkeys(range(25))})
            terminal_error = None
            try:
                exec(compile(ast.Module(body=main_try + [tree.body[-1]], type_ignores=[]), '<actual installer try/finally and terminal gate>', 'exec'), state)
            except RuntimeError as error:
                terminal_error = str(error)
            assert (terminal_error is None) == (fault is None)
            result = records['RESULT.json'] if state['installed'] else records['RECOVERY-RESULT.json']
            if fault is None:
                assert result['installed'] and not result['restored'] and calls == ['write-a', 'write-b', 'build-candidate', 'capture-candidate']
                assert (scratch / 'fixture').is_file()
            else:
                assert not result['installed'] and not (scratch / 'fixture').exists()
                assert all(x in calls for x in ('restore-a', 'restore-b', 'build-restored', 'cleanup'))
                if fault == 'build-restored':
                    assert 'capture-restored' not in calls and result['recovery_errors'] and not result['restored']
                elif fault == 'capture-restored':
                    assert result['recovery_errors'] and not result['restored']
                else:
                    assert 'capture-restored' in calls and result['restored'] and not result['recovery_errors']
            if fault and fault.startswith('publish-'):
                failed_name = fault.removeprefix('publish-')
                assert state['candidate_ready'] and not state['installed']
                assert (scratch / failed_name).read_text() == '{"incomplete":'
                assert failed_name in result['supersedes_partial_success_records']
                assert all(name in records for name in ('RECOVERY-FINAL.json', 'RECOVERY-FINAL-PINS.json', 'RECOVERY-CLEANUP.json', 'RECOVERY-RESULT.json'))
            flow_results.append({'fault': fault, 'calls': calls, 'installed': result['installed'], 'restored': result['restored'], 'terminal_error': terminal_error})
    result = {'status': 'DISABLED_FINITE_MOD_REM_INSTALL_STATIC_PASS', 'source_sha256': sha(HERE / 'install.py'),
              'decisions': decisions, 'actual_archive_binding_checks': binding_decisions, 'readiness_rejections': 3, 'actual_helper_dispatch': dispatch_checks, 'scratch_ownership_cases': 4, 'actual_try_finally_scenarios': flow_results,
              'unchanged_helper_functions': inherited, 'publication_recovery_flow_exact_127v2': True,
              'roles': 628, 'source_guards': 72, 'source_deltas': 1, 'original_identities': 24,
              'success_identities': 25, 'landing_subtests': 24, 'main_controller_executed': False,
              'live_reads_or_actions': False, 'compiler_products_created': False}
    (out / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
