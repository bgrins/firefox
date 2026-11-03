import hashlib
import json
import importlib.util
from pathlib import Path

read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def authenticate(root,binding):
    directory=root/binding['directory']
    assert sha(directory/'FILES.json')==binding['manifest_sha256']
    manifest=read(directory/'FILES.json')
    for name,row in manifest.get('files',manifest).items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert (directory/name).is_file() and not (directory/name).is_symlink()
        if isinstance(row, str):
            assert len(row) == 64 and sha(directory/name) == row
        else:
            assert sha(directory/name)==row['sha256'] and (directory/name).stat().st_size==row['bytes']
    return directory


def direct_evidence(root, policy, native_receipt):
    assert policy['direct_equivalence'] == {
        'directory': 'artifacts/css-native-epoch-direct-equivalence-v1',
        'manifest_sha256': '0c42724061acefb0f49b654d8a22f8aff2507f6138b72109e1906c4e7e49c488',
    }
    directory = authenticate(root, policy['direct_equivalence'])
    spec = importlib.util.spec_from_file_location('saved_native_equivalence', directory/'equivalence.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    evidence = helper.verify_saved(root)
    helper.equal(policy['current_binding'], dict(zip(('path', 'sha256'), helper.INPUTS['current_capture'])), 'current capture binding')
    helper.equal(policy['capture_binding'], dict(zip(('path', 'sha256'), helper.INPUTS['current_terminal'])), 'capture terminal binding')
    helper.equal(native_receipt, read(root/helper.INPUTS['native_receipt'][0]), 'actual native receipt')
    assert evidence['native_head'] == policy['head'] == native_receipt['commit']
    assert evidence['current_epoch_sha256'] == policy['controls']['CURRENT-EPOCH.json']
    assert not evidence['live_checks_performed'] and not evidence['diagnostic_execution_authorized']
    return evidence


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
    assert checkpoint==capture['checkpoint']
    assert capture['authority_kind']==policy['authority_kind']=='signed-native-publication'
    spec=importlib.util.spec_from_file_location('native_capture_authority',owner/'baseline.py')
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    assert receipt['path']==adapter.binding['native_receipt']
    evidence=direct_evidence(root,policy,checkpoint)
    assert checkpoint['commit']==policy['head']==capture['snapshot']['index']['head']
    assert evidence['current_epoch_sha256']==capture['controls']['CURRENT-EPOCH.json']
    assert not adapter.binding['pending_pair_refresh']
    research=read(root/adapter.binding['research_parent_receipt'])
    assert research['committed'] is True and research['signature_verified'] is True
    assert checkpoint['parent']==research['head']==adapter.binding['native_parent']
    assert capture['refresh_lineage_verified'] and capture['additional_sources_match_head']
    assert capture['refresh_binding']==policy['refresh_lineage']==adapter.binding['refresh_binding']
    assert capture['refresh_manifest_sha256']==adapter.binding['refresh_manifest_sha256']
    assert capture['refresh_epoch_sha256']==evidence['current_epoch_sha256']==adapter.binding['current_epoch_sha256']
    post_path=policy['refresh_lineage']['directory']+'/POST.json'
    assert sha(root/post_path)==policy['references'][post_path]
    assert read(root/post_path)==capture['snapshot']
    assert capture['controls']==policy['controls'] and set(capture['controls'])=={'CURRENT-EPOCH.json','ROLE.json','OWNED.json'}
    here=root/policy['owner_directory']
    def local(name):
        spec=importlib.util.spec_from_file_location('admitted_'+name,here/(name+'.py'))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
    role = capture['role']
    assert role['role']=='published-native' and role['variant']=='capacity' and role['built'] is False
    assert role['paired_head']==policy['capacity_commit'] and role['pending_gtest_overlay_installed'] is False
    assert 'last_build' not in role and 'last_install' not in role
    assert role['last_transition']=='artifacts/css-prioritary-declaration-capacity-publication-capacity-runtime-1'
    captured_owner=authenticate(root,policy['capture_source_owner'])
    adapter_binding=read(owner/'BINDINGS.json')
    assert adapter_binding['executed_original_manifest']==policy['capture_source_owner']['manifest_sha256']
    assert adapter_binding['language_commit']==policy['language_commit']
    assert adapter_binding['ownership_commit']==policy['ownership_commit']
    assert adapter_binding['capacity_commit']==policy['capacity_commit']
    for path,pin in adapter_binding['references'].items():
        assert policy['references'][path]==sha(root/path)==pin
    native_receipt=read(root/adapter_binding['native_receipt'])
    assert native_receipt==checkpoint and native_receipt['signature_verified'] and native_receipt['commit']==policy['capacity_commit']
    retirement=capture['prototype_overlay_state']
    assert retirement=={'held_provider_parked':True,'installed':False,'old_restoration_recipes_require_rebase':True,'original_role_preserved_in':'artifacts/css-registered-color-image-publication-union-runtime-1/PRE-ROLE.json'}
    local('review_scope').require_full(capture['snapshot'])
    assert set(capture['sources'])==set(read(captured_owner/'SOURCE-ROLES.json'))
    assert all(claim==capture['payload_claims'][name] for name,claim in capture['sources'].items())
    additional=capture['additional_sources']
    assert set(additional)==set(policy['additional_source_paths'])=={'servo/components/style/data.rs', 'servo/components/style/traversal.rs'}
    assert not set(additional).intersection(capture['payload_claims'])
    source_claims=capture['payload_claims'] | additional
    assert set(roles)<=set(source_claims)
    for name,row in roles.items():
        claim=source_claims[name]
        assert claim['path']==name and claim['owned_sha256']==row['base_sha256']
        assert len(claim['identity'])==2 and all(type(value) is int for value in claim['identity'])
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

