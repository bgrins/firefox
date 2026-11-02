import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda data: hashlib.sha256(data).hexdigest()
spec = importlib.util.spec_from_file_location('checkpoint', HERE / 'commit.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert m.EXECUTION_ENABLED is False
bindings = m.BINDINGS
for path, digest in bindings['references'].items():
    assert sha((ROOT / path).read_bytes()) == digest
selection_body = (HERE / 'SELECTION.json').read_bytes()
assert sha(selection_body) == bindings['selection_sha256']
selected = json.loads(selection_body)
assert len(selected) == bindings['selected_paths_before_self']
previous = set()
for dirname in ('css-research-checkpoint-20261030-v99','css-research-checkpoint-20261030-v100','css-research-checkpoint-20261030-v101','css-research-checkpoint-20261102-v102','css-research-checkpoint-20261102-v103','css-research-checkpoint-20261102-v104','css-research-checkpoint-20261102-v105','css-research-checkpoint-20261102-v106'):
    prior = ROOT / 'artifacts' / dirname
    previous.update(json.loads((prior / 'SELECTION.json').read_bytes()))
    previous.update(str((prior / name).relative_to(ROOT)) for name in json.loads((prior / 'FILES.json').read_bytes()))
    previous.add(str((prior / 'FILES.json').relative_to(ROOT)))
assert not previous.intersection(selected)
for path, record in selected.items():
    assert path.startswith('artifacts/') and '..' not in Path(path).parts
    source = ROOT / path
    assert source.is_file() and not source.is_symlink()
    assert source.stat().st_size == record['bytes'] and sha(source.read_bytes()) == record['sha256']
for path, digest in bindings['completed_packages'].items():
    assert sha((ROOT / path).read_bytes()) == digest == selected[path]['sha256']
    manifest = json.loads((ROOT / path).read_bytes())
    for name, record in manifest.get('files', manifest).items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        full = str((Path(path).parent / name))
        assert selected[full]['sha256'] == (record['sha256'] if isinstance(record, dict) else record)
old = (ROOT / 'artifacts/css-research-checkpoint-20261102-v106/commit.py').read_text()
new = (HERE / 'commit.py').read_text()
marker = "    controls = {name: (RUNTIME / name).read_bytes()"
assert old[old.index(marker):].replace('v106', 'v107').replace('V106', 'V107').replace('Record selected-reference producer validation.', 'Record selected-reference paired browser observations.') == new[new.index(marker):]

if bindings['pending_current_admission']:
    if bindings.get('completed_pair_runtime_frozen'):
        assert 'artifacts/css-font-metric-selected-reference-pair-runtime-1/FILES.json' in bindings['completed_packages']
    else:
        assert 'artifacts/css-font-metric-selected-reference-pair-root-run-v1.log' not in selected
        assert not any(path.startswith('artifacts/css-font-metric-selected-reference-pair-runtime-1/') for path in selected)
    assert bindings['current_capture_sha256'] is None
    if bindings['refresh_binding']:
        receipt = json.loads((ROOT / bindings['prior_receipt']).read_bytes())
        refreshed = m.validate_refresh(receipt)
        frozen = json.loads((ROOT / 'artifacts/css-font-metric-selected-reference-pair-runtime-1/POST.json').read_bytes())
        frozen['index']['raw_index'] = refreshed['index']['raw_index']
        assert refreshed == frozen
        assert bindings['controls']['CURRENT-EPOCH.json'] == bindings['epoch_sha256']
    else:
        assert bindings['epoch_sha256'] is None and bindings['controls'] is None
    try:
        m.saved_admission()
    except AssertionError:
        pass
    else:
        raise AssertionError('Pending current admission accepted')
else:
    assert m.saved_admission()['index']['head'] == bindings['head']

original_git = m.git
m.git = lambda *a, **k: (_ for _ in ()).throw(AssertionError('Unexpected live Git invocation'))
saved_argv = sys.argv
try:
    sys.argv = [str(HERE / 'commit.py'), '--run']
    try:
        m.main()
    except AssertionError as exc:
        assert str(exc) == 'Draft signing execution is disabled'
    else:
        raise AssertionError('Disabled execution accepted')
finally:
    sys.argv = saved_argv
    m.git = original_git
if bindings['pending_current_admission']:
    print(json.dumps({'selected':len(selected), 'bytes':sum(row['bytes'] for row in selected.values()), 'closures':len(bindings['completed_packages']), 'pending_admission_rejected':True, 'disabled_execution_rejected':True, 'exact_v106_signing_tail':True}))
    raise SystemExit(0)
current = json.loads((ROOT / bindings['current_capture']).read_bytes())
receipt = json.loads((ROOT / bindings['prior_receipt']).read_bytes())
directory = ROOT / bindings['refresh_binding']['directory']
refresh = json.loads((directory / 'RESULT.json').read_bytes())
negatives = 0
with tempfile.TemporaryDirectory(prefix='css-research-v107-check-') as temporary:
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
print(json.dumps({'selected':len(selected),'bytes':sum(x['bytes'] for x in selected.values()),'closures':len(bindings['completed_packages']),'binding_negatives':negatives,'disabled_execution_rejected':True,'exact_v106_signing_tail':True,'scratch_removed':True}))
