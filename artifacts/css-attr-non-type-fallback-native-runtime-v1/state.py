import copy
import hashlib
import importlib.util
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / 'artifacts/css-attr-non-type-fallback-repair-v2'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

h = load('preserve', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
o = load('ownership', 'artifacts/css-counter-scope-append-comparison-execution-v1/compare.py')
read = lambda path: json.loads(path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')

def main():
    assert all(not os.environ.get(key) for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    assert h.git(ROOT, ENV, 'symbolic-ref', 'HEAD').decode().strip() == 'refs/heads/stylo-bloom-verification-2'
    assert sha(PROPOSAL / 'FILES.json') == '716c3b142e94b8ff8168cfb51b7a5f2746817ea6b4227a4ce296071f1f0d6b57'
    manifest = read(PROPOSAL / 'FILES.json')
    manifest = manifest.get('files', manifest)
    for name, item in manifest.items():
        assert sha(PROPOSAL / name) == (item['sha256'] if isinstance(item, dict) else item), name
    pins = read(PROPOSAL / 'SOURCE-PINS.json')['paths']
    if sys.argv[1:] == ['init']:
        epoch = read(ROOT / 'artifacts/css-local-signing-20261027-v9/CURRENT-EPOCH.json')
        before = a.verify_current(h, ROOT, ENV, epoch)
        owned = {}
        for name, values in pins.items():
            assert sha(ROOT / name) == epoch['pins'][name] == values['live_sha256']
            info = (ROOT / name).lstat()
            assert stat.S_ISREG(info.st_mode)
            owned[name] = {'path': name, 'identity': [info.st_dev, info.st_ino], 'owned_sha256': values['live_sha256']}
        save(HERE / 'INITIAL-EPOCH.json', epoch)
        save(HERE / 'CURRENT-EPOCH.json', epoch)
        save(HERE / 'BEFORE.json', before)
        save(HERE / 'OWNED.json', owned)
        save(HERE / 'ROLE.json', {'role': 'original', 'built': True})
        print('Initialized original source/binary epoch', flush=True)
        return
    role, label = sys.argv[1:]
    assert role in ('original', 'candidate') and '/' not in label
    epoch = read(HERE / 'CURRENT-EPOCH.json')
    before = a.verify_current(h, ROOT, ENV, epoch)
    owned = read(HERE / 'OWNED.json')
    previous = read(HERE / 'ROLE.json')
    assert previous['role'] != role
    role_dir = 'base-live' if role == 'original' else 'candidate-live'
    key = 'live_sha256' if role == 'original' else 'candidate_live_sha256'
    flags = {name: h.git(ROOT / name, ENV, 'ls-files', '-v', '-z') for name in ('.', 'artifacts/css-spec-lean')}
    for name, values in pins.items():
        assert sha(ROOT / name) == owned[name]['owned_sha256'] == epoch['pins'][name]
        assert sha(PROPOSAL / role_dir / name) == values[key]
    save(HERE / (label + '-PRE.json'), before)
    for name, item in owned.items():
        o.write_owned(ROOT, item, (PROPOSAL / role_dir / name).read_bytes())
    current = copy.deepcopy(epoch)
    for name, values in pins.items():
        current['pins'][name] = values[key]
        current['installed_identities'][name] = owned[name]['identity']
    state = h.index_state(ROOT, ENV)
    semantic = h.semantic_index(state)
    assert all(semantic[key] == epoch['semantic_index'][key] for key in ('head', 'entries', 'cached_diff'))
    current['semantic_index'] = semantic
    current['raw_index_observation']['current'] = state['raw_index']
    current['attribute_fallback_transition'] = {'role': role, 'compiled': False, 'last_transition': label, 'accepted': False}
    after = a.verify_current(h, ROOT, ENV, current)
    assert all(h.git(ROOT / name, ENV, 'ls-files', '-v', '-z') == body for name, body in flags.items())
    save(HERE / (label + '-POST.json'), after)
    save(HERE / (label + '-EPOCH.json'), current)
    (HERE / 'CURRENT-EPOCH.json').write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
    (HERE / 'OWNED.json').write_text(json.dumps(owned, indent=2, sort_keys=True) + '\n')
    (HERE / 'ROLE.json').write_text(json.dumps({'role': role, 'built': False, 'last_transition': label}, indent=2) + '\n')
    print('Switched native sources to', role, '; build required', flush=True)

if __name__ == '__main__':
    main()
