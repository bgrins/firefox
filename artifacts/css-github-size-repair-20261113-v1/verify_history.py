import hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args):return subprocess.check_output(GIT+list(args),cwd=ROOT)
def read(name):return json.loads((OUT/name).read_text())
plan=read('DISCOVERY.json');rewrite=read('REWRITE.json');mapping=read('COMMIT-MAP.json');removed=set(rewrite['removed_paths'])
commits=git('rev-list','--reverse',plan['base']+'..'+plan['original_tip']).decode().splitlines();assert list(mapping)==commits
new_commits=git('rev-list','--reverse',plan['base']+'..'+rewrite['new_tip']).decode().splitlines();assert new_commits==list(mapping.values())
checks=[]
for old,new in mapping.items():
 delta=git('diff-tree','--no-commit-id','--no-renames','--name-status','-r','-z',old,new).split(b'\0');assert delta[-1]==b'';delta=delta[:-1]
 assert len(delta)%2==0
 differences=[]
 for status,path in zip(delta[::2],delta[1::2]):
  assert status==b'D' and path.decode() in removed,(old,new,status,path)
  differences.append(path.decode())
 # Tree equality outside the allowlisted deletions proves every other path's bytes and mode are unchanged.
 old_info=git('show','-s','--format=%an%x00%ae%x00%at%x00%cn%x00%ce%x00%ct%x00%B',old)
 new_info=git('show','-s','--format=%an%x00%ae%x00%at%x00%cn%x00%ce%x00%ct%x00%B',new)
 assert old_info==new_info,(old,new,'metadata')
 old_parent=git('rev-parse',old+'^').decode().strip();new_parent=git('rev-parse',new+'^').decode().strip()
 assert new_parent==mapping.get(old_parent,old_parent)
 checks.append(dict(old=old,new=new,only_deleted_paths=differences))
 assert git('rev-parse','refs/heads/stylo-bloom-verification-2').decode().strip()==plan['original_tip']
objects=git('rev-list','--objects',plan['base']+'..'+rewrite['new_tip'])
scan=subprocess.run(GIT+['cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize) %(rest)'],cwd=ROOT,input=objects,capture_output=True,check=True).stdout
(OUT/'candidate-object-sizes.txt').write_bytes(scan)
large=[];largest=(0,'')
for line in scan.decode().splitlines():
 oid,kind,size,*path=line.split(' ',3)
 if kind!='blob':continue
 n=int(size)
 if n>largest[0]:largest=(n,path[0] if path else oid)
 if n>50*1024**2:large.append(line)
assert not large,large
assert git('diff','--binary')==(OUT/'working-tree-before.patch').read_bytes()
assert git('ls-files','--stage')==(OUT/'index-before.txt').read_bytes()
(OUT/'PER-COMMIT-VERIFICATION.json').write_text(json.dumps(checks,indent=2)+'\n')
result=dict(status='VERIFIED',commits=len(checks),rewritten=rewrite['rewritten'],native_and_test_bytes_unchanged_at_every_commit=True,all_other_paths_and_modes_unchanged=True,authors_committers_dates_messages_preserved=True,parent_mapping_preserved=True,outgoing_blobs_over_50_mib=0,largest_outgoing_blob=dict(bytes=largest[0],path=largest[1]),working_tree_and_index_unchanged=True)
(OUT/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
