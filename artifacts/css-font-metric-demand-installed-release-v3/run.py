import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import time

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'artifacts/css-font-metric-demand-installed-release-runtime-3'
PHASE = ROOT / 'artifacts/css-font-metric-demand-installed-stage-v2'
APP = Path('/Applications/Firefox.app/Contents')
PAGE = '/css/css-properties-values-api/registered-font-metric-demand.tentative.html'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def save(name, value):
    with (OUTPUT / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')

def app_snapshot():
    files = {}
    for relative in ['Info.plist', 'MacOS/firefox', 'MacOS/XUL', 'Resources/application.ini', 'Resources/platform.ini']:
        path = APP / relative
        stat = path.stat()
        files[relative] = {'sha256': sha(path), 'bytes': stat.st_size, 'identity': [stat.st_dev, stat.st_ino], 'resolved': str(path.resolve())}
    ini = configparser.ConfigParser(interpolation=None)
    ini.read(APP / 'Resources/application.ini')
    info = plistlib.loads((APP / 'Info.plist').read_bytes())
    return {'files': files, 'application': dict(ini['App']), 'version': info['CFBundleShortVersionString'], 'bundle_version': info['CFBundleVersion']}

def main():
    assert sys.argv[1:] == ['--run'] and not OUTPUT.exists()
    control_path = ROOT / 'artifacts/css-keyframe-typed-attribute-demand-runtime-v1/process_control.py'
    assert sha(control_path) == 'b57e5e2506b89d48e30c958b2aa04e375e853e3ec68386afe3071a349c1d969a'
    spec = importlib.util.spec_from_file_location('installed_process_control', control_path)
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    assert sha(ROOT / 'artifacts/css-font-metric-demand-installed-stage-v2/STAGED-RESOURCES.json') == '0f70aaa2b0c719b5b914ade8a55df325b67c27360c84a5ab5d9525770b861113'
    assert sha(ROOT / 'artifacts/css-font-metric-demand-installed-stage-v2/wptrunner.ini') == 'd9396664c5839f532e5263bd19386fe79214ee8de0fa7d64e6511ae0d1b69f79'
    assert sha(ROOT / 'artifacts/css-registered-font-metric-demand-probe-v2/ROSTER.json') == '4ae4b7853fc90f9d4a59b69cedc68a63976b43fd5f66e65edd1519cf0090795f'
    staged = json.loads((PHASE / 'STAGED-RESOURCES.json').read_bytes())
    assert all(sha(PHASE / name) == pin for name, pin in staged.items())
    roster = json.loads((ROOT / 'artifacts/css-registered-font-metric-demand-probe-v2/ROSTER.json').read_bytes())
    assert list(roster) == [PAGE] and len(roster[PAGE]) == 13
    assert not (ROOT / 'artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock').exists()
    OUTPUT.mkdir()
    before = app_snapshot()
    save('APP-PRE.json', before)
    assert before['version'] == '158.0'
    run_info = OUTPUT / 'run-info'
    run_info.mkdir()
    temporary = Path(tempfile.mkdtemp(prefix='css-font-metric-matrix-', dir='/private/tmp'))
    identity = [temporary.stat().st_dev, temporary.stat().st_ino]
    command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless', '--processes=1', '--no-manifest-update', '--no-manifest-download', '--no-install-fonts', '--no-enable-webtransport-h3', '--browser-channel=stable', '--binary=' + str(APP / 'MacOS/firefox'), '--config=' + str(PHASE / 'wptrunner.ini'), '--run-info=' + str(run_info), '--prefs-root=' + str(ROOT / 'testing/profiles'), '--log-raw=' + str(OUTPUT / 'raw.jsonl'), '--include=' + PAGE]
    save('COMMAND.json', {'command': command, 'temporary_root': str(temporary), 'temporary_identity': identity, 'timeout_seconds': 180, 'script_sha256': sha(Path(__file__))})
    profiles = json.loads((ROOT / 'testing/profiles/profiles.json').read_bytes())['web-platform-tests']
    save('PROFILE-INPUTS.json', {name: {'sha256': sha(ROOT / 'testing/profiles' / name / 'user.js')} for name in profiles if name != 'unittest-features'})
    prefs = OUTPUT / 'profile-preferences'
    prefs.mkdir()
    samples = {}
    def capture_preferences():
        for path in temporary.rglob('*.js'):
            if path.name not in ('prefs.js', 'user.js') or path.is_symlink():
                continue
            try:
                body = path.read_bytes()
            except FileNotFoundError:
                continue
            digest = hashlib.sha256(body).hexdigest()
            name = digest + '-' + path.name
            if name not in samples:
                (prefs / name).write_bytes(body)
                samples[name] = {'source': str(path.relative_to(temporary)), 'sha256': digest, 'bytes': len(body)}
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary), MOZ_DISABLE_SAFE_MODE_KEY='1', MOZ_DISABLE_UPDATE_PROCESSING='1')
    process, code, error, cleanup = None, None, None, None
    try:
        with (OUTPUT / 'wpt.log').open('x') as stream:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            save('PROCESS.json', {'pid': process.pid, 'pgid': process.pid})
            deadline = time.monotonic() + 180
            while process.poll() is None:
                capture_preferences()
                assert time.monotonic() < deadline, 'WPT timeout'
                time.sleep(0.2)
            code = process.wait()
            capture_preferences()
    except BaseException as exc:
        error = repr(exc)
    finally:
        try:
            cleanup = control.terminate(process)
            assert cleanup['owned_group_absent']
            capture_preferences()
            assert not temporary.is_symlink() and [temporary.stat().st_dev, temporary.stat().st_ino] == identity
            shutil.rmtree(temporary)
            cleanup['temporary_root_removed'] = True
        except BaseException as exc:
            error = error or repr(exc)
        save('CLEANUP.json', cleanup)
        save('PROFILE-SAMPLES.json', samples)
    after = app_snapshot()
    save('APP-POST.json', after)
    preserved = before == after and all(sha(PHASE / name) == pin for name, pin in staged.items())
    raw = OUTPUT / 'raw.jsonl'
    events = [json.loads(line) for line in raw.read_text().splitlines()] if raw.exists() else []
    rows = [row for row in events if row.get('action') == 'test_status']
    ends = [row for row in events if row.get('action') == 'test_end']
    run_infos = [r.get('run_info') for r in events if r.get('action') == 'suite_start']
    browser_bound = len(run_infos) == 1 and run_infos[0].get('browser_build_id') == before['application']['buildid']
    complete = code in (0, 1) and browser_bound and len(rows) == 13 and {(r['test'], r['subtest']) for r in rows} == {(PAGE, name) for name in roster[PAGE]} and len(ends) == 1 and ends[0]['test'] == PAGE and ends[0]['status'] == 'OK' and all(r['status'] in ('PASS', 'FAIL') for r in rows)
    save('RESULT.json', {'complete': complete, 'exit': code, 'error': error, 'rows': rows, 'endings': ends, 'run_info': [r.get('run_info') for r in events if r.get('action') == 'suite_start'], 'app_and_staged_inputs_preserved': preserved, 'cleanup': cleanup, 'preference_samples_saved': len(samples), 'raw_sha256': sha(raw) if raw.exists() else None, 'native_acceptance': False, 'role': 'installed-release-WPT-stable-profile', 'prerequisite_failures_require_separate_triage': True})
    assert preserved and cleanup and cleanup.get('owned_group_absent') and cleanup.get('temporary_root_removed') and error is None and complete and any(name.endswith('-user.js') for name in samples)
    print('Installed release observation complete; ordinary FAIL rows retained')

if __name__ == '__main__':
    main()
