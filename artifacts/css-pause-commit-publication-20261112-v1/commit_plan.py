import hashlib,json,subprocess,sys
from pathlib import Path
plan_path=Path(sys.argv[1]); plan=json.loads(plan_path.read_text()); label=plan_path.stem.removesuffix('-PLAN'); out=plan_path.parent
git=['git','--no-optional-locks','-c','core.fsmonitor=false']
def call(*args): return subprocess.check_output(git+list(args))
assert not call('diff','--cached','--name-only')
source=Path('layout/generic/nsGridContainerFrame.cpp'); before=hashlib.sha256(source.read_bytes()).hexdigest()
for name,pin in plan['files'].items():
 p=Path(name); assert hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256'] and p.stat().st_size==pin['bytes'],name
parent=call('rev-parse','HEAD').decode().strip()
paths=out/(label+'-paths.nul'); paths.write_bytes(b''.join(str(p).encode()+b'\0' for p in plan['files']))
subprocess.run(git+['add','-f','--pathspec-from-file='+str(paths),'--pathspec-file-nul'],check=True)
assert set(call('diff','--cached','--name-only','-z').decode().strip('\0').split('\0'))==set(plan['files'])
message=out/(label+'-message.txt'); message.write_text(plan['subject']+'\n')
with (out/(label+'-commit.log')).open('wb') as log:
 r=subprocess.run(git+['commit','-F',str(message)],stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0, 'Commit failed; inspect retained log'
head=call('rev-parse','HEAD').decode().strip()
with (out/(label+'-signature.log')).open('wb') as log:
 r=subprocess.run(git+['-c','gpg.ssh.allowedSignersFile='+str((out/'allowed-signers').resolve()),'verify-commit',head],stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0,'Signature verification failed'
assert not call('diff','--cached','--name-only')
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
for name,pin in plan['files'].items(): assert hashlib.sha256(call('show',head+':'+name)).hexdigest()==pin['sha256'],name
result=dict(commit=head,parent=parent,files=len(plan['files']),signature_verified=True,blob_hashes_verified=True,native_source_unchanged=True)
(out/(label+'-RESULT.json')).write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result))
