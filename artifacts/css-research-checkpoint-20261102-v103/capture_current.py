import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
sha = lambda body: hashlib.sha256(body).hexdigest()
bindings = json.loads((HERE / 'BINDINGS.json').read_bytes())
assert bindings['head'] and bindings['epoch_sha256'] and bindings['prior_receipt_sha256'], 'Native publication binding is pending'
assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=ENV)
assert git('rev-parse', 'HEAD').decode().strip() == bindings['head']
assert not git('diff', '--name-only').strip() and not git('diff', '--cached', '--name-only').strip()
receipt_body = (ROOT / bindings['prior_receipt']).read_bytes()
assert sha(receipt_body) == bindings['prior_receipt_sha256']
receipt = json.loads(receipt_body)
assert set(receipt) == {'stage', 'commit', 'parent', 'signature_verified', 'files', 'epoch_sha256', 'accepted', 'accepted_fix_increment', 'app_rebuilt'}
assert receipt['stage'] == 'ownership' and receipt['signature_verified'] is True
assert receipt['commit'] == bindings['head'] and receipt['epoch_sha256'] == bindings['epoch_sha256']
assert receipt['accepted'] is False and receipt['accepted_fix_increment'] == 0
assert receipt['app_rebuilt'] is False
assert receipt['files'] == ['dom/base/nsLineBreaker.cpp', 'dom/base/nsLineBreaker.h', 'layout/generic/nsTextFrame.cpp', 'testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-dynamic.html', 'testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-inline-ownership.html', 'testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-pseudo-ownership.html']
research_body = (ROOT / bindings['prior_research_receipt']).read_bytes()
assert sha(research_body) == bindings['prior_research_receipt_sha256']
research = json.loads(research_body)
assert research['committed'] and research['signature_verified']
assert receipt['parent'] == research['head'] == bindings['native_parent']
assert receipt['commit'] != receipt['parent']
assert git('rev-parse', bindings['head'] + '^').decode().strip() == receipt['parent']
assert git('diff-tree', '--no-commit-id', '--name-only', '-r', bindings['head']).decode().splitlines() == receipt['files']
for path, digest in {'dom/base/nsLineBreaker.cpp': '0eb8a512f37f65a2835ebfa21ebb935ce1f26396541d1a722c918f6ebaa7a7ac', 'dom/base/nsLineBreaker.h': '32d514122b1ca1a4bf8ee724a5465bb7f12205314cfc088f31241de408479d5d', 'layout/generic/nsTextFrame.cpp': 'ec44924925012a5c059b5bd6c43e609cc6ecb1838a1e73918518fcb7c17d4077', 'testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-dynamic.html': '658527aa39d99627a5b132970f6afba6532966c5946561414b54929b81926409', 'testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-inline-ownership.html': 'ebc8a0bddbd68c7562d778db8d96bec474122160f44d43649be3af4f0e85d8f3', 'testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-pseudo-ownership.html': 'd45d51c987e7012c0139f62cb84f583b6c1e627c390ef40ef87f3af118ee71ad'}.items():
    assert sha(git('show', bindings['head'] + ':' + path)) == digest
directory = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
assert not (directory / 'SOURCE-TRANSITION.lock').exists()
controls = {name: (directory / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
assert sha(controls['CURRENT-EPOCH.json']) == bindings['epoch_sha256']
for path in ['artifacts/css-registered-number-native-runtime-v1/state.py', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py', 'artifacts/css-counter-scope-append-comparison-execution-v1/compare.py']:
    assert (ROOT / path).read_bytes() == git('show', bindings['head'] + ':' + path)
spec = importlib.util.spec_from_file_location('state', directory / 'state.py')
state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state)
audit = state.a.verify_current(state.h, ROOT, ENV, json.loads(controls['CURRENT-EPOCH.json']))
assert audit['index']['head'] == bindings['head']
assert audit['index']['working_diff'] == audit['index']['cached_diff'] == sha(b'')
assert all((directory / name).read_bytes() == body for name, body in controls.items())
assert not (directory / 'SOURCE-TRANSITION.lock').exists()
assert not git('diff', '--name-only').strip() and not git('diff', '--cached', '--name-only').strip()
result = {'audit':audit, 'controls':{name:sha(body) for name,body in controls.items()},
          'prior_receipt_sha256':sha(receipt_body), 'full_current_state_verified':True,
          'source_transition_lock_absent':True, 'tracked_modified_paths':[], 'staged_paths':[]}
with (ROOT / bindings['current_capture']).open('x') as stream:
    json.dump(result, stream, indent=2); stream.write('\n')
print(json.dumps({'head':bindings['head'], 'epoch':bindings['epoch_sha256'], 'full_current_state_verified':True}))
