from pathlib import Path
import difflib,hashlib,json,shutil,subprocess,tempfile
p=Path(__file__).resolve().parent
previous=p.parent/'css-animation-contextual-attr-proposal-v1/checkpoint-1'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(previous/'FILES.json')=='9f1ac4519d3ea610f711453f8ba7d9146eb26d4b835b9dfe37de21f309c985be'
rows=[];full=[];delta=[]
for b in sorted((p/'base').rglob('*')):
    if not b.is_file():continue
    rel=b.relative_to(p/'base');c=p/'candidate'/rel;old=previous/'candidate'/rel
    assert b.read_bytes()==(previous/'base'/rel).read_bytes()
    rows.append({'path':str(rel),'base_sha256':sha(b),'checkpoint1_sha256':sha(old),'candidate_sha256':sha(c),'changed':b.read_bytes()!=c.read_bytes()})
    for before,out in [(b,full),(old,delta)]:
        if before.read_bytes()!=c.read_bytes():out.extend(difflib.unified_diff(before.read_text().splitlines(True),c.read_text().splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel)))
(p/'EXPERIMENT.patch').write_text(''.join(full));(p/'V2-DELTA.patch').write_text(''.join(delta))
(p/'POSTIMAGES.json').write_text(json.dumps(rows,indent=2)+'\n')
results=[]
with tempfile.TemporaryDirectory(prefix='css-contextual-v2-patch-',dir='/private/tmp') as d:
    scratch=Path(d);shutil.copytree(p/'base',scratch/'tree')
    for i,reverse in enumerate([False,True]):
        command=['/usr/bin/patch','--batch','-p1','-i',str(p/'EXPERIMENT.patch')]
        if reverse:command.insert(1,'-R')
        r=subprocess.run(command,cwd=scratch/'tree',stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
        (p/f'patch-{i}.log').write_bytes(r.stdout);assert r.returncode==0,r.stdout.decode()
        expected=p/('base' if reverse else 'candidate')
        for row in rows:
            assert (scratch/'tree'/row['path']).read_bytes()==(expected/row['path']).read_bytes()
        results.append({'command':command,'exit':r.returncode,'exact_bodies':len(rows)})
assert not scratch.exists()
(p/'PATCH-CHECK.json').write_text(json.dumps({'results':results,'scratch_removed':True,'native_compile':False,'full_delta_sha256':sha(p/'EXPERIMENT.patch'),'checkpoint_delta_sha256':sha(p/'V2-DELTA.patch')},indent=2)+'\n')
print(json.dumps({'exact_bodies':len(rows),'forward_reverse':True,'scratch_removed':True}))
