import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / 'artifacts/css-integer-stored-range-ledger-candidates-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


h = load('preserve', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
epoch = json.loads((HERE / 'CURRENT-EPOCH.json').read_text())
before = a.verify_current(h, ROOT, ENV, epoch)
check = json.loads((PROPOSAL / 'CHECK.json').read_text())
assert check['status'] == 'FIX121_LEDGER_CANDIDATES_PREPARED' and len(check['postimages']) == 5
for name, pin in check['postimages'].items():
    assert sha(ROOT / name) == sha(PROPOSAL / 'before' / name), name
    assert sha(PROPOSAL / 'candidate' / name) == pin, name
for name in check['postimages']:
    (ROOT / name).write_bytes((PROPOSAL / 'candidate' / name).read_bytes())
state = h.index_state(ROOT, ENV)
assert all(state[k] == before['index'][k] for k in ('head', 'entries', 'cached_diff', 'raw_index'))
current = copy.deepcopy(epoch)
for name, pin in check['postimages'].items():
    for field in ('pins', 'committed_research_working_payloads'):
        if name in current[field]:
            current[field][name] = pin
current['semantic_index'] = h.semantic_index(state)
a.verify_current(h, ROOT, ENV, current)
with (HERE / 'LEDGER-EPOCH.json').open('x') as stream:
    json.dump(current, stream, indent=2, sort_keys=True)
    stream.write('\n')
(HERE / 'CURRENT-EPOCH.json').write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
print('Five reviewed ledger updates applied; all other guarded work preserved.', flush=True)
