import copy, hashlib, importlib.util, json, os, stat, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args,env=ENV): return subprocess.check_output(GIT+list(args),cwd=ROOT,env=env)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 with p.open('x') as f: json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('preserve','artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch','artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
for name in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES']: assert not os.environ.get(name),name
config=json.loads((HERE/'REORG-CONFIG.json').read_text());epoch=json.loads((HERE/'CURRENT-EPOCH.json').read_text());before=a.verify_current(h,ROOT,ENV,epoch)
old_tip=git('rev-parse','HEAD').decode().strip();assert old_tip==config['expected_tip']
branch=git('symbolic-ref','HEAD').decode().strip();assert branch=='refs/heads/stylo-bloom-verification-2'
old_research='366551d71eeaa911948b28b56f6bc647d0dc7079';old_native='75271a173ba0dda9d63728fa21aa12c91ddd85d1';old_checkpoint='dc8be586a97d4809aa16c8f5260d641359d14c40';base='feaec25f9647bc603994ce1c864e36107f23c7b2'
assert git('rev-parse',old_research+'^').decode().strip()==base
assert git('rev-parse',old_tip+'^').decode().strip()==old_checkpoint
assert not git('diff','--cached','--name-only')
research=set(config['research_paths']);metadata=set(config['metadata_paths']);assert len(metadata)==2 and all(n.startswith('artifacts/') for n in research)
entries={}
for row in git('ls-tree','-r','-z',old_tip,'--',*sorted(research|metadata)).split(b'\0'):
 if not row:continue
 fields,name=row.split(b'\t',1);mode,kind,oid=fields.decode().split();assert kind=='blob';entries[name.decode()]=(mode,oid)
assert set(entries)==research|metadata
for n,pin in config['source_pins'].items():assert hashlib.sha256(git('show',old_tip+':'+n)).hexdigest()==pin,n
save(HERE/'REORG-BEFORE.json',before)
def make(label,tree,parent,original,message=None):
 receipt=HERE/(label+'-rewrite.json')
 if receipt.exists():
  r=json.loads(receipt.read_text());assert r['tree']==tree and r['parent']==parent;return r['commit']
 identity=git('show','-s','--format=%an%n%ae%n%aI',original).decode().splitlines();assert len(identity)==3
 text=git('show','-s','--format=%B',original).decode() if message is None else message+'\n'
 msg=HERE/(label+'-rewrite-message.txt');msg.write_text(text)
 env=dict(ENV,GIT_AUTHOR_NAME=identity[0],GIT_AUTHOR_EMAIL=identity[1],GIT_AUTHOR_DATE=identity[2])
 with (HERE/(label+'-rewrite-signing.log')).open('w') as log:
  created=subprocess.run(GIT+['commit-tree','-S',tree,'-p',parent,'-F',str(msg)],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=log,check=True)
 commit=created.stdout.decode().strip();assert git('rev-parse',commit+'^{tree}').decode().strip()==tree and git('rev-parse',commit+'^').decode().strip()==parent
 assert git('show','-s','--format=%an%n%ae%n%aI',commit).decode().splitlines()==identity
 with (HERE/(label+'-rewrite-verify.log')).open('w') as log:
  subprocess.run(GIT+['-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',commit],cwd=ROOT,env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True)
 save(receipt,{'commit':commit,'tree':tree,'parent':parent,'original':original,'signature_verified':True,'author_and_date_preserved':True});print(label,commit,flush=True);return commit
with tempfile.TemporaryDirectory(prefix='easing-history-index-',dir='/private/tmp') as tmp:
 env=dict(ENV,GIT_INDEX_FILE=str(Path(tmp)/'index'))
 def assemble(original,paths):
  git('read-tree',original,env=env)
  body=b''.join((entries[n][0]+' '+entries[n][1]+'\t'+n+'\n').encode() for n in sorted(paths))
  subprocess.run(GIT+['update-index','--index-info'],cwd=ROOT,env=env,input=body,check=True)
  return git('write-tree',env=env).decode().strip()
 research_tree=assemble(old_research,research)
 new_research=make('steps-research',research_tree,base,old_research,'No bug - Record easing range verification and expectation corrections. r?#firefox-style-system-reviewers')
 native_tree=assemble(old_native,research|metadata)
 new_native=make('steps-native',native_tree,new_research,old_native)
 final_tree=git('rev-parse',old_tip+'^{tree}').decode().strip()
 new_checkpoint=make('checkpoint',final_tree,new_native,old_checkpoint)
original_native=set(git('diff','--name-only',old_research,old_native).decode().splitlines());assert len(original_native)==4
assert set(git('diff','--name-only',new_research,new_native).decode().splitlines())==original_native|metadata
assert git('diff','--binary',old_research,old_native,'--',*sorted(original_native))==git('diff','--binary',new_research,new_native,'--',*sorted(original_native))
original_checkpoint=set(git('diff','--name-only',old_native,old_checkpoint).decode().splitlines())
assert set(git('diff','--name-only',new_native,new_checkpoint).decode().splitlines())==original_checkpoint-research
assert not git('diff','--name-only',old_tip,new_checkpoint)
assert git('rev-list','--count',base+'..'+old_tip).strip()==b'4' and git('rev-list','--count',base+'..'+new_checkpoint).strip()==b'3'
(HERE/'RANGE-DIFF.txt').write_bytes(git('range-diff',base+'..'+old_tip,base+'..'+new_checkpoint))
a.verify_current(h,ROOT,ENV,epoch)
backup='refs/heads/backup-easing-metadata-20261027-'+old_tip[:12]
transaction='start\ncreate '+backup+' '+old_tip+'\nupdate '+branch+' '+new_checkpoint+' '+old_tip+'\nprepare\ncommit\n'
subprocess.run(GIT+['update-ref','--stdin'],cwd=ROOT,env=ENV,input=transaction.encode(),check=True,stdout=subprocess.DEVNULL)
state=h.index_state(ROOT,ENV);assert all(state[k]==before['index'][k] for k in ['entries','cached_diff','working_diff','raw_index'])
current=copy.deepcopy(epoch);current['semantic_index']=h.semantic_index(state);a.verify_current(h,ROOT,ENV,current)
save(HERE/'REORG-EPOCH.json',current);(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
save(HERE/'REORG-RESULT.json',{'status':'SIGNED_CONTENT_PRESERVING_EASING_REWRITE','backup':backup,'old_tip':old_tip,'new_tip':new_checkpoint,'rewrites':{old_research:new_research,old_native:new_native,old_checkpoint:new_checkpoint},'absorbed':old_tip,'final_tree_unchanged':True,'native_fix_paths':sorted(original_native|metadata),'research_precedes_native':True,'signatures_verified':True,'source_binary_and_staging_preserved':True})
print('Reorganized signed history; final tree and working sources unchanged',new_checkpoint,flush=True)
