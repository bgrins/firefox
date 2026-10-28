import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = read(HERE/'INPUTS.json')
assert inputs['execution_enabled'] is True and inputs['final_validation_ready'] is True
assert inputs['renderer_canonical_write_authorized'] is False
for name,pin in inputs['references'].items(): assert sha(ROOT/name) == pin
assert isinstance(inputs['fix'], int) and inputs['fix'] > 0
assert not any(os.environ.get(n) for n in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
env = dict(os.environ,GIT_OPTIONAL_LOCKS='0')


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,env=env)


payload = read(HERE/'native-selection.json')
acceptance = ROOT/inputs['acceptance_path']
assert sha(acceptance) == inputs['acceptance_sha256']
accepted = read(acceptance)
assert accepted['status'] == 'READY_FOR_STANDALONE_SIGNED_COMMIT'
assert accepted['fix'] == inputs['fix']
assert accepted['payload_sha256'] == sha(HERE/'native-selection.json')
assert accepted['promoted_build_passed'] and accepted['promoted_wpt_passed'] and accepted['wpt_lint_passed']
assert accepted['target_pass'] == 12 and accepted['regressions_unchanged'] == 22 and accepted['ends_unchanged'] == 6
assert accepted['evidence_pins'] == inputs['evidence_pins'] and inputs['evidence_pins']
for name,pin in inputs['evidence_pins'].items():
    assert sha(ROOT/name) == pin
signing = ROOT/inputs['signing_directory']
receipt = read(signing/inputs['native_receipt'])
assert receipt['signature_verified'] and receipt['working_bodies_and_nested_index_preserved']
assert sorted(receipt['files']) == payload['files'] and len(payload['files']) == 3
commit = receipt['commit']
assert git('rev-parse','HEAD').decode().strip() == commit
assert git('rev-parse',commit+'^').decode().strip() == receipt['parent']
assert git('rev-parse',commit+'^{tree}').decode().strip() == receipt['tree']
assert sorted(git('diff-tree','--no-commit-id','--name-only','-r',commit).decode().splitlines()) == payload['files']
assert not git('diff','--cached','--name-only')
for name,pin in payload['source_pins'].items():
    assert sha(ROOT/name) == pin == hashlib.sha256(git('show',commit+':'+name)).hexdigest()
    assert inputs['evidence_pins'].get(name) == pin
subprocess.run(['git','-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',commit],cwd=ROOT,env=env,check=True)
paths = ['artifacts/stylo-bloom-tools/CURRENT-COMMITS.json','artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md','artifacts/css-continuation-roadmap-20261028-v1/PLAN.md']
assert set(inputs['ledger_preimages']) == set(paths)
old = {n:(ROOT/n).read_bytes() for n in paths}
for n,b in old.items():
    assert hashlib.sha256(b).hexdigest() == inputs['ledger_preimages'][n]
    assert b == git('show',commit+':'+n)
ledger = json.loads(old[paths[0]])
assert ledger['committed_native_fixes'] == 139
assert not any(v.get('fix') == inputs['fix'] for v in ledger['new_queue'])
assert inputs['fix'] == max(v['fix'] for v in ledger['new_queue'] if isinstance(v.get('fix'),int)) + 1
entry = copy.deepcopy(accepted['ledger_entry'])
entry['acceptance'] = {'path':inputs['acceptance_path'],'sha256':inputs['acceptance_sha256']}
assert entry['fix'] == inputs['fix']
research_receipt = read(signing/'research-receipt.json')
validation_receipt = read(signing/'validation-receipt.json')
assert research_receipt['parent'] == inputs['initial_head']
assert validation_receipt['parent'] == research_receipt['commit']
assert receipt['parent'] == validation_receipt['commit']
for prior in (research_receipt,validation_receipt):
    assert prior['signature_verified'] and prior['working_bodies_and_nested_index_preserved']
    assert all(name.startswith('artifacts/') for name in prior['files'])
    assert git('rev-parse',prior['commit']+'^').decode().strip() == prior['parent']
    assert git('rev-parse',prior['commit']+'^{tree}').decode().strip() == prior['tree']
    assert sorted(git('diff-tree','--no-commit-id','--name-only','-r',prior['commit']).decode().splitlines()) == sorted(prior['files'])
    subprocess.run(['git','-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',prior['commit']],cwd=ROOT,env=env,check=True)
entry.update(native_commit=commit,research_commit=research_receipt['commit'],validation_commit=validation_receipt['commit'],companion_commit=validation_receipt['commit'],signature_verified=True,status='COMMITTED_NATIVE_WPT',commit_verification={'path':str((signing/inputs['native_receipt']).relative_to(ROOT)),'sha256':sha(signing/inputs['native_receipt'])})
ledger['new_queue'].append(entry)
ledger['committed_native_fixes'] = 140
ledger['latest_line_height_fix'] = entry
summary = accepted['approved_checkpoint_summary']
assert isinstance(summary,str) and summary.strip()
title,rest = old[paths[1]].decode().split('\n',1)
planned = {paths[0]:(json.dumps(ledger,indent=2)+'\n').encode(),paths[1]:(title+'\n\n'+summary+'\n\nEarlier entries retain their historical state.\n\n'+rest).encode(),paths[2]:accepted['approved_roadmap'].encode()}
output = HERE/'prepared-checkpoint'
assert not output.exists() and not output.is_symlink()
output.mkdir()
for name,body in planned.items():
    p=output/'postimages'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body)
    p=output/'preimages'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(old[name])
(output/'PLAN.json').write_text(json.dumps({'before':inputs['ledger_preimages'],'after':{n:hashlib.sha256(b).hexdigest() for n,b in planned.items()},'native_commit':commit,'provider_preserved_unaccepted':True,'canonical_writes_performed':False,'publication_requires_owned_preimages_and_final_epoch_guard':True},indent=2)+'\n')
print('Prepared reviewed ledger postimages only; no canonical ledger or runtime write')
