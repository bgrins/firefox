import hashlib
import json
import importlib.util
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


def verified_refresh(root, policy, checkpoint):
    binding = policy['refresh_lineage']
    directory = root / binding['directory']
    assert sha(directory / 'commit.py') == binding['driver_sha256']
    assert sha(directory / 'BINDINGS.json') == binding['bindings_sha256']
    spec = importlib.util.spec_from_file_location('diagnostic_refresh_lineage', directory / 'commit.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    receipt = root / module.BINDINGS['prior_receipt']
    assert sha(receipt) == module.BINDINGS['prior_receipt_sha256']
    assert checkpoint == read(receipt) and checkpoint['committed'] and checkpoint['signature_verified']
    assert module.BINDINGS['head'] == policy['head']
    assert module.BINDINGS['controls'] == policy['controls']
    return module.validate_refresh(checkpoint)


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
    assert verified_refresh(root,policy,checkpoint)==capture['snapshot']
    assert capture['controls']==policy['controls'] and set(capture['controls'])=={'CURRENT-EPOCH.json','ROLE.json','OWNED.json'}
    here=root/policy['owner_directory']
    def local(name):
        spec=importlib.util.spec_from_file_location('admitted_'+name,here/(name+'.py'))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
    role = capture['role']
    assert role['role']=='published-native' and role['variant']=='ownership' and role['built'] is False
    assert role['paired_head']==policy['ownership_commit'] and role['pending_gtest_overlay_installed'] is False
    assert 'last_build' not in role and 'last_install' not in role
    assert role['last_transition']=='artifacts/css-hyphenation-ownership-publication-ownership-runtime-2'
    captured_owner=authenticate(root,policy['capture_source_owner'])
    adapter_binding=read(owner/'BINDINGS.json')
    assert adapter_binding['executed_original_manifest']==policy['capture_source_owner']['manifest_sha256']
    assert adapter_binding['language_commit']==policy['language_commit']
    assert adapter_binding['ownership_commit']==policy['ownership_commit']
    for path,pin in adapter_binding['references'].items():
        assert policy['references'][path]==sha(root/path)==pin
    native_receipt=read(root/'artifacts/css-hyphenation-ownership-publication-ownership-runtime-2/COMMIT-RESULT.json')
    assert native_receipt['signature_verified'] and native_receipt['commit']==policy['ownership_commit']
    retirement=capture['prototype_overlay_state']
    assert retirement=={'held_provider_parked':True,'installed':False,'old_restoration_recipes_require_rebase':True,'original_role_preserved_in':'artifacts/css-registered-color-image-publication-union-runtime-1/PRE-ROLE.json'}
    local('review_scope').require_full(capture['snapshot'])
    assert set(capture['sources'])==set(read(captured_owner/'SOURCE-ROLES.json'))
    assert all(claim==capture['payload_claims'][name] for name,claim in capture['sources'].items())
    assert set(roles)<=set(capture['payload_claims'])
    for name,row in roles.items():
        claim=capture['payload_claims'][name]
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

