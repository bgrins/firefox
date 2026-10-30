import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
sha = lambda data: hashlib.sha256(data).hexdigest()
assert len(sys.argv) == 5
runtime, manifest_hash, audit_name, audit_hash = sys.argv[1:]
runtime = ROOT / runtime
manifest = (runtime / 'FILES.json').read_bytes()
assert sha(manifest) == manifest_hash
files = json.loads(manifest)
files = files.get('files', files)
review_body = (runtime / 'ROOT-REVIEW.json').read_bytes()
pin = files['ROOT-REVIEW.json']
assert sha(review_body) == (pin['sha256'] if isinstance(pin, dict) else pin)
review = json.loads(review_body)
assert review['restoration_independently_verified']
audit_body = (ROOT / audit_name).read_bytes()
assert sha(audit_body) == audit_hash
audit = json.loads(audit_body)
assert not audit['unexpected_paths'] and not audit['missing_paths'] and not audit['staged_paths']
assert audit['project_hashes_match_committed_recovery'] and not audit['unrelated_metadata_mismatches']
directory = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
assert not (directory / 'SOURCE-TRANSITION.lock').exists()
controls = {name: (directory / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
spec = importlib.util.spec_from_file_location('state', directory / 'state.py')
state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state)
snapshot = state.a.verify_current(state.h, ROOT, dict(os.environ, GIT_OPTIONAL_LOCKS='0'), json.loads(controls['CURRENT-EPOCH.json']))
assert snapshot == review['snapshot']
assert snapshot['index']['head'] == audit['head']
assert all((directory / name).read_bytes() == body for name, body in controls.items())
assert not (directory / 'SOURCE-TRANSITION.lock').exists()
output = ROOT / 'artifacts/css-research-checkpoint-20261030-v86-current.json'
with output.open('x') as stream:
    json.dump({'observed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'audit': snapshot, 'controls': {name: sha(body) for name, body in controls.items()},
               'source_transition_lock_absent': True, 'full_current_state_verified': True,
               'untracked_audit': audit_name, 'untracked_audit_sha256': audit_hash,
               'restoration_runtime': str(runtime.relative_to(ROOT)), 'runtime_manifest_sha256': manifest_hash,
               'restoration_review_sha256': sha(review_body)}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'path': str(output.relative_to(ROOT)), 'sha256': sha(output.read_bytes())}))
