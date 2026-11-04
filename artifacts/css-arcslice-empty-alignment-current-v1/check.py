import hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'artifacts/stylo-bloom-tools/creusot-gate/matcher-dyn-capability-candidate/backend-v1/actual-context-v1/header-swap-defect-v1'
TC=OLD/'rustup/toolchains/nightly-2026-09-17-aarch64-apple-darwin'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=json.loads((HERE/'SOURCE.json').read_text())['files']
vendor=json.loads((HERE/'VENDOR.json').read_text())
def verify():
 for path,digest in sources.items():assert sha(HERE/'current'/path)==digest,path
 for folder,record in vendor.items():
  for path,digest in record['files'].items():assert sha(ROOT/folder/path)==digest,(folder,path)
verify()
rows=[]
with tempfile.TemporaryDirectory(prefix='arcslice-alignment-',dir='/private/tmp') as scratch:
 scratch=Path(scratch)
 for folder,record in vendor.items():
  target=scratch/'vendor'/Path(folder).name
  shutil.copytree(ROOT/folder,target)
  checksum=json.loads((target/'.cargo-checksum.json').read_text())
  checksum['files']={str(p.relative_to(target)):sha(p) for p in target.rglob('*') if p.is_file() and p.name!='.cargo-checksum.json'}
  (target/'.cargo-checksum.json').write_text(json.dumps(checksum))
  assert sha(target/'.cargo-checksum.json')==record['temporary_checksum_sha256']
 env=dict(os.environ,RUSTUP_HOME=str(OLD/'rustup'),CARGO_HOME=str(OLD/'cargo-home'),CARGO_TARGET_DIR=str(scratch/'target'),PATH=str(TC/'bin')+':/Users/bgrins/.cargo/bin:/usr/bin:/bin:/usr/sbin:/sbin',MIRIFLAGS='-Zmiri-tree-borrows -Zmiri-ignore-leaks')
 command=[str(TC/'bin/cargo'),'miri','run','--offline','-j','2','--manifest-path',str(HERE/'current/Cargo.toml'),'--bin','alignment','--config','source.crates-io.replace-with="vendored-sources"','--config','source.vendored-sources.directory='+json.dumps(str(scratch/'vendor'))]
 for debug in ['on','off']:
  env['CARGO_PROFILE_DEV_DEBUG_ASSERTIONS']='true' if debug=='on' else 'false'
  for case in ['normal-default','normal-empty','high-default-read','high-empty-read','high-default-drop','high-empty-drop']:
   name=case+'-'+debug
   cmd=command+['--',case,debug]
   with (HERE/(name+'.log')).open('w') as log:
    result=subprocess.run(cmd,cwd=scratch,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
   text=(HERE/(name+'.log')).read_text()
   assert 'debug_assertions='+str(debug=='on').lower() in text,(name,'did not reach target')
   if case.startswith('normal'):
    classification='normal-success'
    assert result.returncode==0 and 'dropped normal' in text,name
   elif debug=='on':
    classification='debug-assertion-panic'
    assert result.returncode!=0 and 'Need to increase' in text and 'Undefined Behavior' not in text,name
   else:
    classification='observed-undefined-behavior' if 'Undefined Behavior' in text else 'other'
   row={'case':name,'exit':result.returncode,'classification':classification,'command':cmd,'log_sha256':sha(HERE/(name+'.log'))}
   rows.append(row)
   print(json.dumps(row),flush=True)
 verify()
record={'rows':rows,'scratch_removed':not scratch.exists(),'input_sha256':{p:sha(HERE/p) for p in ['SOURCE.json','VENDOR.json','check.py']},'cargo_lock_sha256':sha(HERE/'current/Cargo.lock'),'source_and_vendor_pre_post_unchanged':True,'miri_flags':env['MIRIFLAGS'],'scope':'Exact current servo_arc plus complete unchanged a6 client crates; intentional leaked static singleton is excluded from leak reporting.'}
(HERE/'CHECK.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'cases':len(rows),'scratch_removed':record['scratch_removed']}),flush=True)
