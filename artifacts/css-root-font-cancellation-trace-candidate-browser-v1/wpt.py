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


def prepare_inputs(root, output, settings, role):
    tests = output / 'tests'
    mozilla = output / 'mozilla-tests'
    tests.mkdir()
    mozilla.mkdir()
    for url, record in settings['resources'].items():
        assert url.startswith('/') and '..' not in Path(url).parts
        assert not url.startswith('/__research__/zoom/')
        source = root / record['path']
        assert source.is_file() and not source.is_symlink() and sha(source) == record['sha256']
        target = mozilla / url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else tests / url[1:]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    assert not (tests / 'tools').exists()
    (tests / 'tools').symlink_to(root / 'testing/web-platform/tests/tools', target_is_directory=True)
    server = json.loads((root / settings['server_config']['path']).read_bytes())
    assert sha(root / settings['server_config']['path']) == settings['server_config']['sha256']
    server['ports'] = {name: ['auto'] * count for name, count in settings['server_protocols'].items()}
    save(tests / 'config.json', server)
    roots = {}
    for name, url, test_root in [('portable', '/', tests), ('mozilla', '/_mozilla/', mozilla)]:
        metadata = output / ('metadata' if name == 'portable' else 'mozilla-metadata')
        metadata.mkdir()
        manifest = root / settings['manifests'][name]['path']
        assert sha(manifest) == settings['manifests'][name]['sha256']
        (metadata / 'MANIFEST.json').write_bytes(manifest.read_bytes())
        for relative, record in settings['metadata'][name].items():
            assert not Path(relative).is_absolute() and '..' not in Path(relative).parts
            if record['sha256'] is None:
                assert record.get('require_absent_in_staged_root') is True and record['path'] is None
                assert not (metadata / relative).exists() and not (metadata / relative).is_symlink()
            else:
                assert sha(root / record['path']) == record['sha256']
                target = metadata / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((root / record['path']).read_bytes())
        roots[name] = {'tests': str(test_root), 'metadata': str(metadata), 'url_base': url,
                       'manifest': str(metadata / 'MANIFEST.json')}
    config = configparser.ConfigParser(interpolation=None)
    config.read(root / settings['wpt_config'])
    for name in list(config.sections()):
        if name.startswith('manifest:'):
            config.remove_section(name)
    config['paths']['run_info'] = str(root / 'objdir-full.noindex')
    config['paths']['prefs'] = str(root / 'testing/profiles')
    config['web-platform-tests']['sync_path'] = str(output / 'unused-sync')
    config['manifest:upstream'] = roots['portable']
    config['manifest:mozilla'] = roots['mozilla']
    config_path = output / 'wptrunner.ini'
    with config_path.open('x') as stream:
        config.write(stream)
    capture = None
    if settings['capture'] is not None:
        helper = root / settings['capture']['path']
        assert sha(helper) == settings['capture']['sha256']
        capture = load('required_zoom_capture', helper)
        capture.install(tests, output, role)
        for url, record in settings['install_managed_resources'].items():
            assert sha(tests / url[1:]) == record['sha256'] == sha(root / record['path'])
    staged = {}
    for name, info in roots.items():
        for folder in ['tests', 'metadata']:
            for path in Path(info[folder]).rglob('*'):
                if path.is_file() and not path.is_symlink():
                    staged[str(path.relative_to(output))] = sha(path)
    save(output / 'STAGED-RESOURCES.json', staged)
    return config_path, capture


def run(root, here, output, role, policy, env, verify, owned, cancelled, original=None, lane="ordinary"):
    settings = policy['wpt_lanes'][lane]
    metadata_helper = load('activation_metadata', root / settings['metadata_helper'])
    checks = load('activation_checks', root / settings['checks_helper'])
    control = load('activation_wpt_control', root / settings['control_helper'])
    assessor = load('activation_assessor', here / 'assess.py')
    expected = settings['expected_subtests']
    targets = settings['target_subtests']
    assert expected and set(targets) <= set(expected)
    assert all(set(names) <= set(expected[test]) for test, names in targets.items())
    comparison = load('paired_comparison', here / 'comparison.py')
    assert role == 'candidate'
    builds = {'candidate': comparison.build_binding(root, here, output.parent, policy, 'candidate')}
    phase_policy = comparison.phase_policy(settings, builds, policy['head'])
    output.mkdir()
    before = verify()
    app_before = metadata_helper.application_metadata(root / settings['application_ini'], settings['phase_revisions'][role])
    app_before.update(build_revision=app_before['revision'], harness_revision=settings['harness_revision'], source_role=role)
    binaries = {name: sha(root / name) for name in policy['rebuilt_binaries']}
    assert app_before == builds[role]['application_metadata'] and binaries == builds[role]['binaries']
    save(output / 'PRE.json', before)
    save(output / 'APPLICATION-METADATA.json', app_before)
    save(output / 'BINARY-PINS.json', binaries)
    save(output / 'ASSESSMENT-POLICY.json', phase_policy)
    config_path, capture = prepare_inputs(root, output, settings, role)
    temporary = Path(tempfile.mkdtemp(prefix='css-easing-paired-', dir='/private/tmp'))
    identity = (temporary.stat().st_dev, temporary.stat().st_ino)
    phase_env = dict(env, TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary), MOZ_DISABLE_SAFE_MODE_KEY='1', MOZ_DISABLE_UPDATE_PROCESSING='1')
    command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless', '--processes=1', '--no-manifest-update', '--no-manifest-download', '--no-install-fonts', '--no-enable-webtransport-h3', '--binary=' + str(root / settings['binary']), '--config=' + str(config_path), '--run-info=' + str(root / 'objdir-full.noindex'), '--prefs-root=' + str(root / 'testing/profiles'), '--log-raw=' + str(output / 'raw.jsonl')]
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
    staged = json.loads((output / 'STAGED-RESOURCES.json').read_bytes())
    assert all(sha(output / name) == digest for name, digest in staged.items())
    events = [json.loads(line) for line in (output / 'raw.jsonl').read_text().splitlines()]
    assert role == 'candidate' and original is None
    replay = None
    capture_result = None
    if capture is not None:
        assert error is None and cleanup and cleanup.get('owned_group_absent') and cleanup.get('temporary_root_removed')
        capture_result = capture.review(output, events)
        assert capture.replay(output, events) == capture_result
        assert original is not None
        original_events = [json.loads(line) for line in (original / 'raw.jsonl').read_text().splitlines()]
        original_capture = capture.replay(original, original_events)
        assert original_capture == json.loads((original / 'ZOOM-OBSERVATION.json').read_bytes())
        save(output / 'ZOOM-COMPARISON.json', capture.compare(original_capture, capture_result))
    assessment = assessor.assess(events, code, phase_policy, checks, original=replay, run_binding=app_before)
    save(output / 'ASSESSMENT.json', assessment)
    behavior = comparison.behavior(replay, assessment, assessor.signature) if replay is not None else None
    save(output / 'BEHAVIOR-COMPARISON.json', behavior)
    success = error is None and preserved and cleanup and cleanup.get('temporary_root_removed') and assessment['complete']
    save(output / 'RESULT.json', {'success': bool(success), 'exit': code, 'execution_error': error, 'preservation_verified': preserved, 'comparison_gate_passed': assessment['comparison_gate_passed'], 'publication_observation_gate': behavior['publication_observation_gate'] if behavior is not None else None, 'all_signatures_equal': behavior['all_signatures_equal'] if behavior is not None else None, 'required_zoom_capture_complete': capture_result is not None if capture is not None else None, 'lane': lane, 'native_fix_acceptance': False, 'success_scope': 'complete observation and preservation; comparison verdict retained separately'})
    assert success, (error, preserved, assessment['errors'], assessment['comparison_errors'])
    return {'lane': lane, 'behavior_sha256': sha(output / 'BEHAVIOR-COMPARISON.json'), 'zoom_comparison_sha256': sha(output / 'ZOOM-COMPARISON.json') if capture_result is not None else None, 'zoom_observation_sha256': sha(output / 'ZOOM-OBSERVATION.json') if capture_result is not None else None, 'assessment_sha256': sha(output / 'ASSESSMENT.json'), 'raw_sha256': sha(output / 'raw.jsonl'), 'result_sha256': sha(output / 'RESULT.json')}
