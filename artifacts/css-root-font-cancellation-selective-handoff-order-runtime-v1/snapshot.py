import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OWNER = ROOT / 'artifacts/css-root-font-cancellation-selective-handoff-candidate-browser-v1'
RUNTIME = ROOT / 'artifacts/css-root-font-cancellation-selective-handoff-candidate-browser-runtime-v1'
CANONICAL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
assert sys.argv[1:] in [['PRE'], ['POST']]
assert sha(RUNTIME / 'FILES.json') == '50f72d25bb9bea8f03da9357259f54f17ad2121d363c6f8b7d89621db507c8b4'
for name, item in read(RUNTIME / 'FILES.json')['files'].items():
    assert sha(RUNTIME / name) == item['sha256']
assert sha(OWNER / 'FILES.json') == '758668de9e3bd6883d0f8b3cbad2dd79aa4d66f2b7e894a67037b8bc517b6772'
for name, item in read(OWNER / 'FILES.json').items():
    assert sha(OWNER / name) == item['sha256']
audit = read(RUNTIME / 'ROOT-LIVE-RESTORATION.json')
assert audit['independent_live_restoration_verified']
assert audit['archive_observation']['archive_retained_verified']
assert read(RUNTIME / 'ROOT-AUDIT-TERMINAL.json')['exit'] == 0
policy = read(OWNER / 'POLICY.json')
archive = load('candidate_inventory', OWNER / 'archive.py')
record = read(RUNTIME / 'ARCHIVE-SNAPSHOT.json')
app = Path(record['application'])
inventory = archive.inventory(app, False)
assert inventory['files'] == record['files']
assert hashlib.sha256(json.dumps(inventory, sort_keys=True).encode()).hexdigest() == audit['archive_observation']['retained_inventory_sha256']
assert archive.validate(ROOT, record, policy['archive']) == read(RUNTIME / 'ARCHIVE-VALIDATION.json')
state = load('candidate_shared_state', ROOT / policy['state_helper'])
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
epoch = read(CANONICAL / 'CURRENT-EPOCH.json')
index = state.h.index_state(ROOT, env)
assert state.h.semantic_index(index) == epoch['semantic_index']
adjusted = copy.deepcopy(epoch)
adjusted['raw_index_observation']['current'] = index['raw_index']
observed = state.a.verify_current(state.h, ROOT, env, adjusted)
assert observed == audit['snapshot']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
sources = {}
for name, claim in audit['restored_source_claims'].items():
    path = ROOT / name
    assert sha(path) == claim['owned_sha256']
    assert [path.stat().st_dev, path.stat().st_ino] == claim['identity']
    sources[name] = claim
for name, pin in policy['source_context_pins'].items():
    assert sha(ROOT / name) == pin
bundle = load('candidate_shared_bundle', ROOT / policy['bundle_helper'])
shared_app = bundle.scan(ROOT / policy['bundle_path'])
assert bundle.semantic(shared_app) == bundle.semantic(read(RUNTIME / 'APP-PRE.json'))
extras = {name: bundle.entry(ROOT / name) for name in policy['extra_backup_paths']}
assert bundle.semantic(extras) == bundle.semantic(read(RUNTIME / 'EXTRA-PRE.json'))
controls = {name: sha(CANONICAL / name) for name in policy['controls']}
flags = {label: hashlib.sha256(state.h.git(path, env, 'ls-files', '-v', '-z')).hexdigest()
         for label, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
report = dict(archive_inventory=inventory, shared_snapshot=observed,
              shared_app=shared_app, shared_extras=extras, sources=sources,
              controls=controls, flags=flags)
if sys.argv[1] == 'POST':
    assert report == read(HERE / 'PRE.json')
with (HERE / (sys.argv[1] + '.json')).open('x') as stream:
    json.dump(report, stream, sort_keys=True, indent=2)
    stream.write('\n')
print(sys.argv[1], 'archive and shared state verified', len(inventory['files']), 'files')
