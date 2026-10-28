import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def git(directory, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', *args], cwd=directory, env=ENV)


def snapshot():
    files = {}
    for name in policy['protected_paths']:
        path = ROOT / name
        st = path.lstat()
        assert stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode)
        files[name] = {'sha256': digest(path), 'identity': [st.st_dev, st.st_ino], 'mode': st.st_mode,
                       'symlink': os.readlink(path) if path.is_symlink() else None}
    controls = {name: digest(ROOT / 'artifacts/css-registered-number-native-runtime-v1' / name)
                for name in ['CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json']}
    indexes = {}
    for name, directory in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
        fields = {'head': git(directory, 'rev-parse', 'HEAD').decode().strip()}
        for key, args in [('entries', ['ls-files', '--stage', '-z']), ('flags', ['ls-files', '-v', '-z']),
                          ('working', ['diff', '--binary', '--full-index']), ('cached', ['diff', '--cached', '--binary', '--full-index']),
                          ('untracked', ['ls-files', '--others', '--exclude-standard', '-z'])]:
            body = git(directory, *args)
            if key == 'untracked' and name == 'root':
                prefix = (policy['output'] + '/').encode()
                body = b'\0'.join(item for item in body.split(b'\0') if not item.startswith(prefix))
            fields[key] = hashlib.sha256(body).hexdigest()
        indexes[name] = fields
    return {'files': files, 'controls': controls, 'indexes': indexes}


policy = read(HERE / 'BASELINE-POLICY.json')
assert policy['execution_enabled'] and len(sys.argv) == 2
assert digest(HERE / 'FILES.json') == sys.argv[1]
for name, pin in read(HERE / 'FILES.json').items():
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    assert not (HERE / name).is_symlink() and digest(HERE / name) == pin
assert not any(os.environ.get(k) for k in ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'MOZ_PROFILE'])
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
           MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'),
           MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           MOZ_DISABLE_SAFE_MODE_KEY='1', MOZ_DISABLE_UPDATE_PROCESSING='1')
assert digest(ROOT / policy['observation_path']) == policy['observation_sha256']
assert digest(ROOT / policy['control_helper']) == policy['control_sha256']
spec = importlib.util.spec_from_file_location('baseline_control', ROOT / policy['control_helper'])
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)
output = ROOT / policy['output']
assert output.parent == ROOT / 'artifacts' and not os.path.lexists(output)
assert not os.path.lexists(ROOT / 'artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock')
before = snapshot()
assert before['controls']['CURRENT-EPOCH.json'] == policy['epoch_sha256']
assert before['indexes']['root']['head'] == policy['head']
assert before['indexes']['root']['cached'] == hashlib.sha256(b'').hexdigest()
for name, pin in policy['expected_pins'].items():
    assert before['files'][name]['sha256'] == pin
output.mkdir()
save(output / 'PRE.json', before)
tests = output / 'tests'
page = tests / policy['target'].lstrip('/')
page.parent.mkdir(parents=True)
page.write_bytes((HERE / 'fixture/baseline.html').read_bytes())
(page.parent / 'record.py').write_bytes((HERE / 'fixture/record.py').read_bytes())
(page.parent / 'observation.js').write_bytes((ROOT / policy['observation_path']).read_bytes())
for name, pin in policy['resources'].items():
    original = ROOT / 'testing/web-platform/tests' / name
    assert digest(original) == pin
    target = tests / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(original.read_bytes())
(tests / 'tools').symlink_to(ROOT / 'testing/web-platform/tests/tools', target_is_directory=True)
server = read(ROOT / 'testing/web-platform/tests/config.json')
server['ports'] = {name: ['auto'] * count for name, count in policy['server_protocols'].items()}
save(tests / 'config.json', server)
metadata = output / 'metadata'
metadata.mkdir()
save(metadata / 'MANIFEST.json', read(HERE / 'SUBSET-MANIFEST.json'))
config = configparser.ConfigParser(interpolation=None)
config.read(ROOT / policy['wpt_config'])
for name in list(config.sections()):
    if name.startswith('manifest:'):
        config.remove_section(name)
config['paths']['run_info'] = str(ROOT / 'objdir-full.noindex')
config['paths']['prefs'] = str(ROOT / 'testing/profiles')
config['web-platform-tests']['sync_path'] = str(output / 'unused-sync')
config['manifest:upstream'] = {'tests': str(tests), 'metadata': str(metadata), 'url_base': '/', 'manifest': str(metadata / 'MANIFEST.json')}
config_path = output / 'wptrunner.ini'
with config_path.open('x') as stream:
    config.write(stream)
temporary = Path(tempfile.mkdtemp(prefix='css-round-infinite-baseline-', dir='/private/tmp'))
temporary_identity = (temporary.stat().st_dev, temporary.stat().st_ino)
ENV.update(TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary), ROUND_BASELINE_RECORD=str(output / 'observation.json'))
command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless', '--processes=1',
           '--no-manifest-update', '--no-manifest-download', '--binary=' + policy['binary'],
           '--config=' + str(config_path), '--run-info=' + str(ROOT / 'objdir-full.noindex'),
           '--prefs-root=' + str(ROOT / 'testing/profiles'), '--log-raw=' + str(output / 'raw.jsonl'), '--include=' + policy['target']]
save(output / 'COMMAND.json', {'command': command, 'temporary_root': str(temporary), 'timeout_seconds': 300})
process, code, error, cleanup = None, None, None, None
stopped = [False]
def stop(signum, frame):
    stopped[0] = True
for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, stop)
try:
    with (output / 'wpt.log').open('x') as log:
        process = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        save(output / 'PROCESS.json', {'pid': process.pid, 'pgid': process.pid})
        deadline = time.monotonic() + 300
        while process.poll() is None:
            if stopped[0] or time.monotonic() >= deadline:
                raise RuntimeError('Cancelled or baseline deadline exceeded')
            time.sleep(0.2)
        code = process.wait()
except BaseException as exc:
    error = repr(exc)
finally:
    try:
        cleanup = control.terminate(process)
        assert cleanup['owned_group_absent']
        assert not temporary.is_symlink() and (temporary.stat().st_dev, temporary.stat().st_ino) == temporary_identity
        shutil.rmtree(temporary)
        cleanup['temporary_root_removed'] = True
    except BaseException as exc:
        error = error or repr(exc)
    save(output / 'CLEANUP.json', cleanup)
after = snapshot()
save(output / 'POST.json', after)
preserved = after == before
assessment_error = None
summary = {}
try:
    events = [json.loads(line) for line in (output / 'raw.jsonl').read_text().splitlines()]
    rows = [e for e in events if e.get('action') == 'test_status']
    ends = [e for e in events if e.get('action') == 'test_end']
    expected = {f'{kind} {mode} {sign}' for mode in ['nearest', 'up', 'down', 'to-zero'] for sign in [1, -1]
                for kind in ['nan-step', 'relative-leaf-step', 'fixed-finite-step']}
    assert len(rows) == 24 and {e['subtest'] for e in rows} == expected
    assert all(e['test'] == policy['target'] and e['status'] in ['PASS', 'FAIL'] for e in rows)
    assert len(ends) == 1 and ends[0]['test'] == policy['target'] and ends[0]['status'] == 'OK'
    assert not any(e.get('action') in ['crash', 'process_error'] or (e.get('action') == 'log' and e.get('level') == 'ERROR') for e in events)
    assert code in [0, 1]
    observation = read(output / 'observation.json')
    assert observation['caseCount'] == 24 and observation['snapshotCount'] == len(observation['snapshots']) == 72
    identities = {(x['kind'], x['mode'], x['sign'], x['phase']) for x in observation['snapshots']}
    assert identities == {(kind, mode, sign, phase) for kind in ['nan-step', 'relative-leaf-step', 'fixed-finite-step']
                          for mode in ['nearest', 'up', 'down', 'to-zero'] for sign in [1, -1] for phase in range(3)}
    calibration_errors = []
    for row in observation['snapshots']:
        c = row['inputCalibration']
        expected_value = 0 if row['kind'] == 'nan-step' or (row['kind'] == 'relative-leaf-step' and row['font'] == 0) else 0.5 + 0.25 * row['sign']
        valid = row['expected'] == expected_value
        valid = valid and row['font'] == [8, 0, 8][row['phase']] and row['supported'] and row['specified'] and row['actual'] == row['repeated']
        valid = valid and c['font'] == c['width'] == str(row['font']) + 'px' and c['nanSupported'] and c['nanSpecified']
        valid = valid and float(c['nanEncoding']) == 0 and float(row['literal']) == row['expected']
        if not valid:
            calibration_errors.append([row['kind'], row['mode'], row['sign'], row['phase']])
    assert not calibration_errors, calibration_errors
    summary = {'pass': sum(e['status'] == 'PASS' for e in rows), 'fail': sum(e['status'] == 'FAIL' for e in rows),
               'snapshots': 72, 'calibration_errors': calibration_errors, 'known_mismatches_are_observations': True}
except BaseException as exc:
    assessment_error = repr(exc)
success = error is None and assessment_error is None and preserved and cleanup and cleanup.get('temporary_root_removed')
save(output / 'RESULT.json', {'success': bool(success), 'harness_exit': code, 'execution_error': error,
     'assessment_error': assessment_error, 'preservation_verified': preserved, 'summary': summary, 'native_fix_acceptance': False})
assert success, (error, assessment_error, preserved)
print(json.dumps(summary))
