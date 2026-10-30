import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import check

policy = check.read(HERE / 'POLICY.json')
roles = check.read(HERE / 'SOURCE-ROLES.json')
head = 'e' * 40
checkpoint = {'committed': True, 'signature_verified': True, 'head': head, 'epoch_sha256': 'a' * 64}
with tempfile.TemporaryDirectory(prefix='binding-check-', dir=HERE) as temporary:
    scratch = Path(temporary)
    receipt = scratch / 'CHECKPOINT.json'
    receipt.write_text(json.dumps(checkpoint))
    capture = {
        'prepared_manifest_sha256': policy['prepared_binding']['manifest_sha256'],
        'full_current_state_verified': True, 'source_transition_lock_absent': True,
        'published_image_ancestor_verified': True, 'sources_match_head': True,
        'checkpoint': checkpoint,
        'checkpoint_receipt': {'path': str(receipt.relative_to(ROOT)), 'sha256': check.sha(receipt)},
        'snapshot': {'index': {'head': head}, 'nested_index': {},
                     'current_raw_stable_during_check': True,
                     'working_sources_binaries_research_preserved': True},
        'controls': {'CURRENT-EPOCH.json': 'a' * 64, 'ROLE.json': 'b' * 64, 'OWNED.json': 'c' * 64},
        'role': {'role': 'published-native', 'variant': 'registered-image', 'built': False,
                 'paired_head': policy['image_commit'], 'pending_gtest_overlay_installed': False},
        'prototype_overlay_state': {'installed': False, 'held_provider_parked': True,
             'old_restoration_recipes_require_rebase': True,
             'original_role_preserved_in': 'artifacts/css-registered-color-image-publication-union-runtime-1/PRE-ROLE.json'},
        'sources': {name: {'path': name, 'owned_sha256': row['base_sha256'], 'identity': [1, i + 2]} for i, (name, row) in enumerate(roles.items())},
        'flag_hashes': {'root': 'd' * 64, 'nested': 'f' * 64},
        'binaries': {name: 'a' * 64 for name in policy['rebuilt_binaries']},
        'extras': {name: {'kind': 'file'} for name in policy['extra_backup_paths']},
        'application_metadata': {'revision': policy['restored_application_revision'],
            'sha256': '936bd88f3e47b0106b04b608cda306cc2fdee3bfd502e041b561febdb9643d3a', 'browser_build_id': '20261029165244'},
        'app_inventory_sha256': 'f' * 64, 'capture_helper_sha256': check.sha(HERE / 'capture_current.py'),
    }
    capture['payload_claims'] = copy.deepcopy(capture['sources'])
    capture['installed_identities'] = {name: row['identity'] for name, row in capture['payload_claims'].items()}
    capture['epoch_payload_pins'] = {name: row['owned_sha256'] for name, row in capture['payload_claims'].items()}
    bound = copy.deepcopy(policy)
    bound.update(head=head, controls=capture['controls'])
    bound['accepted_current_payloads'] = {name: {'sha256': row['owned_sha256'], 'identity': row['identity']} for name, row in capture['payload_claims'].items()}
    check.validate_capture(bound, capture, roles)
    mutations = [lambda c: c.update(full_current_state_verified=False),
                 lambda c: c.update(published_image_ancestor_verified=False),
                 lambda c: c.update(sources_match_head=False),
                 lambda c: c['role'].update(built=True),
                 lambda c: c['role'].update(variant='held-provider'),
                 lambda c: c['role'].update(last_build='stale'),
                 lambda c: c['prototype_overlay_state'].update(installed=True),
                 lambda c: c['controls'].update(**{'CURRENT-EPOCH.json': 'wrong'}),
                 lambda c: c['sources'][next(iter(roles))].update(owned_sha256='wrong'),
                 lambda c: c['payload_claims'].pop(next(iter(roles))),
                 lambda c: c['installed_identities'].pop(next(iter(roles))),
                 lambda c: c['application_metadata'].update(sha256='wrong')]
    for mutate in mutations:
        changed = copy.deepcopy(capture); mutate(changed)
        check.rejected(lambda: check.validate_capture(bound, changed, roles))
assert not scratch.exists()
old = ROOT / 'artifacts/css-prioritary-selection-original-v3/check.py'
spec = importlib.util.spec_from_file_location('original_saved_check', old)
original = importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
assessor = check.load('assess')
spec = importlib.util.spec_from_file_location('stream_checks', ROOT / policy['wpt']['checks_helper'])
stream_checks = importlib.util.module_from_spec(spec); spec.loader.exec_module(stream_checks)
streams = []
for lane in policy['lane_order']:
    for status in ('PASS', 'FAIL'):
        events, code, settings, app = original.synthetic(policy, lane, status)
        result = assessor.assess(events, code, settings, stream_checks, run_binding=app)
        assert result['complete'] and all(row['status'] == status for row in result['rows'])
        assert len(result['rows']) == settings['expected_subtest_count']
        assert len(result['ends']) == settings['expected_page_count']
        streams.append([lane, status, len(result['rows']), len(result['ends'])])
print(json.dumps({'synthetic_capture_positive': 1, 'capture_negatives': len(mutations),
                  'streams': streams, 'owned_scratch_removed': True, 'live_guard': False}))
