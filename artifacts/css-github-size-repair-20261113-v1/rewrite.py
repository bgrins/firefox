import hashlib,json,os,re,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
PLAN=json.loads((OUT/'DISCOVERY.json').read_text())
BRANCH='refs/heads/stylo-bloom-verification-2'
BACKUP='refs/heads/backup-stylo-bloom-verification-2-before-size-repair-20261113'
CANDIDATE='refs/heads/stylo-bloom-verification-2-size-repair'
PATHS={row['path'] for row in PLAN['large_blobs']}
def git(*args,data=None,env=None):
 return subprocess.run(GIT+list(args),cwd=ROOT,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,check=True).stdout

def headers(raw):
 head,msg=raw.split(b'\n\n',1); result=[]
 for line in head.split(b'\n'):
  if line.startswith(b' '): result[-1][1]+=b'\n'+line
  else:
   key,value=line.split(b' ',1);result.append([key,value])
 return result,msg

def identity(value,prefix):
 m=re.fullmatch(rb'(.*) <([^<>]*)> ([0-9]+) ([+-][0-9]{4})',value);assert m,value
 name,email,seconds,zone=m.groups()
 return {prefix+'_NAME':name.decode(),prefix+'_EMAIL':email.decode(),prefix+'_DATE':'@'+seconds.decode()+' '+zone.decode()}

cache={}
def prune(tree,prefix=''):
 key=(tree,prefix)
 if key in cache:return cache[key]
 raw=git('cat-file','tree',tree);entries=[];pos=0
 while pos<len(raw):
  end=raw.index(b'\0',pos);mode,name=raw[pos:end].split(b' ',1);oid=raw[end+1:end+21];assert len(oid)==20
  path=prefix+name.decode();pos=end+21
  if path in PATHS:
   assert mode in (b'100644',b'100755')
   assert oid.hex() in {r['oid'] for r in PLAN['large_blobs']}
   continue
  if mode==b'40000' and any(p.startswith(path+'/') for p in PATHS): oid=bytes.fromhex(prune(oid.hex(),path+'/'))
  entries.append(mode+b' '+name+b'\0'+oid)
 new=b''.join(entries)
 result=tree if new==raw else git('hash-object','-w','-t','tree','--stdin',data=new).decode().strip()
 cache[key]=result;return result

assert git('rev-parse',BRANCH).decode().strip()==PLAN['original_tip']
assert not git('diff','--cached','--name-only')
assert git('diff','--binary')==(OUT/'working-tree-before.patch').read_bytes()
assert git('ls-files','--stage')==(OUT/'index-before.txt').read_bytes()
for ref in [BACKUP,CANDIDATE]:
 assert subprocess.run(GIT+['show-ref','--verify','--quiet',ref],cwd=ROOT).returncode==1,ref
git('update-ref',BACKUP,PLAN['original_tip'],'0'*40)
commits=git('rev-list','--reverse',PLAN['base']+'..'+PLAN['original_tip']).decode().splitlines()
mapping={};records=[];previous=PLAN['base'];previous_candidate='0'*40
with (OUT/'signatures.log').open('wb') as log:
 for i,old in enumerate(commits):
  old_headers,msg=headers(git('cat-file','commit',old)); fields=dict(old_headers)
  assert set(fields)<={b'tree',b'parent',b'author',b'committer',b'gpgsig'},set(fields)
  parents=[v.decode() for k,v in old_headers if k==b'parent'];assert len(parents)==1
  parent=mapping.get(parents[0],parents[0]);assert parent==previous
  tree=prune(fields[b'tree'].decode())
  changed=tree!=fields[b'tree'].decode() or parent!=parents[0]
  if changed:
   env=dict(os.environ,**identity(fields[b'author'],'GIT_AUTHOR'),**identity(fields[b'committer'],'GIT_COMMITTER'))
   new=git('commit-tree','-S',tree,'-p',parent,'-F','-',data=msg,env=env).decode().strip()
   actual,new_msg=headers(git('cat-file','commit',new));nf=dict(actual)
   assert new_msg==msg and nf[b'author']==fields[b'author'] and nf[b'committer']==fields[b'committer']
   assert nf[b'tree'].decode()==tree and nf[b'parent'].decode()==parent and b'gpgsig' in nf
   checked=subprocess.run(GIT+['-c','gpg.ssh.allowedSignersFile='+str(OUT/'allowed-signers'),'verify-commit',new],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   log.write((old+' -> '+new+'\n').encode()+checked.stdout);log.flush();assert checked.returncode==0,checked.stdout
  else:new=old
  mapping[old]=new;previous=new
  records.append(dict(old=old,new=new,changed=changed,old_tree=fields[b'tree'].decode(),new_tree=tree))
  (OUT/'PROGRESS.json').write_text(json.dumps(dict(completed=i+1,total=len(commits),records=records),indent=2)+'\n')
  if (i+1)%10==0 or i+1==len(commits):
   git('update-ref',CANDIDATE,new,previous_candidate);previous_candidate=new
   print(json.dumps(dict(completed=i+1,total=len(commits),tip=new)),flush=True)
assert git('rev-parse',BRANCH).decode().strip()==PLAN['original_tip']
assert git('diff','--binary')==(OUT/'working-tree-before.patch').read_bytes()
assert git('ls-files','--stage')==(OUT/'index-before.txt').read_bytes()
(OUT/'COMMIT-MAP.json').write_text(json.dumps(mapping,indent=2)+'\n')
(OUT/'REWRITE.json').write_text(json.dumps(dict(status='CANDIDATE_CREATED_MAIN_BRANCH_UNCHANGED',base=PLAN['base'],original_tip=PLAN['original_tip'],new_tip=previous,backup=BACKUP,candidate=CANDIDATE,commits=len(commits),rewritten=sum(r['changed'] for r in records),removed_paths=sorted(PATHS),signatures_verified=True),indent=2)+'\n')
print((OUT/'REWRITE.json').read_text(),flush=True)
