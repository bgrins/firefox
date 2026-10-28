raise SystemExit('Obsolete unexecuted draft: root owns the direct signing retry; use adopt-research-retry.py only after success')
import hashlib
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
source = (Path(__file__).resolve().parent / 'commit.py').read_text()
assert hashlib.sha256(source.encode()).hexdigest() == 'ef3b5cafed2f379372c2cc6948fee914a6a90d176ae9151baee9b34d89ca8ceb'
exec(compile(source.split("if sys.argv[1]=='init':",1)[0], 'reviewed-commit-helper-prefix', 'exec'))
read = lambda p: json.loads(p.read_text())
item=read(HERE/'research-selection.json');epoch=read(HERE/'CURRENT-EPOCH.json');inputs=read(HERE/'INPUTS.json')
assert inputs['ready'] and item['id']=='research' and len(item['files'])==207
parent=inputs['frozen_head'];selected=set(item['files'])
assert read(HERE/'research-item.json')==item|{'expected_head':parent,'execution_enabled':True}
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert git('symbolic-ref','HEAD').decode().strip()=='refs/heads/stylo-bloom-verification-2'
assert git('rev-parse','HEAD').decode().strip()==parent==epoch['semantic_index']['head']
assert git('config','--get','commit.gpgsign').strip()==b'true'
for name,key in [('CURRENT-EPOCH.json','runtime_epoch_sha256'),('ROLE.json','role_sha256'),('OWNED.json','owned_sha256')]:
 assert sha(ROOT/'artifacts/css-registered-number-native-runtime-v1'/name)==inputs[key]
assert not any((HERE/n).exists() for n in ['research-receipt.json','research-retry1-commit.log','research-signature.log'])
assert set(git('diff','--cached','--name-only',parent).decode().splitlines())==selected
assert git('diff','--cached','--binary','--full-index',parent)==(HERE/'research-staged.patch').read_bytes()
assert all(n.startswith('artifacts/') for n in selected)
for n,pin in item['source_pins'].items():
 assert sha(ROOT/n)==pin and hashlib.sha256(git('show',':'+n)).hexdigest()==pin
 assert git('ls-files','--stage','--',n).decode().split()[::2]==['100644','0']
entries=git('ls-files','--stage','-z').split(b'\0')
prior_entries=b''.join(r+b'\0' for r in entries if r and r.split(b'\t',1)[1].decode() not in selected)
assert hashlib.sha256(prior_entries).hexdigest()==epoch['semantic_index']['entries']
flags=git('ls-files','-v','-z');prior_flags=b''.join(r+b'\0' for r in flags.split(b'\0') if r and r[2:].decode() not in selected)
saved_flags=read(ROOT/inputs['candidate_runtime']/'INDEX-FLAGS.json')
assert hashlib.sha256(prior_flags).hexdigest()==saved_flags['.']
assert hashlib.sha256(h.git(ROOT/'artifacts/css-spec-lean',ENV,'ls-files','-v','-z')).hexdigest()==saved_flags['artifacts/css-spec-lean']
tree=git('write-tree').decode().strip()
staged=h.index_state(ROOT,ENV);nested=h.index_state(ROOT/'artifacts/css-spec-lean',ENV)
assert staged['working_diff']==epoch['semantic_index']['working_diff']
assert nested==read(HERE/'BEFORE.json')['nested_index']
for group in ['pins','staged_working','committed_research_working_payloads']:
 assert {n:h.fingerprint(ROOT,n) for n in epoch[group]}==epoch[group]
for n,identity in epoch['installed_identities'].items():
 info=(ROOT/n).lstat();assert stat.S_ISREG(info.st_mode) and [info.st_dev,info.st_ino]==identity
assert set(git('diff','--name-only').decode().splitlines())==set(epoch['modified_native_paths'])==set(inputs['dirty_native_source_pins'])
assert len(epoch['modified_native_paths'])==7
untracked={n for n in git('ls-files','--others','--exclude-standard','--','layout','dom','servo','mfbt').decode().splitlines() if not n.startswith('artifacts/')}
assert untracked==set(epoch['untracked_native'])
message=HERE/'research-message.txt';assert message.read_text()==item['message'].rstrip()+'\n'
assert h.index_state(ROOT,ENV)==staged
assert h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==nested
before={'index':staged,'nested_index':nested}
save(HERE/'research-retry1-preflight.json',{'parent':parent,'tree':tree,'staged_patch_sha256':sha(HERE/'research-staged.patch'),'selection_sha256':sha(HERE/'research-selection.json'),'first_failed_log_sha256':sha(HERE/'research-commit.log'),'staged_index':staged,'nested_index':nested,'selected_files':207,'native_paths':7})
with (HERE/'research-retry1-commit.log').open('x') as f:
 rc=subprocess.run(GIT+['commit','--file',str(message)],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT).returncode
assert rc==0,'Signing retry failed; staging retained; do not rerun this helper'
assert git('ls-files','-v','-z')==flags
exec(compile(source[source.index("commit=git('rev-parse','HEAD')"):], 'reviewed-commit-helper-post-sign', 'exec'))
