import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIB = ROOT / 'artifacts/css-spec-lean'
PROPOSAL = ROOT / 'artifacts/css-steps-origin-library-proposal-v1'
INPUTS = HERE / 'INPUTS.json'
read = lambda p: json.loads(p.read_text())


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(name, value):
    with (HERE / name).open('x') as f:
        f.write(json.dumps(value, indent=2) + '\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_binding(inputs):
    assert inputs['ready'] is True, 'disabled application plan'
    for key in ('post_capture_epoch', 'post_capture_receipt'):
        ref = inputs[key]
        assert isinstance(ref, dict) and isinstance(ref.get('path'), str)
        assert not Path(ref['path']).is_absolute() and '..' not in Path(ref['path']).parts
        digest = ref.get('sha256')
        assert isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)
    required = inputs['post_capture_receipt'].get('required_fields')
    assert isinstance(required, dict) and required and 'status' in required
    assert isinstance(required['status'], str) and required['status']
    assert isinstance(inputs['protected_binary_paths'], list) and len(inputs['protected_binary_paths']) == 4
    assert set(inputs['protected_binary_paths']) == {
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL',
        'objdir-full.noindex/dist/bin/gtest/XUL'}


def main():
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    assert not any(k in os.environ for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'))
    inputs = read(INPUTS)
    validate_binding(inputs)
    mutable = {'ready', 'post_capture_epoch', 'post_capture_receipt'}
    static = read(HERE / 'STATIC-INPUTS.json')
    assert {k: v for k, v in inputs.items() if k not in mutable} == {k: v for k, v in static.items() if k not in mutable}
    assert not (HERE / 'BEFORE.json').exists()
    for path, digest in inputs['helper_pins'].items():
        assert sha(ROOT / path) == digest, path
    save('ATTEMPT.json', {'inputs_sha256': sha(INPUTS), 'canonical_application_authorized': True})
    h = load('library_helpers', ROOT / 'artifacts/css-keyframe-animation-library-application-v1/apply.py')
    pins = load('epoch_helpers', ROOT / 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    h.ENV = dict(h.ENV, LEAN_NUM_THREADS='1')
    refs = inputs['references']
    for path, digest in refs.items():
        h.authenticate(ROOT / path, digest)
    save('REFERENCES.json', refs)
    for name, pin in read(PROPOSAL / 'REFERENCES.json').items():
        assert sha(ROOT / name) == pin, name
    for key in ('post_capture_epoch', 'post_capture_receipt'):
        assert sha(ROOT / inputs[key]['path']) == inputs[key]['sha256'], key
    receipt = read(ROOT / inputs['post_capture_receipt']['path'])
    for key, value in inputs['post_capture_receipt']['required_fields'].items():
        assert receipt[key] == value, key
    epoch = read(ROOT / inputs['post_capture_epoch']['path'])
    assert {n: pins.fingerprint(ROOT, n) for n in epoch['pins']} == epoch['pins']
    assert all(n in epoch['pins'] and epoch['pins'][n] for n in inputs['protected_binary_paths'])
    research = epoch['committed_research_working_payloads']
    assert {n: pins.fingerprint(ROOT, n) for n in research} == research
    plan = read(PROPOSAL / 'PLAN.json')
    changes = plan['changes']
    assert len(changes) == 10
    lean = ROOT / inputs['compiler']
    assert sha(lean) == inputs['compiler_sha256']
    assert sha(ROOT / inputs['lake']) == inputs['lake_sha256']
    for name, pair in changes.items():
        assert pins.fingerprint(LIB, name) == pair['before'], name
        assert sha(PROPOSAL / 'candidate' / name) == pair['after'], name
    before = h.state()
    save('BEFORE.json', before)
    assert before['nested']['head'] == plan['base_head'], 'canonical proposal base HEAD'
    for local, key in [('root', 'semantic_index'), ('nested', 'nested_semantic_index')]:
        for observed, recorded in [('head', 'head'), ('index_entries_sha256', 'entries'), ('cached_diff_sha256', 'cached_diff')]:
            assert before[local][observed] == epoch[key][recorded], (local, observed)
    assert before['root']['raw_index_sha256'] == epoch['raw_index_observation']['current']
    for n, pin in epoch.get('staged_working', {}).items():
        assert pins.fingerprint(ROOT, n) == pin, n
    for n, identity in epoch['installed_identities'].items():
        info = (ROOT / n).lstat()
        assert [info.st_dev, info.st_ino] == identity, n
    assert sha(LIB / '.lake/verification/report.json') == plan['base_report_sha256']
    old = read(LIB / '.lake/verification/report.json')
    assert old['status'] == 'pass'
    assert (len(old['declaration_axioms']), len(old['executable_cases']), len(old['source_sha256'])) == (11830, 12424, 2153)
    assert sum(not r['result'] for r in old['executable_cases']) == 170
    for name, pin in old['source_sha256'].items():
        assert sha(LIB / name) == pin, name
    shutil.copytree(LIB / '.lake/verification', HERE / 'previous-verification')
    expected_working = json.loads(json.dumps(before['working']))
    for name, pair in changes.items():
        expected_working[name] = {'kind': 'file', 'sha256': pair['after'], 'mode': before['working'].get(name, {}).get('mode', 0o644)}
    expected_roles = dict(epoch['pins'])
    expected_roles.update({str((LIB / name).relative_to(ROOT)): pair['after'] for name, pair in changes.items()})
    failure, errors, applied, code = None, [], False, None
    try:
        for label, args in [('apply-check', ['--check']), ('apply', [])]:
            with (HERE / (label + '.log')).open('xb') as log:
                run = subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', 'apply', *args, str(PROPOSAL / 'library.patch')], cwd=LIB, env=h.ENV, stdout=log, stderr=subprocess.STDOUT)
            assert run.returncode == 0, label
        applied = True
        assert h.working() == expected_working
        save('APPLIED.json', {'status': 'STEPS_ORIGIN_APPLIED_FULL_CHECK_PENDING', 'postimages': {n: p['after'] for n, p in changes.items()}})
        command = [sys.executable, '-I', '-S', '-B', 'check.py', '--lake', str(ROOT / inputs['lake'])]
        print('Ten-path steps-origin package applied; full canonical check starting.', flush=True)
        with (HERE / 'canonical-check.log').open('xb') as log:
            run = subprocess.run(command, cwd=LIB, env=h.ENV, stdout=log, stderr=subprocess.STDOUT)
        code = run.returncode
        save('CHECK-EXECUTION.json', {'command': command, 'exit': code, 'LEAN_NUM_THREADS': h.ENV['LEAN_NUM_THREADS']})
        assert code == 0, 'full canonical check failed'
        report = read(LIB / '.lake/verification/report.json')
        assert report['status'] == 'pass'
        totals = {'audits': len(report['declaration_axioms']), 'cases': len(report['executable_cases']), 'sources': len(report['source_sha256']), 'false_cases': sum(not r['result'] for r in report['executable_cases'])}
        assert totals == {'audits': 11840, 'cases': 12438, 'sources': 2155, 'false_cases': 173}, totals
        assert report['executable_cases'] == old['executable_cases'] + [{'name': n, 'result': v} for n, v in plan['cases']]
        checker = load('canonical_checker', LIB / 'check.py')
        transferred_axioms = checker.parse_axiom_audit((PROPOSAL / 'replay/audits.log').read_text())
        assert set(transferred_axioms) == set(plan['audits'])
        assert not set(transferred_axioms) & set(old['declaration_axioms'])
        expected_axioms = old['declaration_axioms'] | transferred_axioms
        assert report['declaration_axioms'] == expected_axioms
        for name in ('axioms.log', 'executable-examples.log'):
            assert (LIB / '.lake/verification' / name).read_bytes().startswith((HERE / 'previous-verification' / name).read_bytes()), name
        expected_sources = dict(old['source_sha256'])
        expected_sources.update({n: p['after'] for n, p in changes.items() if n in expected_sources or n.endswith('.lean')})
        assert report['source_sha256'] == expected_sources
        for name, pin in report['source_sha256'].items():
            assert sha(LIB / name) == pin, name
        for name, record in report['commands'].items():
            assert sha(LIB / '.lake/verification' / (name + '.log')) == record['log_sha256']
    except BaseException as error:
        failure = repr(error)
    finally:
        try:
            assert sha(lean) == inputs['compiler_sha256']
            assert sha(ROOT / inputs['lake']) == inputs['lake_sha256']
            after = h.state()
            save('AFTER.json', after)
            for name in ('root', 'nested', 'main_native_diff_sha256', 'main_nonartifact_diff_sha256'):
                assert after[name] == before[name], name
            untouched = lambda w: {n: v for n, v in w.items() if n not in changes}
            assert untouched(after['working']) == untouched(before['working'])
            observed_roles = dict(epoch['pins'])
            for name, pair in changes.items():
                actual = pins.fingerprint(LIB, name)
                assert actual in (pair['before'], pair['after']), ('unknown proposal body', name)
                observed_roles[str((LIB / name).relative_to(ROOT))] = actual
            if applied:
                assert after['working'] == expected_working
                assert observed_roles == expected_roles
            assert {n: pins.fingerprint(ROOT, n) for n in observed_roles} == observed_roles
            for n, pin in epoch.get('staged_working', {}).items():
                assert pins.fingerprint(ROOT, n) == pin, n
            assert {n: pins.fingerprint(ROOT, n) for n in research} == research
            for name, identity in epoch['installed_identities'].items():
                info = (ROOT / name).lstat()
                assert [info.st_dev, info.st_ino] == identity, name
        except BaseException as error:
            errors.append(repr(error))
        try:
            shutil.copytree(LIB / '.lake/verification', HERE / 'verification')
        except BaseException as error:
            errors.append('verification archive: ' + repr(error))
        save('PRESERVATION.json', {'application_error': failure, 'preservation_errors': errors, 'applied': applied, 'full_check_exit': code, 'rollback_performed': False})
    if failure is not None or errors:
        save('RESULT.json', {'status': 'STEPS_ORIGIN_LIBRARY_APPLICATION_OR_CHECK_FAILED', 'applied': applied, 'full_check_exit': code, 'error': failure, 'preservation_errors': errors, 'rollback_performed': False})
        raise RuntimeError((failure, errors))
    save('RESULT.json', {'status': 'STEPS_ORIGIN_LIBRARY_FULL_CHECK_PASS', **totals, 'transferred_audits': 10, 'new_proof_discovery_credit': 0, 'normative_coverage_delta': 0, 'native_refinement_proved': False, 'both_indexes_preserved': True, 'native_and_binary_unchanged': True, 'guarded_roles': len(expected_roles)})
    print((HERE / 'RESULT.json').read_text(), flush=True)


if __name__ == '__main__':
    main()
