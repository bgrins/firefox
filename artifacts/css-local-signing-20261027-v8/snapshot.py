import hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'artifacts/css-unfinished-work-checkpoint-20261027-v5'
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args,env=ENV):return subprocess.check_output(GIT+list(args),cwd=ROOT,env=env)
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(HERE/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
HERE.mkdir()
base=git('rev-parse','HEAD').decode().strip()
old=json.loads((ROOT/'artifacts/css-unfinished-work-checkpoint-20261027-v4/SOURCE-PINS.json').read_text())
names=sorted(set(old)|{'servo/components/style/custom_properties.rs'})
assert set(git('diff','--name-only').decode().splitlines())<=set(names)
assert not git('diff','--cached','--name-only')
before={k:sha(git(*args)) for k,args in {'entries':['ls-files','--stage','-z'],'flags':['ls-files','-v','-z']}.items()}
pins={n:sha((ROOT/n).read_bytes()) for n in names}
with tempfile.TemporaryDirectory(prefix='css-wip-snapshot-',dir='/private/tmp') as tmp:
 env=dict(ENV,GIT_INDEX_FILE=str(Path(tmp)/'index'));git('read-tree',base,env=env)
 pathspec=Path(tmp)/'paths';pathspec.write_bytes(b''.join(n.encode()+b'\0' for n in names))
 git('add','-f','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul',env=env)
 changed=git('diff','--cached','--name-only',base,env=env).decode().splitlines()
 for n,h in pins.items():assert sha(git('show',':'+n,env=env))==h,n
 patch=HERE/'unfinished.patch';patch.write_bytes(git('diff','--cached','--binary','--full-index',base,env=env))
 git('apply','--cached','--reverse','--check',str(patch),env=env)
 git('apply','--cached','--reverse',str(patch),env=env)
 assert git('write-tree',env=env).strip()==git('rev-parse',base+'^{tree}').strip()
 git('apply','--cached','--check',str(patch),env=env)
 git('apply','--cached',str(patch),env=env)
 for n,h in pins.items():assert sha(git('show',':'+n,env=env))==h,n
assert git('rev-parse','HEAD').decode().strip()==base
assert before=={k:sha(git(*args)) for k,args in {'entries':['ls-files','--stage','-z'],'flags':['ls-files','-v','-z']}.items()}
assert all(sha((ROOT/n).read_bytes())==h for n,h in pins.items())
save('BASE.json',{'commit':base,'branch':git('symbolic-ref','HEAD').decode().strip()})
save('SOURCE-PINS.json',pins)
save('CHECK.json',{'source_count':len(pins),'unfinished_count':len(changed),'unfinished_paths':changed,'forward_and_reverse_application_verified':True,'live_head_index_bodies_preserved':True,'accepted_fix_count':135,'typed_demand_build_active_at_capture':True})
(HERE/'README.md').write_text('# Unfinished work checkpoint\n\nApply unfinished.patch to the commit in BASE.json to recover the current prototypes and fixtures. Exact forward and reverse application and all source hashes were checked in an isolated index. Live source bodies and the real index were preserved.\n\nThis snapshot includes typed attribute demand and its compile correction. Rust compilation succeeded; the full native build was still running at capture, and the new host tests had not run. It is a recovery checkpoint, not a set of accepted production fixes. Existing accepted fixes remain separate native-plus-WPT commits. The accepted count stays 135. Unrelated directories, nested Lean repository and build outputs are excluded.\n')
save('FILES.json',{str(f.relative_to(HERE)):sha(f.read_bytes()) for f in sorted(HERE.iterdir()) if f.is_file()})
print('Verified recovery snapshot:',len(changed),'unfinished paths; bytes',patch.stat().st_size,flush=True)
