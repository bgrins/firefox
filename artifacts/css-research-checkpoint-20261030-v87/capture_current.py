import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda data: hashlib.sha256(data).hexdigest()
assert len(sys.argv) == 3
bindings = json.loads((HERE / 'BINDINGS.json').read_bytes())
receipts = bindings['native_receipts']
assert [r['stage'] for r in receipts] == ['minmax', 'log', 'union', 'image']
parent = '8f0f2859676d19f41848f376724e1281c12f1f00'
for record in receipts:
    assert record['path'] and record['sha256']
    body = (ROOT / record['path']).read_bytes()
    assert sha(body) == record['sha256']
    receipt = json.loads(body)
    assert receipt['signature_verified'] and receipt['parent'] == parent
    parent = receipt['commit']
audit_name, audit_hash = sys.argv[1:]
audit_body = (ROOT / audit_name).read_bytes()
assert sha(audit_body) == audit_hash
audit = json.loads(audit_body)
assert audit['head'] == parent and not audit['staged_paths'] and not audit['tracked_modified_paths']
assert not audit['unexpected_paths'] and not audit['missing_paths'] and not audit['unrelated_metadata_mismatches']
assert audit['project_hashes_match_committed_recovery']
directory = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
assert not (directory / 'SOURCE-TRANSITION.lock').exists()
controls = {name: (directory / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
assert sha(controls['CURRENT-EPOCH.json']) == receipt['epoch_sha256']
epoch = json.loads(controls['CURRENT-EPOCH.json'])
role = json.loads(controls['ROLE.json'])
assert role['role'] == 'published-native' and role['variant'] == 'registered-image'
assert role['built'] is False and role['paired_head'] == parent and 'last_build' not in role
assert 'last_install' not in role and role['pending_gtest_overlay_installed'] is False
retirement = epoch['prototype_overlay_state']
assert retirement['installed'] is False and retirement['held_provider_parked'] is True
assert retirement['old_restoration_recipes_require_rebase'] is True
union_runtime = (ROOT / receipts[2]['path']).parent
parked_role = union_runtime / 'PRE-ROLE.json'
assert retirement['original_role_preserved_in'] == str(parked_role.relative_to(ROOT))
initial_claims = union_runtime / 'INITIAL-CLAIMS.json'
assert json.loads(initial_claims.read_bytes())['controls']['ROLE.json']['owned_sha256'] == sha(parked_role.read_bytes())
retirement_claim = {'path':str(parked_role.relative_to(ROOT)), 'sha256':sha(parked_role.read_bytes()),
                    'initial_claims_path':str(initial_claims.relative_to(ROOT)), 'initial_claims_sha256':sha(initial_claims.read_bytes())}
spec = importlib.util.spec_from_file_location('state', directory / 'state.py')
state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state)
snapshot = state.a.verify_current(state.h, ROOT, dict(os.environ, GIT_OPTIONAL_LOCKS='0'), json.loads(controls['CURRENT-EPOCH.json']))
assert snapshot['index']['head'] == parent
assert all((directory / name).read_bytes() == body for name, body in controls.items())
assert not (directory / 'SOURCE-TRANSITION.lock').exists()
output = ROOT / 'artifacts/css-research-checkpoint-20261030-v87-current.json'
with output.open('x') as stream:
    json.dump({'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'audit':snapshot, 'controls':{name:sha(body) for name,body in controls.items()},
               'source_transition_lock_absent':True, 'full_current_state_verified':True,
               'untracked_audit':audit_name, 'untracked_audit_sha256':audit_hash,
               'publication_receipts':receipts, 'role':role, 'prototype_overlay_state':retirement,
               'retirement_claim':retirement_claim}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'path':str(output.relative_to(ROOT)), 'sha256':sha(output.read_bytes())}))
