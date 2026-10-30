import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def run(root, here, output, role, policy, env, verify, owned, cancelled, original=None):
    settings = policy['wpt']
    metadata_helper = load('activation_metadata', root / settings['metadata_helper'])
    checks = load('activation_checks', root / settings['checks_helper'])
    control = load('activation_wpt_control', root / settings['control_helper'])
    assessor = load('activation_assessor', here / 'assess.py')
    expected = settings['expected_subtests']
    targets = settings['target_subtests']
    assert expected and set(targets) <= set(expected)
    assert all(set(names) <= set(expected[test]) for test, names in targets.items())
    phase_policy = dict(settings, tests={test: 'testharness' for test in expected}, held_subtests={})
    phase_policy['regression_subtests'] = {test: [name for name in names if name not in targets.get(test, [])] for test, names in expected.items()}
    phase_policy['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    output.mkdir()
    before = verify()
    app_before = metadata_helper.application_metadata(root / settings['application_ini'], settings['phase_revisions'][role])
    app_before.update(build_revision=app_before['revision'], harness_revision=settings['harness_revision'], source_role=role)
    binaries = {name: sha(root / name) for name in policy['rebuilt_binaries']}
    save(output / 'PRE.json', before)
    save(output / 'APPLICATION-METADATA.json', app_before)
    save(output / 'BINARY-PINS.json', binaries)
    save(output / 'ASSESSMENT-POLICY.json', phase_policy)
    tests = output / 'tests'
    tests.mkdir()
    for name, record in settings['resources'].items():
        part = Path(name)
        assert not part.is_absolute() and '..' not in part.parts
        source = root / record['path']
        assert source.is_file() and not source.is_symlink() and sha(source) == record['sha256']
        target = tests / part
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    assert not (tests / 'tools').exists()
    (tests / 'tools').symlink_to(root / 'testing/web-platform/tests/tools', target_is_directory=True)
    server = json.loads((root / settings['server_config']['path']).read_bytes())
    assert sha(root / settings['server_config']['path']) == settings['server_config']['sha256']
    server['ports'] = {name: ['auto'] * count for name, count in settings['server_protocols'].items()}
    save(tests / 'config.json', server)
    metadata = output / 'metadata'
    metadata.mkdir()
    manifest = root / settings['manifest']['path']
    assert sha(manifest) == settings['manifest']['sha256']
    (metadata / 'MANIFEST.json').write_bytes(manifest.read_bytes())
    for name, record in settings['metadata'].items():
        target = metadata / name
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        if record['sha256'] is None:
            assert not (root / record['path']).exists()
        else:
            assert sha(root / record['path']) == record['sha256']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((root / record['path']).read_bytes())
    config = configparser.ConfigParser(interpolation=None)
    config.read(root / settings['wpt_config'])
    for name in list(config.sections()):
        if name.startswith('manifest:'):
            config.remove_section(name)
    config['paths']['run_info'] = str(root / 'objdir-full.noindex')
    config['paths']['prefs'] = str(root / 'testing/profiles')
    config['web-platform-tests']['sync_path'] = str(output / 'unused-sync')
    config['manifest:upstream'] = {'tests': str(tests), 'metadata': str(metadata), 'url_base': '/', 'manifest': str(metadata / 'MANIFEST.json')}
    config_path = output / 'wptrunner.ini'
    with config_path.open('x') as stream:
        config.write(stream)
    temporary = Path(tempfile.mkdtemp(prefix='css-easing-paired-', dir='/private/tmp'))
    identity = (temporary.stat().st_dev, temporary.stat().st_ino)
    phase_env = dict(env, TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary), MOZ_DISABLE_SAFE_MODE_KEY='1', MOZ_DISABLE_UPDATE_PROCESSING='1')
    command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless', '--processes=1', '--no-manifest-update', '--no-manifest-download', '--binary=' + str(root / settings['binary']), '--config=' + str(config_path), '--run-info=' + str(root / 'objdir-full.noindex'), '--prefs-root=' + str(root / 'testing/profiles'), '--log-raw=' + str(output / 'raw.jsonl')]
    command.extend('--include=' + test for test in expected)
    save(output / 'COMMAND.json', {'command': command, 'temporary_root': str(temporary), 'temporary_identity': identity, 'timeout_seconds': settings['timeout_seconds']})
    process, code, error, cleanup = None, None, None, None
    try:
        with (output / 'wpt.log').open('x') as stream:
            process = subprocess.Popen(command, cwd=root, env=phase_env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            owned['wpt'] = process.pid
            save(output / 'PROCESS.json', {'pid': process.pid, 'pgid': process.pid})
            deadline = time.monotonic() + settings['timeout_seconds']
            while process.poll() is None:
                assert not cancelled() and time.monotonic() < deadline, 'WPT cancelled or timed out'
                time.sleep(0.2)
            code = process.wait()
    except BaseException as exc:
        error = repr(exc)
    finally:
        try:
            cleanup = control.terminate(process)
            assert cleanup['owned_group_absent']
            owned.pop('wpt', None)
            assert not temporary.is_symlink() and (temporary.stat().st_dev, temporary.stat().st_ino) == identity
            shutil.rmtree(temporary)
            cleanup['temporary_root_removed'] = True
        except BaseException as exc:
            error = error or repr(exc)
        save(output / 'CLEANUP.json', cleanup)
    after = verify()
    app_after = metadata_helper.application_metadata(root / settings['application_ini'], settings['phase_revisions'][role])
    app_after.update(build_revision=app_after['revision'], harness_revision=settings['harness_revision'], source_role=role)
    preserved = before == after and app_before == app_after and {name: sha(root / name) for name in binaries} == binaries
    save(output / 'POST.json', after)
    save(output / 'APPLICATION-METADATA-POST.json', app_after)
    events = [json.loads(line) for line in (output / 'raw.jsonl').read_text().splitlines()]
    if original is not None:
        assert original == root / policy['baseline_binding']['directory'] / 'original-wpt'
        comparison = load('strict_original_comparison', here / 'comparison.py')
        replay = comparison.replay_original(root, policy, assessor, checks)
    else:
        replay = None
    assessment = assessor.assess(events, code, phase_policy, checks, original=replay, run_binding=app_before)
    save(output / 'ASSESSMENT.json', assessment)
    success = error is None and preserved and cleanup and cleanup.get('temporary_root_removed') and assessment['complete']
    save(output / 'RESULT.json', {'success': bool(success), 'exit': code, 'execution_error': error, 'preservation_verified': preserved, 'comparison_gate_passed': assessment['comparison_gate_passed'], 'native_fix_acceptance': False, 'success_scope': 'complete observation and preservation; comparison verdict retained separately'})
    assert success, (error, preserved, assessment['errors'], assessment['comparison_errors'])
    return {'assessment_sha256': sha(output / 'ASSESSMENT.json'), 'raw_sha256': sha(output / 'raw.jsonl'), 'result_sha256': sha(output / 'RESULT.json')}
