import ast,copy,hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('transition',HERE/'install.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);o=m.ownership_helper()
positive=[];negative=[]
def rejects(label,call):
    try:call()
    except (AssertionError,RuntimeError,FileNotFoundError):negative.append(label)
    else:raise AssertionError('accepted corruption: '+label)
ast.parse((HERE/'install.py').read_text())
policy,roles=m.read(HERE/'POLICY.json'),m.read(HERE/'SOURCE-ROLES.json')
epoch,role,owned=[m.read(HERE/('INITIAL-'+n+'.json')) for n in ['EPOCH','ROLE','OWNED']]
m.check_state(policy,roles,epoch,role,owned,'original',policy['initial_epoch_sha256']);positive.append('exact rebound state')
for key,value in [('head','0'*40),('initial_epoch_sha256','0'*64)]:
 bad=copy.deepcopy(policy);bad[key]=value
 rejects(key,lambda:m.check_state(bad,roles,epoch,role,owned,'original',policy['initial_epoch_sha256']))
for label,change in [('owned inode',lambda e,r,w:w[next(iter(w))].update(identity=[0,0])),('native hash',lambda e,r,w:e['pins'].update({next(iter(roles)):'0'*64})),('native inventory',lambda e,r,w:e['modified_native_paths'].pop()),('wrong role',lambda e,r,w:r.update(role='original'))]:
 e,r,w=copy.deepcopy((epoch,role,owned));change(e,r,w)
 rejects(label,lambda:m.check_state(policy,roles,e,r,w,'original',policy['initial_epoch_sha256']))
census='1 0 1 launchd\n10 1 10 zsh\n11 10 10 python3 installer\n12 1 12 unrelated\n'
m.process_census_clear(census,11);positive.append('quiet calibrated census')
for label,extra in [('objdir',f'13 1 13 {ROOT}/objdir-full.noindex/dist/bin/firefox\n'),('build','13 1 13 python ./mach build binaries\n'),('wpt','13 1 13 python ./mach wpt test\n'),('gtest','13 1 13 python ./mach gtest Suite\n')]:
 rejects(label,lambda:m.process_census_clear(census+extra,11))
rejects('missing own pid',lambda:m.process_census_clear(census,99))
rejects('malformed census',lambda:m.process_census_clear('junk',11))
with tempfile.TemporaryDirectory(prefix='zoom-standalone-check-') as temp:
 scratch=Path(temp)
 for name,rec in roles.items():
  path=scratch/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/rec['original']).read_bytes())
 patch=ROOT/'artifacts/css-registered-zoom-normalization-proposal-v3/native.patch'
 for args,key in [([], 'candidate_sha256'),(['-R'],'original_sha256'),([], 'candidate_sha256')]:
  run=subprocess.run(['patch','-p1','--fuzz=0',*args,'-i',str(patch)],cwd=scratch,capture_output=True,text=True)
  assert run.returncode==0,run.stdout+run.stderr
  for name,rec in roles.items():assert m.sha(scratch/name)==rec.get(key,rec['original_sha256'])
 positive.append('exact seven-file forward reverse reapply; A2 stays original')
 fake=scratch/'guard';fake.mkdir();(fake/'native').write_bytes(b'old');(fake/'control').write_bytes(b'control')
 oldroot,oldauth=m.ROOT,m.authenticate;m.ROOT=fake;m.authenticate=lambda pin:None
 native={'native':o.claim(fake,'native',m.sha(fake/'native'))};control={'control':o.claim(fake,'control',m.sha(fake/'control'))}
 m.prewrite_guard(o,control,native,'unused');positive.append('immediate claims')
 for name in ['native','control']:
  path=fake/name;data=path.read_bytes();path.write_bytes(b'changed')
  rejects(name+' bytes',lambda:m.prewrite_guard(o,control,native,'unused'));path.write_bytes(data)
  saved=fake/(name+'-saved');path.rename(saved);path.write_bytes(data)
  rejects(name+' inode',lambda:m.prewrite_guard(o,control,native,'unused'));path.unlink();saved.rename(path)
  path.rename(saved);path.symlink_to(saved)
  rejects(name+' symlink',lambda:m.prewrite_guard(o,control,native,'unused'));path.unlink();saved.rename(path)
 item=native['native'];identity=item['identity'][:];o.write_owned(fake,item,b'new');o.write_owned(fake,item,b'old')
 assert item['identity']==identity and (fake/'native').read_bytes()==b'old';positive.append('buffered write rollback same inode')
 m.authenticate=lambda pin:(_ for _ in ()).throw(AssertionError('manifest drift'))
 rejects('changed package',lambda:m.prewrite_guard(o,control,native,'unused'))
 m.ROOT,m.authenticate=oldroot,oldauth
 runtime=scratch/'runtime';runtime.mkdir();job=runtime/'job';job.mkdir();(job/'COMMAND.json').write_text('{}')
 rejects('unfinished recorded command',lambda:o.quiescent(runtime));(job/'RESULT.json').write_text('{}');o.quiescent(runtime);positive.append('terminal command inventory')
 oldkill=o.os.killpg;o.os.killpg=lambda pgid,sig:None
 rejects('live owned group',lambda:o.group_absent(99999))
 def absent(pgid,sig):raise ProcessLookupError()
 o.os.killpg=absent;o.group_absent(99999);positive.append('absent owned group');o.os.killpg=oldkill
assert not scratch.exists()
result={'positive':positive,'negative':negative,'main_executed':False,'live_mutation':False,'scratch_removed':True}
with (HERE/'CHECK.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'positive':len(positive),'negative':len(negative),'scratch_removed':True}))
