import hashlib
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import baseline

assert len(sys.argv) == 5
manifest, receipt_name, receipt_sha, output_name = sys.argv[1:]
policy, ownership, roles = baseline.prepare(manifest)
assert not Path(receipt_name).is_absolute() and ".." not in Path(receipt_name).parts
receipt_path = ROOT / receipt_name
assert baseline.sha(receipt_path) == receipt_sha
checkpoint = baseline.read(receipt_path)
assert receipt_name == baseline.binding['native_receipt']
state, env, controls, epoch, role, sources, flags, snapshot = baseline.observe(policy, ownership, roles, checkpoint)
additional_sources = baseline.claim_additional_sources(ownership, state, env, epoch, checkpoint['commit'])
payload_claims = {name: ownership.claim(ROOT, name, epoch['pins'][name], identity)
                  for name, identity in epoch['installed_identities'].items()}
bundle = baseline.load('published_capture_bundle', policy['bundle_helper'])
app = bundle.scan(ROOT / policy['bundle_path'])
extras = {name: bundle.entry(ROOT / name) for name in policy['extra_backup_paths']}
metadata = baseline.load('published_capture_metadata', policy['wpt']['metadata_helper'])
application = metadata.application_metadata(ROOT / policy['wpt']['application_ini'], policy['restored_application_revision'])
assert application['sha256'] == '936bd88f3e47b0106b04b608cda306cc2fdee3bfd502e041b561febdb9643d3a'
assert application['browser_build_id'] == '20261029165244'
binaries = {name: baseline.sha(ROOT / name) for name in policy['rebuilt_binaries']}
assert all(epoch['pins'][name] == pin for name, pin in binaries.items())
assert state.a.verify_current(state.h, ROOT, env, epoch) == snapshot
assert all((baseline.RUNTIME / name).read_bytes() == body for name, body in controls.items())
for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert state.h.git(path, env, 'ls-files', '-v', '-z') == flags[name]
assert not (baseline.RUNTIME / 'SOURCE-TRANSITION.lock').exists() and not (baseline.RUNTIME / 'SOURCE-TRANSITION.lock').is_symlink()
for name, claim in additional_sources.items():
    ownership.claim(ROOT, name, claim['owned_sha256'], claim['identity'])
output = ROOT / output_name
assert output.parent == ROOT / 'artifacts' and not output.exists() and not output.is_symlink()
state.save(output, {'checkpoint_receipt': {'path': receipt_name, 'sha256': receipt_sha},
                   'checkpoint': checkpoint, 'authority_kind': 'signed-native-publication', 'snapshot': snapshot,
                   'controls': {name: hashlib.sha256(body).hexdigest() for name, body in controls.items()},
                   'role': role, 'prototype_overlay_state': epoch['prototype_overlay_state'],
                   'sources': sources, 'additional_sources': additional_sources,
                   'additional_sources_match_head': True,
                   'refresh_binding': baseline.binding['refresh_binding'],
                   'refresh_manifest_sha256': baseline.binding['refresh_manifest_sha256'],
                   'refresh_epoch_sha256': baseline.binding['current_epoch_sha256'],
                   'refresh_lineage_verified': True, 'payload_claims': payload_claims, 'epoch_payload_pins': epoch['pins'],
                   'installed_identities': epoch['installed_identities'], 'flag_hashes': {name: hashlib.sha256(body).hexdigest() for name, body in flags.items()},
                   'application_metadata': application, 'app_inventory_sha256': baseline.digest(app),
                   'extras': extras, 'binaries': binaries, 'full_current_state_verified': True,
                   'source_transition_lock_absent': True,
                   'published_image_ancestor_verified': True, 'sources_match_head': True,
                   'capture_helper_sha256': baseline.sha(HERE / 'capture_current.py'),
                   'prepared_manifest_sha256': manifest,
                   'free_bytes': os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize})
print(json.dumps({'path': output_name, 'sha256': baseline.sha(output)}))
