import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
from types import SimpleNamespace

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIB = ROOT / 'artifacts/css-spec-lean'
PROPOSAL = ROOT / 'artifacts/css-finite-mod-rem-library-integration-proposal-v1'
INSTALLED = ROOT / 'artifacts/css-finite-mod-rem-install-runtime-v2'
TERMINAL = ROOT / 'artifacts/css-finite-mod-rem-install-terminal-review-v1'
PRIOR = ROOT / 'artifacts/css-round-knowledge-library-integration-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())


def write(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def working():
    result = {}
    for directory, dirs, files in os.walk(LIB):
        dirs[:] = [d for d in dirs if d not in ('.git', '.lake')]
        for name in files:
            path = Path(directory) / name
            result[str(path.relative_to(LIB))] = sha(path)
    return result


def git_state(directory):
    def git(*args):
        return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', '-C', str(directory), *args], env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
    index = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
    return {'head': git('rev-parse', 'HEAD').decode().strip(), 'index_path': str(index),
            'index_sha256': sha(index), 'index_entries_sha256': hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest(),
            'staged_diff_sha256': hashlib.sha256(git('diff', '--cached', '--binary')).hexdigest(),
            'staged_paths': git('diff', '--cached', '--name-only').decode().splitlines()}


def authenticate(directory, digest):
    assert sha(directory / 'FILES.json') == digest, str(directory)
    for name, value in read(directory / 'FILES.json').items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        path = directory / name
        assert stat.S_ISREG(path.lstat().st_mode) and sha(path) == value, str(path)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def native_verifier():
    config = read(INSTALLED / 'CONFIG.json')
    final = read(INSTALLED / 'FINAL.json')
    assert final['pins'] == read(INSTALLED / 'FINAL-PINS.json') and len(final['pins']) == 628
    assert len(final['snapshot']['sources']) == 72 and len(final['installed_tests']) == 25
    assert len(config['index_expectations']['staged_payload_sha256']) == 925
    assert len(config['modified_native_paths']) == 43
    installed_inputs = read(INSTALLED / 'INPUTS.json')
    assert sha(INSTALLED / 'install.py') == installed_inputs['install_sha256']
    for name, digest in installed_inputs['helper_pins'].items():
        assert sha(ROOT / name) == digest, name
    wpt = load('finite_mod_rem_library_wpt', ROOT / config['helpers'] / 'run_wpt.py')
    wpt.HERE, wpt.CONFIG = HERE, config
    index = load('finite_mod_rem_library_index', ROOT / 'artifacts/css-round-baseline-surprises-browser-bound-v1/index_gate.py')
    tree = ast.parse((INSTALLED / 'install.py').read_text())
    names = ('sha', 'need', 'verify_roles', 'verify')
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in functions} == set(names)
    env = {'ROOT': ROOT, 'stat': stat, 'hashlib': hashlib, 'wpt': wpt,
           'config': config, 'before': final, 'restoration': final['pins'],
           'maps': {'installed': final['snapshot']['sources']},
           'snapshots': {'installed': final['snapshot']}, 'owned': {},
           'owned_plan': {'temporary_fixtures': {}, 'permanent_absences': [n for n, h in final['pins'].items() if h is None]},
           'prior': SimpleNamespace(index=index)}
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<authenticated installed verification only>', 'exec'), env)
    binaries = {name: final['pins'][name] for name in wpt.BINARIES}
    return lambda: env['verify']('installed', binaries, active=False)


def main():
    inputs = read(HERE / 'INPUTS.json')
    assert inputs['ready_for_execution'] is True and inputs['actual_session'] is None and inputs['actual_exit'] is None, 'disabled activation'
    assert sha(HERE / 'apply.py') == inputs['apply_sha256']
    for directory, digest in inputs['manifests'].items():
        authenticate(ROOT / directory, digest)
    review = inputs['proposal_review']
    assert review is not None
    authenticate(ROOT / review['path'], review['manifest_sha256'])
    proposal_peer = read(ROOT / review['path'] / 'CHECK.json')
    assert proposal_peer['status'] == 'FINITE_MOD_REM_LIBRARY_INTEGRATION_REVIEW_GO'
    assert proposal_peer['proposal_manifest'] == sha(PROPOSAL / 'FILES.json')
    assert proposal_peer['patch_sha256'] == sha(PROPOSAL / 'integration.patch')
    proposal_refs = read(ROOT / review['path'] / 'REFERENCES.json')
    assert proposal_refs[str((PROPOSAL / 'FILES.json').relative_to(ROOT))] == sha(PROPOSAL / 'FILES.json')
    assert proposal_refs[str((PROPOSAL / 'integration.patch').relative_to(ROOT))] == sha(PROPOSAL / 'integration.patch')
    assert read(HERE / 'ROOT-REVIEW-BINDING.json') == {
        'status': 'FINITE_MOD_REM_LIBRARY_APPLICATION_ROOT_BINDING_GO',
        'inputs_sha256': sha(HERE / 'INPUTS.json'), 'apply_sha256': inputs['apply_sha256'],
        'proposal_review_manifest_sha256': review['manifest_sha256']}
    assert not (HERE / 'BEFORE.json').exists()
    expected = read(PROPOSAL / 'EXPECTED.json')
    transfer = read(PROPOSAL / 'TRANSFER.json')
    assert len(expected['modified_paths']) == 7 and len(expected['new_paths']) == 5
    assert expected['research_theorem_credit_delta'] == expected['normative_coverage_delta'] == 0
    assert sha(INSTALLED / 'FINAL.json') == inputs['installed_final_sha256']
    assert sha(INSTALLED / 'ROOT-COMPLETION.json') == inputs['installed_root_receipt_sha256']
    root = read(INSTALLED / 'ROOT-COMPLETION.json')
    assert root['session'] == 71619 and root['actual_exit'] == 0 and root['installed'] is True and root['fix'] == 128
    peer = read(TERMINAL / 'CHECK.json')
    assert peer['status'] == 'FINITE_MOD_REM_INSTALL_TERMINAL_REVIEW_GO' and peer['installed'] is True
    assert peer['runtime_manifest'] == sha(INSTALLED / 'FILES.json') and peer['root_receipt'] == sha(INSTALLED / 'ROOT-COMPLETION.json')
    assert root['final_sha256'] == sha(INSTALLED / 'FINAL.json') and root['final_pins_sha256'] == sha(INSTALLED / 'FINAL-PINS.json')
    native = native_verifier()
    native_before = native()
    assert native_before == read(INSTALLED / 'FINAL.json')
    write('NATIVE-BEFORE.json', native_before)
    before = {'working_sha256': working(), 'parent': git_state(ROOT),
              'nested': git_state(LIB), 'canonical_report_sha256': sha(LIB / '.lake/verification/report.json')}
    assert before['canonical_report_sha256'] == inputs['prior_canonical_report_sha256'] == sha(PRIOR / 'verification/report.json')
    old_report = read(LIB / '.lake/verification/report.json')
    baseline = expected['actual_baseline']
    assert len(old_report['declaration_axioms']) == baseline['audits'] == 11724
    assert old_report['executable_case_count'] == baseline['cases'] == 12312
    assert len(old_report['source_sha256']) == baseline['sources'] == 2135
    assert sha(LIB / 'coverage.json') == expected['coverage_sha256']
    for name in expected['new_paths']:
        assert not (LIB / name).exists() and not (LIB / name).is_symlink()
    for name, digest in {**expected['preimage_sha256'], **transfer['canonical_dependencies']}.items():
        assert sha(LIB / name) == digest
    for name, digest in old_report['source_sha256'].items():
        assert sha(LIB / name) == digest, name
    shutil.copytree(LIB / '.lake/verification', HERE / 'prior-verification')
    for name in expected['modified_paths']:
        destination = HERE / 'originals' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(LIB / name, destination)
    write('BEFORE.json', before)
    post = dict(before['working_sha256'], **expected['postimage_sha256'])
    failure, preservation_errors = None, []
    try:
        for operation, args in [('apply-check', ['--check']), ('apply', [])]:
            with (HERE / (operation + '.log')).open('xb') as log:
                result = subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                                         'apply', *args, str(PROPOSAL / 'integration.patch')],
                                        cwd=LIB, stdout=log, stderr=subprocess.STDOUT)
            assert result.returncode == 0, operation
        assert working() == post
        write('APPLIED.json', {'status': 'APPLIED_PENDING_FULL_CHECK', 'postimage_sha256': expected['postimage_sha256']})
        argv = ['python3', '-I', '-S', '-B', 'check.py', '--lake', str(ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lake')]
        with (HERE / 'canonical-check.log').open('xb') as log:
            result = subprocess.run(argv, cwd=LIB, env=dict(os.environ, LEAN_NUM_THREADS='2', GIT_OPTIONAL_LOCKS='0'),
                                    stdout=log, stderr=subprocess.STDOUT)
        write('EXECUTION.json', {'argv': argv, 'cwd': str(LIB), 'exit': result.returncode})
        assert result.returncode == 0
        report = read(LIB / '.lake/verification/report.json')
        assert report['status'] == 'pass'
        assert len(report['declaration_axioms']) == expected['planned_audits']
        assert report['executable_case_count'] == expected['planned_cases']
        assert len(report['source_sha256']) == expected['planned_sources']
        assert all(report['declaration_axioms'][name] == value for name, value in old_report['declaration_axioms'].items())
        for name, digest in report['source_sha256'].items():
            assert sha(LIB / name) == digest, name
        for name in ('axioms.log', 'executable-examples.log'):
            assert (LIB / '.lake/verification' / name).read_bytes().startswith((HERE / 'prior-verification' / name).read_bytes())
        lines = (LIB / '.lake/verification/executable-examples.log').read_text().splitlines()
        assert sum(line.endswith(': false') for line in lines) == expected['planned_expected_false']
        shutil.copytree(LIB / '.lake/verification', HERE / 'verification')
    except BaseException as error:
        failure = repr(error)
    finally:
        checks = [
            ('canonical working files', lambda: working() == post if failure is None else
                {n: h for n, h in working().items() if n not in expected['postimage_sha256']} ==
                {n: h for n, h in before['working_sha256'].items() if n not in expected['postimage_sha256']}),
            ('parent raw and semantic index', lambda: git_state(ROOT) == before['parent']),
            ('nested raw and semantic index', lambda: git_state(LIB) == before['nested']),
            ('normative coverage', lambda: sha(LIB / 'coverage.json') == expected['coverage_sha256']),
            ('native installed epoch', lambda: native() == native_before)]
        for label, check in checks:
            try:
                assert check(), label
            except BaseException as error:
                preservation_errors.append(label + ': ' + repr(error))
        write('PRESERVATION.json', {'application_error': failure, 'errors': preservation_errors,
                                   'verified': not preservation_errors, 'native_mutation_performed': False})
    assert failure is None and not preservation_errors, (failure, preservation_errors)
    write('CHECK.json', {'status': 'PASS_APPLIED_CANONICAL', 'declarations': len(report['declaration_axioms']),
                        'cases': report['executable_case_count'], 'sources': len(report['source_sha256']),
                        'expected_false_controls': expected['planned_expected_false'], 'full_check_exit': 0,
                        'unrelated_working_files_preserved': True, 'both_indexes_preserved': True,
                        'old_audit_and_case_prefixes_preserved': True, 'research_theorem_credit_delta': 0,
                        'normative_coverage_delta': 0, 'native_or_browser_changed': False})
    print((HERE / 'CHECK.json').read_text(), flush=True)


if __name__ == '__main__':
    main()
