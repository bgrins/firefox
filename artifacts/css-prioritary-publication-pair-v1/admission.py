import hashlib
import json
from pathlib import Path

read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def authenticate(root,binding):
    directory=root/binding['directory']
    assert sha(directory/'FILES.json')==binding['manifest_sha256']
    for name,row in read(directory/'FILES.json').items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert (directory/name).is_file() and not (directory/name).is_symlink()
        assert sha(directory/name)==row['sha256'] and (directory/name).stat().st_size==row['bytes']
    return directory


def validate_current(root,policy,roles):
    binding=policy['current_binding']
    assert binding and sha(root/binding['path'])==binding['sha256']
    capture=read(root/binding['path'])
    assert capture['full_current_state_verified'] and capture['source_transition_lock_absent']
    assert capture['published_image_ancestor_verified'] and capture['sources_match_head']
    owner=authenticate(root,policy['capture_owner'])
    assert capture['prepared_manifest_sha256']==policy['capture_owner']['manifest_sha256']
    assert capture['capture_helper_sha256']==sha(owner/'capture_current.py')
    receipt=capture['checkpoint_receipt']
    assert sha(root/receipt['path'])==receipt['sha256']
    checkpoint=read(root/receipt['path'])
    assert checkpoint==capture['checkpoint'] and checkpoint['committed'] and checkpoint['signature_verified']
    assert checkpoint['accepted_fix_increment']==0 and checkpoint['native_working_diff_preserved']
    assert checkpoint['head']==policy['head']==capture['snapshot']['index']['head']
    assert checkpoint['epoch_sha256']==capture['controls']['CURRENT-EPOCH.json']
    assert capture['controls']==policy['controls'] and set(capture['controls'])=={'CURRENT-EPOCH.json','ROLE.json','OWNED.json'}
    assert set(capture['sources'])==set(roles)
    for name,row in roles.items():
        claim=capture['sources'][name]
        assert claim['path']==name and claim['owned_sha256']==row['base_sha256']
        assert claim==capture['payload_claims'][name]
    assert set(capture['payload_claims'])==set(capture['installed_identities'])
    for name,claim in capture['payload_claims'].items():
        assert claim['path']==name and claim['identity']==capture['installed_identities'][name]
        assert claim['owned_sha256']==capture['epoch_payload_pins'][name]
    assert policy['accepted_current_payloads']=={name:{'sha256':claim['owned_sha256'],'identity':claim['identity']} for name,claim in capture['payload_claims'].items()}
    assert set(capture['binaries'])==set(policy['rebuilt_binaries'])
    assert all(capture['binaries'][name]==capture['epoch_payload_pins'][name] for name in policy['rebuilt_binaries'])
    assert capture['application_metadata']['revision']==policy['restored_application_revision']
    assert capture['application_metadata']['sha256']=='936bd88f3e47b0106b04b608cda306cc2fdee3bfd502e041b561febdb9643d3a'
    assert capture['application_metadata']['browser_build_id']=='20261029165244'
    assert set(capture['extras'])==set(policy['extra_backup_paths']) and len(capture['app_inventory_sha256'])==64
    assert set(capture['flag_hashes'])=={'root','nested'}
    return capture


def validate_prerequisite(root,policy,roles):
    runtime=authenticate(root,policy['prerequisite_binding'])
    report=read(runtime/'ROOT-REVIEW.json')
    terminal=read(runtime/'ROOT-REVIEW-TERMINAL.json')
    assert terminal['exit']==0 and terminal['review_sha256']==sha(runtime/'ROOT-REVIEW.json')
    assert report['restoration_independently_verified'] and report['observation_complete']
    assert not report['native_acceptance'] and not report['canonical_updated']
    assert report['actual_terminal']==read(runtime/'ROOT-OWNER-TERMINAL.json')
    assert report['actual_terminal']['exit']==0 and report['actual_terminal']['result_sha256']==sha(runtime/'CANDIDATE-RESULT.json')
    assert read(runtime/'candidate-build/RESULT.json')['native_sources']=={name:row['candidate_sha256'] for name,row in roles.items()}
    original=read(runtime/'CANDIDATE-PRE.json')['sources']
    assert {name:row['base_sha256'] for name,row in original.items()}=={name:row['base_sha256'] for name,row in roles.items()}
    corrected=authenticate(root,policy['assessor_binding'])
    replay=read(corrected/'REPLAY.json')
    assert not replay['native_acceptance'] and not replay['live_records_modified']
    lanes=replay['lanes']
    assert all(row['corrected_assessment_gate'] and row['corrected_behavior_gate'] for row in lanes.values())
    assert sum(row['targets_PASS'] for row in lanes.values())==24
    assert sum(row['preserved_original_PASS'] for row in lanes.values())==64
    assert sum(row['published_signatures_preserved'] for row in lanes.values())==8
    assert sum(row['endings_OK'] for row in lanes.values())==12
