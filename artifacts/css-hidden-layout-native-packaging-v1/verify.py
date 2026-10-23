import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
import argparse
import hashlib
import json
import stat
import subprocess
import tempfile
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--manifest-sha',required=True)
a=p.parse_args()
here=Path(__file__).resolve().parent
root=here.parents[1]
sha=lambda data:hashlib.sha256(data).hexdigest()
blob=lambda data:hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
read=lambda path:json.loads(path.read_text())
def need(ok,why):
    if not ok:
        raise RuntimeError(why)
need(sha((here/'FILES.json').read_bytes())==a.manifest_sha,'Wrong package manifest')
manifest=read(here/'FILES.json')
actual=set()
for file in here.rglob('*'):
    mode=file.lstat().st_mode
    if stat.S_ISDIR(mode):
        continue
    need(stat.S_ISREG(mode),'Nonregular package entry')
    actual.add(file.relative_to(here).as_posix())
need(actual==set(manifest)|{'FILES.json','FREEZE.json'},'Package roster mismatch')
for name,pin in manifest.items():
    need(sha((here/name).read_bytes())==pin,'Package input changed')
bindings=read(here/'BINDINGS.json')
need(sha((root/'artifacts/css-hidden-layout-compact-runtime-v3/FILES.json').read_bytes())==bindings['runtime_manifest'],'Runtime manifest changed')
need(sha((root/'artifacts/css-hidden-layout-landing-plan-v1/FILES.json').read_bytes())==bindings['landing_plan_manifest'],'Landing plan changed')
all_paths=[]
for kind,entries in bindings['recipes'].items():
    recipe=read(here/(kind+'-native-draft.json'))
    need(recipe['draft_only'] and recipe['expected_head']=='PENDING_VERIFIED_PRECEDING_EVIDENCE_COMMIT','Recipe accidentally activated')
    patch=here/(kind+'.patch')
    need(sha(patch.read_bytes())==recipe['patch_sha256'],'Patch changed')
    need(recipe['files']==[x['path'] for x in entries],'Recipe roster mismatch')
    with tempfile.TemporaryDirectory(prefix='hidden-native-review-') as temp:
        work=Path(temp)
        before={}
        after={}
        for entry in entries:
            name=entry['path']
            need(name not in all_paths,'Packages overlap')
            all_paths.append(name)
            data=(root/entry['final_source']).read_bytes()
            need(sha(data)==entry['after_sha256']==recipe['expected_final_sha256'][name] and blob(data)==entry['after_blob']==recipe['expected_final_blobs'][name],'Final source identity mismatch')
            after[name]=data
            before[name]=None if entry['before_source'] is None else (root/entry['before_source']).read_bytes()
            need(recipe['expected_before_blobs'][name]==entry['before_blob'],'Before recipe mismatch')
            if before[name] is not None:
                need(sha(before[name])==entry['before_sha256'] and blob(before[name])==entry['before_blob'],'Before source identity mismatch')
            target=work/name
            target.parent.mkdir(parents=True,exist_ok=True)
            if before[name] is not None:
                target.write_bytes(before[name])
        forward=subprocess.run(['/usr/bin/patch','-p1','--batch','--fuzz=0','-i',str(patch)],cwd=work,capture_output=True,text=True)
        need(forward.returncode==0 and all((work/name).read_bytes()==data for name,data in after.items()),'Private apply mismatch')
        reverse=subprocess.run(['/usr/bin/patch','-R','-E','-p1','--batch','--fuzz=0','-i',str(patch)],cwd=work,capture_output=True,text=True)
        need(reverse.returncode==0 and all(not (work/name).exists() if data is None else (work/name).read_bytes()==data for name,data in before.items()),'Private reverse mismatch')
print('PASS: principal four-file and absolute three-file patches, exact tested blobs, disjoint paths, private apply/reverse; recipes remain unapproved drafts')
