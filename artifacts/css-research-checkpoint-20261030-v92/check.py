import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('checkpoint',HERE/'commit.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.EXECUTION_ENABLED is False
bindings=m.BINDINGS
for name,pin in bindings['references'].items():assert sha((ROOT/name).read_bytes())==pin,name
selection_body=(HERE/'SELECTION.json').read_bytes()
assert sha(selection_body)==bindings['selection_sha256']
selected=json.loads(selection_body)
assert len(selected)==bindings['selected_paths_before_self']
prior=ROOT/'artifacts/css-research-checkpoint-20261030-v91'
previous=set(json.loads((prior/'SELECTION.json').read_bytes()))
previous.update(str((prior/name).relative_to(ROOT)) for name in json.loads((prior/'FILES.json').read_bytes()))
previous.add(str((prior/'FILES.json').relative_to(ROOT)))
assert not previous.intersection(selected)
for name,row in selected.items():
    assert name.startswith('artifacts/') and '..' not in Path(name).parts
    path=ROOT/name
    assert path.is_file() and not path.is_symlink()
    assert path.stat().st_size==row['bytes'] and sha(path.read_bytes())==row['sha256'],name
for name,pin in bindings['completed_packages'].items():
    assert sha((ROOT/name).read_bytes())==pin==selected[name]['sha256']
    for path,row in json.loads((ROOT/name).read_bytes()).items():
        assert selected[str(Path(name).parent/path)]['sha256']==row['sha256']
old=(prior/'commit.py').read_text();new=(HERE/'commit.py').read_text()
marker="    controls = {name: (RUNTIME / name).read_bytes()"
assert old[old.index(marker):].replace("prefix='css-research-v91-'","prefix='css-research-v92-'").replace('No bug - Record focused CSS publication validation preparation.','No bug - Record paired CSS publication validation research.')==new[new.index(marker):]
patch=''
for name in ['commit.py','capture_current.py']:
    patch+=''.join(difflib.unified_diff((prior/name).read_text().splitlines(True),(HERE/name).read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
assert patch==(HERE/'RUN-DELTA.patch').read_text()
saved_argv,original_git=sys.argv,m.git
m.git=lambda *a,**k:(_ for _ in ()).throw(AssertionError('MOCK FIRST GIT'))
try:
    sys.argv=[str(HERE/'commit.py'),'--run']
    try:m.main()
    except AssertionError as e:assert str(e)=='Draft signing execution is disabled'
    else:raise AssertionError('disabled signing accepted')
    if not bindings['pending_current_admission']:
        assert m.saved_admission()['index']['head']==bindings['head']
        sys.argv=[str(HERE/'commit.py'),'--check']
        try:m.main()
        except AssertionError as e:assert str(e)=='MOCK FIRST GIT'
        else:raise AssertionError('first Git boundary missing')
finally:sys.argv,m.git=saved_argv,original_git
negatives=0
if not bindings['pending_current_admission']:
    receipt=json.loads((ROOT/bindings['prior_receipt']).read_bytes())
    current=json.loads((ROOT/bindings['current_capture']).read_bytes())
    directory=ROOT/bindings['refresh_binding']['directory']
    refresh=json.loads((directory/'RESULT.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='css-research-v92-check-') as temporary:
        scratch=Path(temporary);(scratch/'refresh').mkdir()
        for name in ['PRE-CURRENT-EPOCH.json','EPOCH.json','PRE.json','POST.json']:
            (scratch/'refresh'/name).write_bytes((directory/name).read_bytes())
        for label,target,field,value in [('unsigned','receipt','signature_verified',False),('wrong_head','receipt','head','0'*40),('fix_increment','receipt','accepted_fix_increment',1),('incomplete','current','full_current_state_verified',False),('tracked_dirt','current','tracked_modified_paths',['servo/example.rs']),('staged_dirt','current','staged_paths',['artifacts/example']),('refresh_field','refresh','updated_only','semantic_index'),('refresh_acceptance','refresh','native_fix_acceptance',True)]:
            r,c,f=copy.deepcopy(receipt),copy.deepcopy(current),copy.deepcopy(refresh)
            {'receipt':r,'current':c,'refresh':f}[target][field]=value
            rb=json.dumps(r).encode();c['prior_receipt_sha256']=sha(rb)
            f['signed_commit_receipt']={'path':'receipt.json','sha256':sha(rb)}
            cb,fb=json.dumps(c).encode(),json.dumps(f).encode()
            (scratch/'receipt.json').write_bytes(rb);(scratch/'current.json').write_bytes(cb);(scratch/'refresh/RESULT.json').write_bytes(fb)
            b=copy.deepcopy(bindings);b.update(prior_receipt='receipt.json',prior_receipt_sha256=sha(rb),current_capture='current.json',current_capture_sha256=sha(cb),refresh_binding={'directory':'refresh','result_sha256':sha(fb)})
            m.ROOT,m.BINDINGS=scratch,b
            try:m.saved_admission()
            except AssertionError:negatives+=1
            else:raise AssertionError('accepted '+label)
        m.ROOT,m.BINDINGS=ROOT,bindings
    assert not scratch.exists()
print(json.dumps({'selected':len(selected),'bytes':sum(x['bytes'] for x in selected.values()),'closures':len(bindings['completed_packages']),'pending_current_admission':bindings['pending_current_admission'],'binding_negatives':negatives,'disabled_execution_rejected':True,'exact_v91_signing_tail':True,'live_Git_executed':False}))
