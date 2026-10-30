import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert len(sys.argv) == 2 and sha(HERE / 'FILES.json') == sys.argv[1]
    files = read(HERE / 'FILES.json')
    policy = read(HERE / 'POLICY.json')
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
               MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'),
               MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'))
    state = load('minmax_state', policy['state_helper'])
    epoch = read(RUNTIME / 'CURRENT-EPOCH.json')
    assert epoch['semantic_index']['head'] == policy['head'] and epoch['staged_working'] == {}
    assert epoch['accepted_pow_special_value']['fix'] == 150
    assert epoch['pow_special_value_transition']['accepted']
    built = read(ROOT / policy['build_epoch'])
    bound = [name for name in built['pins']
             if name.startswith(('servo/', 'layout/', 'dom/')) or name in policy['rebuilt_binaries']]
    assert bound and all(epoch['pins'][name] == built['pins'][name] for name in bound)

    def verify():
        assert sha(HERE / 'FILES.json') == sys.argv[1]
        for name, pin in files.items():
            assert sha(HERE / name) == pin, name
        for name, pin in policy['references'].items():
            assert sha(ROOT / name) == pin, name
        assert {name: sha(RUNTIME / name) for name in policy['controls']} == policy['controls']
        assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
        return state.a.verify_current(state.h, ROOT, env, epoch)

    output = ROOT / policy['output']
    assert not output.exists() and not output.is_symlink()
    output.mkdir()
    stopped = [False]
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: stopped.__setitem__(0, True))
    runner = load('minmax_wpt', policy['wpt_helper'])
    owned = {}
    phase = runner.run(ROOT, HERE, output / 'original-wpt', 'original', policy,
                       env, verify, owned, lambda: stopped[0])
    assert not owned
    runner.save(output / 'RESULT.json', {
        'phase': phase, 'build_native_and_binary_pin_count': len(bound),
        'preservation_verified': True, 'native_fix_accepted': False,
        'source_or_canonical_mutation': False,
    })
    print('Completed min/max branch observation; outcomes recorded without acceptance', flush=True)


if __name__ == '__main__':
    main()
