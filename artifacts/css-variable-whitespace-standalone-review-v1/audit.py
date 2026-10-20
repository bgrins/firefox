import sys
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):raise RuntimeError('use -I -S')
from pathlib import Path
import hashlib,json,os,subprocess,runpy,shutil
R=Path(__file__).resolve().parent;repo=R.parent.parent
patch_text=runpy.run_path(str(R/'patch_text.py'))['patch_text']
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],cwd=repo,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
families=[(83,'css-attr-leading-whitespace-root-v1','css-attr-leading-whitespace-review-v1','a17a2be899e5206d2b2b8218f0ae69dad607adb14c27ce5150b0748832dbd4f3','ad608a212bd8'),(84,'css-variable-trailing-token-root-v1','css-variable-trailing-token-review-v1','df5f6e68901f1510f137d55a0a91f0611114749f0b027c650fe5d8209f69d4ce','bccea9c1fffc'),(85,'css-variable-escaped-whitespace-root-v1','css-variable-escaped-whitespace-review-v1','469772509f50cded60552157ef646f389221bda5c74cbe175b462bbebae93f52','fff2d758ef6b')]
records=[];auth=[]
for number,dirname,reviewname,pin,commit in families:
 root=repo/'artifacts'/dirname;review=repo/'artifacts'/reviewname
 manifest=(review/'FILES.json').read_bytes();assert sha(manifest)==pin
 m=json.loads(manifest);m={x['path']:x['sha256'] for x in m} if isinstance(m,list) else m
 for n,h in m.items():assert sha((review/n).read_bytes())==h,n
 auth.append({'fix':number,'review':reviewname,'manifest_sha256':pin,'authenticated_inputs':len(m)})
 package=json.loads((root/'PACKAGING.json').read_text())['standalone'];patch=(root/'standalone-native-wpt.patch').read_bytes();assert sha(patch)==package['sha256'];base=package['base'];tree=package['candidate_tree'];paths=package['paths'];assert len(paths)==2
 actualpaths=git('diff','--name-only',base,tree).decode().splitlines();assert actualpaths==paths
 parts=patch.decode().split('diff --git ')[1:];assert len(parts)==2;assert [x.splitlines()[0].split(' b/',1)[1] for x in parts]==paths
 folder=R/str(number);folder.mkdir(exist_ok=True)
 for p in ['PACKAGING.json','standalone-native-wpt.patch','NATIVE-REVIEW.json']:shutil.copyfile(root/p,folder/p)
 for i,(path,part) in enumerate(zip(paths,parts)):
  original=git('show',base+':'+path) if i==0 else b''
  if i==1:assert not git('ls-tree',base,'--',path)
  expected=git('show',tree+':'+path)
  after=patch_text(original.decode(),part).encode();assert after==expected;assert patch_text(after.decode(),part,True).encode()==original
  (folder/('candidate.rs' if i==0 else 'test.html')).write_bytes(after)
  if i==0:
   assert original==(R/'upstream-custom_properties.rs').read_bytes()==(root/'package-standalone/original.rs').read_bytes()
   assert after==(root/'package-standalone/candidate.rs').read_bytes();assert sha(after)==package['source_sha256']
  else:assert git('show',commit+':'+path)==after
 mainpaths=git('diff-tree','--no-commit-id','--name-only','-r',commit).decode().splitlines();assert mainpaths==paths
 records.append({'fix':number,'upstream_base':base,'upstream_candidate_tree':tree,'paths':paths,'patch_sha256':sha(patch),'native_sha256':sha((folder/'candidate.rs').read_bytes()),'test_sha256':sha((folder/'test.html').read_bytes()),'pure_exact_apply_reverse':True,'git_blobs_match_retained':True,'main_commit':git('rev-parse',commit).decode().strip(),'main_commit_exact_same_two_paths':True,'main_commit_test_bytes_equal':True,'isolated_upstream_runtime':False})
(R/'REVIEW-AUTH.json').write_text(json.dumps(auth,indent=2)+'\n');(R/'AUDIT.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2))
