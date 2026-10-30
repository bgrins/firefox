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
assert receipt['stage'] == 'language' and receipt['signature_verified'] is True
assert receipt['commit'] == bindings['head'] and receipt['epoch_sha256'] == bindings['epoch_sha256']
assert receipt['accepted'] is False and receipt['accepted_fix_increment'] == 0
assert receipt['app_rebuilt'] is False
assert receipt['files'] == ['dom/base/nsLineBreaker.cpp', 'testing/web-platform/tests/css/css-text/line-break/line-break-language-latin1-partitions.html', 'testing/web-platform/tests/css/css-text/line-break/line-break-language-text-partitions.html', 'testing/web-platform/tests/css/css-text/line-break/line-break-unknown-language-context.html']
research_body = (ROOT / bindings['prior_research_receipt']).read_bytes()
assert sha(research_body) == bindings['prior_research_receipt_sha256']
research = json.loads(research_body)
assert research['committed'] and research['signature_verified']
assert receipt['parent'] == research['head'] == bindings['native_parent']
assert receipt['commit'] != receipt['parent']
assert git('rev-parse', bindings['head'] + '^').decode().strip() == receipt['parent']
assert git('diff-tree', '--no-commit-id', '--name-only', '-r', bindings['head']).decode().splitlines() == receipt['files']
for path, digest in {'dom/base/nsLineBreaker.cpp': 'a1ae4b3afd12908b882d3a6e34c4fd1d078c5b66dff9b06a75c31a6624ad4d9d', 'testing/web-platform/tests/css/css-text/line-break/line-break-language-latin1-partitions.html': '0b304a726d7ce7ebd6c9f080eb1de772b8eee7268115fb34244bd290b0da1d5b', 'testing/web-platform/tests/css/css-text/line-break/line-break-language-text-partitions.html': '66845fdb6776a311767e2dcbcc86d33163294dd3eb7101d7251185702d86e285', 'testing/web-platform/tests/css/css-text/line-break/line-break-unknown-language-context.html': 'b4283942b4656abe352395e8c38c931428492e26db814d5a9accef51b3d30967'}.items():
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
