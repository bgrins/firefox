import copy
import hashlib
import json
import subprocess

read=lambda p:json.loads(p.read_bytes())
def validate_projection(initial, current, items):
    expected=copy.deepcopy(initial)
    assert len(expected['staged_working'])==36 and current['staged_working']=={}
    expected['staged_working']={}
    expected['semantic_index']=current['semantic_index']
    expected['raw_index_observation']['current']=current['raw_index_observation']['current']
    for item in items:
        assert set(item['source_pins'])==set(item['files'])
        assert all(n.startswith('artifacts/') and n!='artifacts/css-spec-lean' and not n.startswith('artifacts/css-spec-lean/') for n in item['files'])
        expected['committed_research_working_payloads'].update(item['source_pins'])
    expected['counts']['committed_research_payloads']=len(expected['committed_research_working_payloads'])
    assert expected==current
    assert current['semantic_index']['working_diff']==initial['semantic_index']['working_diff']
    assert current['modified_native_paths']==['servo/components/style/custom_properties.rs']

def validate(root, capsule, policy, epoch, h, env):
    for name,pin in read(capsule/'REFERENCES.json').items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==pin,name
    signing=root/policy['signing']
    initial=read(signing/'INITIAL-EPOCH.json')
    final=read(signing/'FINAL-CHECK.json')
    assert final['signature_chain_verified'] and final['runtime_epoch_synchronized']
    assert final['provider_candidate_compiled'] is False and final['provider_candidate_accepted'] is False
    assert final['head']==policy['head']==epoch['semantic_index']['head']
    assert (signing/'CURRENT-EPOCH.json').read_bytes()==(capsule/'INITIAL-EPOCH.json').read_bytes()
    assert epoch==read(capsule/'INITIAL-EPOCH.json')
    assert final['current_epoch_sha256']==hashlib.sha256((capsule/'INITIAL-EPOCH.json').read_bytes()).hexdigest()
    ids=read(signing/'SYNC-PLAN.json')['receipt_ids']
    assert ids==['cycle-model','initial-independence','provider-observations','provider-repair','continued-research','checkpoint']
    items=[];parent=initial['semantic_index']['head']
    for ident in ids:
        receipt=read(signing/(ident+'-receipt.json'));item=read(signing/(ident+'-item.json'))
        assert receipt['signature_verified'] and receipt['working_bodies_and_nested_index_preserved']
        assert receipt['parent']==parent and sorted(receipt['files'])==sorted(item['files'])
        assert h.git(root,env,'rev-parse',receipt['commit']+'^').decode().strip()==parent
        assert h.git(root,env,'rev-parse',receipt['commit']+'^{tree}').decode().strip()==receipt['tree']
        assert sorted(h.git(root,env,'diff-tree','--no-commit-id','--name-only','-r',receipt['commit']).decode().splitlines())==sorted(item['files'])
        subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false','-c','gpg.ssh.allowedSignersFile='+str(root/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',receipt['commit']],cwd=root,env=env,check=True,capture_output=True)
        parent=receipt['commit'];items.append(item)
    assert parent==policy['head']
    validate_projection(initial,epoch,items)
