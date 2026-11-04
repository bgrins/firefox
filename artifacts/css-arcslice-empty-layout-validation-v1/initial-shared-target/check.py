from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'artifacts/stylo-bloom-tools/creusot-gate/matcher-dyn-capability-candidate/backend-v1/actual-context-v1/header-swap-defect-v1'
TC=OLD/'rustup/toolchains/nightly-2026-09-17-aarch64-apple-darwin'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=json.loads((HERE/'TESTED-INPUTS.json').read_text())
vendor=json.loads((HERE/'VENDOR.json').read_text())
def verify():
 for path,digest in inputs.items():assert sha(HERE/path)==digest,path
 for folder,record in vendor.items():
  for path,digest in record['files'].items():assert sha(ROOT/folder/path)==digest,(folder,path)
verify()
rows=[]
with tempfile.TemporaryDirectory(prefix='arcslice-empty-fix-',dir='/private/tmp') as scratch:
 scratch=Path(scratch)
 for folder,record in vendor.items():
  target=scratch/'vendor'/Path(folder).name;shutil.copytree(ROOT/folder,target)
  checksum=json.loads((target/'.cargo-checksum.json').read_text())
  checksum['files']={str(p.relative_to(target)):sha(p) for p in target.rglob('*') if p.is_file() and p.name!='.cargo-checksum.json'}
  (target/'.cargo-checksum.json').write_text(json.dumps(checksum))
  assert sha(target/'.cargo-checksum.json')==record['temporary_checksum_sha256']
 env=dict(os.environ,RUSTUP_HOME=str(OLD/'rustup'),CARGO_HOME=str(OLD/'cargo-home'),CARGO_TARGET_DIR=str(scratch/'target'),PATH=str(TC/'bin')+':/Users/bgrins/.cargo/bin:/usr/bin:/bin:/usr/sbin:/sbin')
 for variant in ['current','dst']:
  command=[str(TC/'bin/cargo'),'miri','run','--offline','--locked','-j','2','--manifest-path',str(HERE/variant/'Cargo.toml'),'--bin','alignment','--config','source.crates-io.replace-with="vendored-sources"','--config','source.vendored-sources.directory='+json.dumps(str(scratch/'vendor'))]
  for debug in ['on','off']:
   env['CARGO_PROFILE_DEV_DEBUG_ASSERTIONS']='true' if debug=='on' else 'false'
   for model in ['tree','stacked']:
    env['MIRIFLAGS']='-Zmiri-tree-borrows' if model=='tree' else ''
    name=f'{variant}-{debug}-{model}'
    cmd=command+['--',debug]
    with (HERE/(name+'.log')).open('w') as log:result=subprocess.run(cmd,cwd=scratch,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    text=(HERE/(name+'.log')).read_text()
    row={'case':name,'exit':result.returncode,'command':cmd,'flags':env['MIRIFLAGS'],'log_sha256':sha(HERE/(name+'.log'))}
    rows.append(row);print(json.dumps(row),flush=True)
    assert result.returncode==0,(name,text[-4000:])
    assert text.count('read-clone-drop passed')==8,name
    assert 'eight empty cases and two nonempty ZST refusals passed' in text,name
    assert 'debug_assertions='+str(debug=='on').lower() in text,name
 verify()
record={'rows':rows,'scratch_removed':not scratch.exists(),'source_vendor_pre_post_unchanged':True,'inputs':{name:sha(HERE/name) for name in ['check.py','main.rs','TESTED-INPUTS.json','VENDOR.json','SOURCE-ROLES.json','BASE-FFI-ROLES.json']},'scope':'Eight actual configurations, each eight empty constructor/read/clone/drop cases and two nonempty ZST refusals; strict leak checks, no Gecko refcount-logging feature.'}
(HERE/'CHECK.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'configurations':len(rows),'scratch_removed':record['scratch_removed']}),flush=True)
