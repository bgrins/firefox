from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'artifacts/css-arcslice-empty-alignment-current-v1/current'
OLD=ROOT/'artifacts/stylo-bloom-tools/creusot-gate/matcher-dyn-capability-candidate/backend-v1/actual-context-v1/header-swap-defect-v1'
TC=OLD/'rustup/toolchains/nightly-2026-09-17-aarch64-apple-darwin'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=json.loads((BASE.parent/'SOURCE.json').read_text())['files']
inputs={name:sha(HERE/name) for name in ['module.rs','adapter.rs','original/Cargo.toml','check-original.py','VENDOR.json']}
vendor=json.loads((HERE/'VENDOR.json').read_text())
def verify():
 for name,digest in inputs.items():assert sha(HERE/name)==digest,name
 for name,digest in sources.items():assert sha(BASE/name)==digest,name
 for folder,row in vendor.items():
  for name,digest in row['files'].items():assert sha(ROOT/folder/name)==digest
verify();rows=[]
with tempfile.TemporaryDirectory(prefix='arcslice-unit-',dir='/private/tmp') as scratch:
 scratch=Path(scratch)
 for folder,row in vendor.items():
  dest=scratch/'vendor'/Path(folder).name;shutil.copytree(ROOT/folder,dest)
  checksum=json.loads((dest/'.cargo-checksum.json').read_text())
  checksum['files']={str(q.relative_to(dest)):sha(q) for q in dest.rglob('*') if q.is_file() and q.name!='.cargo-checksum.json'}
  (dest/'.cargo-checksum.json').write_text(json.dumps(checksum));assert sha(dest/'.cargo-checksum.json')==row['temporary_checksum_sha256']
 for variant in ['original']:
  env=dict(os.environ,RUSTUP_HOME=str(OLD/'rustup'),CARGO_HOME=str(OLD/'cargo-home'),CARGO_TARGET_DIR=str(scratch/('target-'+variant)),PATH=str(TC/'bin')+':/Users/bgrins/.cargo/bin:/usr/bin:/bin:/usr/sbin:/sbin',MIRIFLAGS='-Zmiri-tree-borrows',TESTED_VARIANT='current',CARGO_PROFILE_DEV_DEBUG_ASSERTIONS='true')
  command=[str(TC/'bin/cargo'),'miri','test','--offline','-j','2','--manifest-path',str(HERE/variant/'Cargo.toml'),'--lib','--config','source.crates-io.replace-with="vendored-sources"','--config','source.vendored-sources.directory='+json.dumps(str(scratch/'vendor')),'--','--nocapture','--test-threads=1']
  with (HERE/(variant+'.log')).open('w') as log:r=subprocess.run(command,cwd=scratch,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
  text=(HERE/(variant+'.log')).read_text();row={'variant':variant,'exit':r.returncode,'command':command,'log_sha256':sha(HERE/(variant+'.log'))};rows.append(row);print(json.dumps(row),flush=True)
  assert r.returncode==101,(variant,text[-3000:])
  assert 'Need to increase the alignment of EMPTY_ARC_SLICE' in text
  assert 'Undefined Behavior' not in text
  assert 'tests::empty_slices_preserve_element_layout' in text and 'FAILED' in text
  assert '1 passed; 1 failed' in text and 'variant=current' in text
  assert 'header_reference_words='+('2' if variant=='dst' else '1') in text
 verify()
record={'rows':rows,'inputs':inputs,'matrix_source_inputs_sha256':sha(BASE.parent/'SOURCE.json'),'scratch_removed':not scratch.exists(),'source_vendor_pre_post_unchanged':True,'scope':'Original-current same delivered module: intended debug alignment assertion failure, one fingerprint guard passes; not a new UB run.'}
(HERE/'ORIGINAL-CHECK.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'passed':len(rows),'scratch_removed':record['scratch_removed']}),flush=True)
