import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = ROOT / 'artifacts/css-keyframe-operation-descriptor-runtime-v1'
SIGNING = ROOT / 'artifacts/css-pending-121-131-signing-execution-v2'
LEDGER = ROOT / 'artifacts/css-pending-121-131-committed-ledger-runtime-v3'
PACKAGE = ROOT / 'artifacts/css-pending-121-131-execution-package-v1'
PREP = ROOT / 'artifacts/css-keyframe-operation-descriptor-capture-preparation-v1'
TARGET = ROOT / 'artifacts/css-keyframe-operation-descriptor-capture-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
read = lambda p: json.loads(p.read_text())


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(path, expected):
    assert sha(path) == expected, str(path)
    for name, pin in read(path).items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert sha(path.parent / name) == pin, name


def archives():
    authenticate(SIGNING / 'FILES.json', '021bda6ad19579a2c9816f919dc090c164dc3c5fb6e6d0841400ba994a716cdb')
    authenticate(LEDGER / 'FILES.json', '685b4f1688c4e51020403c25c20cb7af558643c4539be7b5dd253684c4fc4bda')
    authenticate(PACKAGE / 'FILES.json', 'adae4c29ddb73bfb203af150f70911999d5e99bfc524f30d6b4f6ac29a725028')
    authenticate(PREP / 'DRAFT-FILES.json', '36d8982349cdb63dba104d4e85fdc1d6bd4da85669037a96dd78e82896f998e3')
    adapter_input = read(HERE / 'ADAPTER.json')
    adapter_path = ROOT / adapter_input['manifest']['path']
    authenticate(adapter_path, adapter_input['manifest']['sha256'])
    adapter = load('post_signing_epoch', adapter_path.parent / 'epoch.py')
    ledger_inputs = read(LEDGER / 'INPUTS.json')
    for name, pin in ledger_inputs['helper_pins'].items():
        assert sha(ROOT / name) == pin
    h = load('epoch_helpers', ROOT / ledger_inputs['helper'])
    updater = load('ledger_receipts', LEDGER / 'update.py')
    execution = read(SIGNING / 'EXECUTION-RESULT.json')
    assert sha(SIGNING / 'EXECUTION-RESULT.json') == ledger_inputs['execution_result_sha256']
    assert sha(SIGNING / 'FILES.json') == ledger_inputs['signing_files_sha256']
    old = read(SIGNING / 'CURRENT-EPOCH.json')
    assert sha(SIGNING / 'CURRENT-EPOCH.json') == ledger_inputs['signing_epoch_sha256']
    sequence = [Path(n).stem for n in read(PACKAGE / 'EXECUTION.json')['sequence']]
    receipts = {n: read(SIGNING / (n + '-ROOT-RESULT.json')) for n in sequence}
    head = updater.verified_receipts(execution, receipts, sequence,
                                    sha(SIGNING / 'CURRENT-EPOCH.json'), old['semantic_index']['head'])
    research = dict(old['committed_research_working_payloads'])
    research_count = 0
    for name in sequence:
        recipe = read(PACKAGE / (name + '.json'))
        assert recipe == read(SIGNING / (name + '.json'))
        result = receipts[name]
        signed = read(SIGNING / (name + '-receipt.json'))
        assert signed['id'] == name and signed['exit_code'] == 0 and signed['signature_present'] is True
        assert signed['before'] == result['before'] and signed['after'] == result['after']
        assert sorted(signed['files']) == sorted(recipe['files']) and signed['message'] == recipe['message']
        content = read(SIGNING / (name + '-content.log'))
        assert content['status'] == 'EXACT_COMMITTED_ITEM_VERIFIED'
        assert content['id'] == name and content['commit'] == result['after']
        assert content['parent'] == result['before'] and content['paths'] == len(recipe['files'])
        assert 'Good "git" signature for configured-key' in (SIGNING / (name + '-signature.log')).read_text()
        if 'patch' not in recipe:
            research_count += 1
            for path, pin in recipe['source_pins'].items():
                assert path not in research or research[path] == pin
                research[path] = pin
    current, check = read(LEDGER / 'CURRENT-EPOCH.json'), read(LEDGER / 'CHECK.json')
    terminal = read(LEDGER / 'EXECUTION.json')
    assert terminal['status'] == 'COMPLETE' and terminal['exit'] == 0 and terminal['terminal']
    assert terminal['check_sha256'] == sha(LEDGER / 'CHECK.json')
    assert check['head'] == head and check['current_epoch_sha256'] == sha(LEDGER / 'CURRENT-EPOCH.json')
    assert check['status'] == 'POST_SIGNING_LEDGER_ROOT_VERIFIED'
    assert current['semantic_index']['head'] == head
    assert set(current['pins']) == set(old['pins'])
    assert all(current['pins'][p] == pin for p, pin in old['pins'].items() if p not in check['ledger_paths'])
    assert research_count == 12 and current['committed_research_working_payloads'] == research
    for name, pin in read(LEDGER / 'DESCRIPTOR-STATUS.json')['references'].items():
        assert sha(ROOT / name) == pin
    build = read(BUILD / 'BUILD-EXECUTION.json')
    assert build['status'] == 'COMPLETE' and build['exit'] == 0 and build['terminal'] == 'cd6a0c'
    for label in ['metadata-confirmed', 'export', 'binaries', 'gtest-build']:
        stage = BUILD / (label + '-RESULT.json')
        assert ref(stage) == build['stages'][label]
        result = read(stage)
        assert result['exit'] == 0
        for name, pin in result['logs'].items():
            assert sha(BUILD / name) == pin
    sources = read(BUILD / 'SOURCE-PINS.json')
    assert sources == read(BUILD / 'BUILD-BEFORE.json')['sources'] == read(PREP / 'EXPECTED-SOURCES.json')
    assert sources == read(SIGNING / 'RETRY-BEFORE.json')['source_pins']
    attempt = read(BUILD / 'GTEST-ATTEMPT-EXECUTION.json')
    assert attempt['exit'] == 1 and attempt['native_command_exit'] == 0 and attempt['terminal'] == 'b4222b'
    failure = read(BUILD / 'PACKAGE-FAILED-EXECUTION.json')
    assert failure['exit'] == 1 and failure['terminal'] == '9f0a31' and failure['session'] == 80363
    assert failure['package_validation_created'] is False
    tests = read(BUILD / 'GTEST-RESULT.json')
    assert tests['exit'] == 0 and tests['binaries_before'] == build['binaries']
    assert tests['command'] == ['./mach', 'gtest', 'AnimationOperationArena.*:AnimationRuleSample.*', '--jobs=1']
    app = 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL'
    host = 'objdir-full.noindex/dist/bin/gtest/XUL'
    assert set(build['binaries']) == {app, host,
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL'}
    binaries = dict(build['binaries'])
    binaries[app] = binaries[host]
    assert tests['binaries_after'] == binaries
    assert {n for n in binaries if binaries[n] != build['binaries'][n]} == {app}
    assert all(n in current['pins'] and current['pins'][n] == pin for n, pin in (sources | binaries).items())
    log = (BUILD / 'gtest.log').read_text()
    assert sha(BUILD / 'gtest.log') == tests['log_sha256']
    assert log.index('START_assemble_macos_bundle Nightly.app') < log.index('END_assemble_macos_bundle Nightly.app') < log.index('TEST_START:')
    assert 'AssertionError: GTest build/repackage changed tested binaries' in (BUILD / 'test-driver.log').read_text()
    names = {'AnimationOperationArena.' + n for n in ['NativeArithmeticAndMetadata', 'NativeDifferential']}
    names |= {'AnimationRuleSample.' + n for n in ['FrozenOwnership', 'AdditiveRecipe', 'Replacement',
              'EndpointError', 'MissingUnderlying', 'ConcreteBulk', 'RepeatedRoots', 'InvalidRoots']}
    rows, active = [], None
    for line in log.splitlines():
        match = re.search(r'TEST_START: (\S+)', line)
        if match:
            assert active is None
            active = match[1]
        match = re.search(r'TEST_END: (\S+)', line)
        if match:
            assert active is not None
            rows.append({'name': active, 'status': match[1]})
            active = None
    assert active is None and rows == tests['tests'] and len(rows) == 10
    assert {r['name'] for r in rows} == names and all(r['status'] == 'PASS' for r in rows)
    return adapter, h, old, current, check, sources, binaries


def main():
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    assert not any(n in os.environ for n in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'))
    assert sys.argv[1:] in [['--validate'], ['--prepare']]
    adapter, h, old, current, check, sources, binaries = archives()
    provenance = {
        'build': ref(BUILD / 'BUILD-EXECUTION.json'), 'compile_sources': ref(BUILD / 'SOURCE-PINS.json'),
        'gtest_attempt': ref(BUILD / 'GTEST-ATTEMPT-EXECUTION.json'), 'gtest_results': ref(BUILD / 'GTEST-RESULT.json'),
        'post_signing_epoch': ref(LEDGER / 'CURRENT-EPOCH.json'), 'post_signing_check': ref(LEDGER / 'CHECK.json'),
        'post_signing_manifest': ref(LEDGER / 'FILES.json'), 'post_signing_execution': ref(LEDGER / 'EXECUTION.json'),
        'signing_execution': ref(SIGNING / 'EXECUTION-RESULT.json'), 'signing_manifest': ref(SIGNING / 'FILES.json'),
        'failed_reconciliation': ref(BUILD / 'PACKAGE-FAILED-EXECUTION.json'),
    }
    if sys.argv[1] == '--validate':
        observation = adapter.verify_current(h, ROOT, ENV, current)
        save(HERE / 'PACKAGE-VALIDATION.json', {
            'status': 'POST_SIGNING_EXACT_GTEST_PACKAGE_VALIDATED', 'original_gtest_driver_exit': 1,
            'original_reconciliation_exit': 1, 'native_command_exit': 0,
            'test_reexecution': False, 'binaries_after': binaries,
            'ten_native_tests_pass': True, 'signed_items_verified': 23,
            'observation': observation, 'references': provenance,
            'adapter': read(HERE / 'ADAPTER.json'), 'validator': ref(HERE / 'prepare.py'),
        })
        print('Exact GTest package transition and current signed state validated.')
        return
    validation = read(HERE / 'PACKAGE-VALIDATION.json')
    execution = read(HERE / 'VALIDATION-EXECUTION.json')
    assert execution['status'] == 'COMPLETE' and execution['exit'] == 0 and execution['terminal']
    assert execution['validation_sha256'] == sha(HERE / 'PACKAGE-VALIDATION.json')
    assert validation['status'] == 'POST_SIGNING_EXACT_GTEST_PACKAGE_VALIDATED'
    assert validation['references'] == provenance and validation['binaries_after'] == binaries
    assert validation['validator'] == ref(HERE / 'prepare.py')
    assert validation['adapter'] == read(HERE / 'ADAPTER.json')
    provenance['packaging_validation'] = ref(HERE / 'PACKAGE-VALIDATION.json')
    provenance['packaging_execution'] = ref(HERE / 'VALIDATION-EXECUTION.json')
    candidate = adapter.derive(old, current, check, sources, binaries, check['ledger_paths'], provenance)
    observation = adapter.verify_current(h, ROOT, ENV, candidate)
    assert set(read(PREP / 'REQUIRED-ROLES.json')) <= set(candidate['pins'])
    assert set(read(PREP / 'EXPECTED-UNTRACKED.json')) == set(candidate['untracked_native'])
    TARGET.mkdir()
    for path in PREP.iterdir():
        if path.is_file() and path.name != 'INPUTS.json':
            shutil.copyfile(path, TARGET / path.name)
    save(TARGET / 'CANDIDATE-EPOCH.json', candidate)
    inputs = read(PREP / 'INPUTS.json')
    inputs.update(ready=True, execution_epoch=ref(TARGET / 'CANDIDATE-EPOCH.json'))
    save(TARGET / 'INPUTS.json', inputs)
    save(HERE / 'PREPARATION-RESULT.json', {
        'status': 'CAPTURE_PREPARED_NOT_ACTIVATED', 'target': str(TARGET.relative_to(ROOT)),
        'candidate': ref(TARGET / 'CANDIDATE-EPOCH.json'), 'inputs': ref(TARGET / 'INPUTS.json'),
        'observation': observation, 'browser_run': False,
    })
    print('Capture prepared against signed state; root activation still required.')


if __name__ == '__main__':
    main()
