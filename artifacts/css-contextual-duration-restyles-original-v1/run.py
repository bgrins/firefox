import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    assert len(sys.argv) == 2 and sha(HERE / 'FILES.json') == sys.argv[1]
    for name, pin in read(HERE / 'FILES.json').items():
        assert sha(HERE / name) == pin
    policy = read(HERE / 'POLICY.json')
    for name, pin in policy['references'].items():
        assert sha(ROOT / name) == pin, name
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'MOZ_PROFILE'))
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
               MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'),
               MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')
    state = load('state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
    control = load('control', 'artifacts/css-keyframe-typed-attribute-demand-runtime-v1/process_control.py')
    metadata = load('metadata', 'artifacts/css-round-context-quotient-paired-wpt-runner-v2/run.py')
    epoch = read(RUNTIME / 'CURRENT-EPOCH.json')
    assert epoch['semantic_index']['head'] == policy['head'] and epoch['staged_working'] == {}

    def verify():
        assert {n: sha(RUNTIME / n) for n in policy['controls']} == policy['controls']
        for name, pin in {**policy['source_pins'], **policy['references']}.items():
            assert sha(ROOT / name) == pin, name
        assert sha(ROOT / policy['app_ini']) == policy['app_ini_sha256']
        return state.a.verify_current(state.h, ROOT, env, epoch)

    before = verify()
    app = metadata.application_metadata(ROOT / policy['app_ini'], policy['build_revision'])
    save('PRE.json', before)
    save('APPLICATION-METADATA.json', app)
    command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'mochitest',
               '--headless', '--flavor=plain', '--timeout=180',
               '--appname=' + str(ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'),
               '--log-raw=' + str(HERE / 'raw.jsonl'), policy['selector']]
    save('COMMAND.json', {'command': command, 'external_timeout_seconds': policy['timeout_seconds']})
    stopped = [False]
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: stopped.__setitem__(0, True))
    process, code, error = None, None, None
    try:
        with (HERE / 'mochitest.log').open('x') as stream:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            save('PROCESS.json', {'pid': process.pid, 'pgid': process.pid})
            deadline = time.monotonic() + policy['timeout_seconds']
            while process.poll() is None:
                assert not stopped[0] and time.monotonic() < deadline, 'Mochitest cancelled or timed out'
                time.sleep(0.2)
            code = process.wait()
    except BaseException as exc:
        error = repr(exc)
    finally:
        cleanup = control.terminate(process)
        save('CLEANUP.json', cleanup)
        assert cleanup['owned_group_absent']
    after = verify()
    app_after = metadata.application_metadata(ROOT / policy['app_ini'], policy['build_revision'])
    save('POST.json', after)
    save('APPLICATION-METADATA-POST.json', app_after)
    assert before == after and app == app_after
    save('RESULT.json', {'exit': code, 'execution_error': error,
                         'preservation_verified': True, 'owned_group_absent': True,
                         'raw_present': (HERE / 'raw.jsonl').is_file(),
                         'native_acceptance': False})
    assert error is None
    print('Original restyle-count observation completed; test outcome retained separately')


if __name__ == '__main__':
    main()
