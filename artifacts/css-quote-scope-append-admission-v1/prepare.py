import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


h = load('guards', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
old_path = ROOT / 'artifacts/css-local-signing-20261027-v5/research-checkpoint-EPOCH.json'
epoch = json.loads(old_path.read_text())
before = a.verify_current(h, ROOT, ENV, epoch)
paths = set(json.loads((ROOT / 'artifacts/css-quote-scope-append-coc-inputs-v1/GUARD-PATHS.json').read_text())['paths'])
paths.add('objdir-full.noindex/_tests/web-platform/wptrunner.local.ini')
test_root = Path('testing/web-platform/tests')
for name in list(paths):
    p = Path(name)
    if p.is_relative_to(test_root) and not name.endswith('.headers'):
        paths.add(name + '.headers')
        parent = p.parent
        while parent.is_relative_to(test_root):
            paths.add(str(parent / '__dir__.headers'))
            parent = parent.parent
pins = {name: h.fingerprint(ROOT, name) for name in sorted(paths)}
for name, pin in pins.items():
    if name in epoch['pins']:
        assert epoch['pins'][name] == pin, name
source_pins = json.loads((ROOT / 'artifacts/css-quote-scope-append-coc-inputs-v1/SOURCE-PINS.json').read_text())
identities = {}
for name, pin in source_pins.items():
    assert pins[name] == pin['candidate_sha256']
    info = (ROOT / name).lstat()
    identities[name] = [info.st_dev, info.st_ino]
    if name in epoch['installed_identities']:
        assert epoch['installed_identities'][name] == identities[name]
current = copy.deepcopy(epoch)
current['pins'].update(pins)
current['installed_identities'].update(identities)
current['counts']['roles'] = len(current['pins'])
current['counts']['installed_identities'] = len(current['installed_identities'])
after = a.verify_current(h, ROOT, ENV, current)
assert before == after
save('CURRENT-EPOCH.json', current)
save('RESOURCES.json', pins)
save('QUOTE-IDENTITIES.json', identities)
save('CHECK.json', dict(status='QUOTE_CURRENT_STATE_VERIFIED', root_head=before['index']['head'], nested_head=before['nested_index']['head'], guard_paths=len(pins), absent_paths=sum(p is None for p in pins.values()), source_variants='candidate', source_and_binaries_unchanged=True, both_indexes_preserved=True, prior_epoch_sha256=hashlib.sha256(old_path.read_bytes()).hexdigest()))
print('Current source, binaries, indexes and quote resource closure verified.', flush=True)
