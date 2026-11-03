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
prior = ROOT / 'artifacts/css-research-checkpoint-20261102-v114'
previous = set(json.loads((prior / 'SELECTION.json').read_bytes()))
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
    for name, record in m.manifest_items(manifest):
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        full = str((Path(path).parent / name))
        assert selected[full]['sha256'] == (record['sha256'] if isinstance(record, dict) else record)
nested_path = str((HERE / 'NESTED-DEPENDENCIES.json').relative_to(ROOT))
assert sha((ROOT / nested_path).read_bytes()) == bindings['references'][nested_path]
nested = json.loads((ROOT / nested_path).read_bytes())
assert nested['repository'] == 'artifacts/css-spec-lean'
assert nested['head'] == '162b20fb7c53a0ab89b20875a965baee98fb66bb'
assert nested['tracked_status'] == '' and nested['before_after_head_and_tracked_status_equal']
assert nested['read_only_git'] and not nested['source_or_nested_writes']
assert len(nested['files']) == 25
omitted = json.loads((ROOT / 'artifacts/css-research-v123-staging-mismatch-v1/RESULT.json').read_bytes())['exact_missing']
assert set(nested['files']) == set(omitted) and not set(omitted).intersection(selected)
for path, record in nested['files'].items():
    assert bindings['references'][path] == record['sha256'] == sha((ROOT / path).read_bytes())
    assert (ROOT / path).stat().st_size == record['bytes']
    assert str(Path(nested['repository']) / record['nested_path']) == path
    assert len(record['blob']) == 40 and set(record['blob']) <= set('0123456789abcdef')
    assert not any(Path(path).is_relative_to(Path(item).parent) for item in bindings['completed_packages'])
old = (ROOT / 'artifacts/css-research-checkpoint-20261103-v126/commit.py').read_text()
new = (HERE / 'commit.py').read_text()
marker = "    controls = {name: (RUNTIME / name).read_bytes()"
assert old[old.index(marker):].replace('v126','v127').replace('V126','V127').replace('No bug - Record CSS substitution and animation verification research.', 'No bug - Record font animation and cancellation repair research.') == new[new.index(marker):]
assert (HERE / 'capture_current.py').read_bytes() == (ROOT / 'artifacts/css-research-checkpoint-20261103-v126/capture_current.py').read_bytes()
assert list(m.manifest_items({'files':[{'path':'proof','sha256':'x'}]})) == [('proof',{'path':'proof','sha256':'x'})]
try:
    m.manifest_items({'files':[{'path':'proof','sha256':'x'},{'path':'proof','sha256':'y'}]})
except AssertionError:
    pass
else:
    raise AssertionError('Duplicate manifest path accepted')
self_start = new.index("    self_manifest = json.loads((HERE / 'FILES.json').read_bytes())")
self_end = new.index("    for path in extras:", self_start)
import textwrap
self_block = textwrap.dedent(new[self_start:self_end])
with tempfile.TemporaryDirectory(prefix='css-research-v127-self-check-', dir='/private/tmp') as temporary:
    own = Path(temporary)
    entries = {}
    for name in ('commit.py', 'CHECK-FINAL.log', 'SELECTION-ADDITION.json'):
        (own/name).write_text(name)
        entries[name] = {'sha256':sha((own/name).read_bytes())}
    (own/'FILES.json').write_text(json.dumps(entries))
    scope = {'HERE':own, 'json':json, 'Path':Path, 'sha':sha, 'manifest_items':m.manifest_items}
    exec(self_block, scope)
    assert {x.name for x in scope['extras']} == set(entries) | {'FILES.json'}
    (own/'omitted.log').write_text('omitted')
    try: exec(self_block, scope)
    except AssertionError: pass
    else: raise AssertionError('Unlisted owner payload accepted')
    (own/'omitted.log').unlink()
    (own/'CHECK-FINAL.log').write_text('changed')
    try: exec(self_block, scope)
    except AssertionError: pass
    else: raise AssertionError('Changed owner payload accepted')
assert not own.exists()
conditions = json.loads((HERE / 'PRECONDITIONS.json').read_bytes())
pending_new_refresh = bindings['pending_current_admission'] and conditions['pending_new_raw_refresh']
future_bindings = bindings
if pending_new_refresh:
    assert bindings['refresh_binding'] is None and bindings['epoch_sha256'] is None
    assert bindings['current_capture_sha256'] is None and bindings['controls'] == {}
    assert bindings['refresh_prefix'] == conditions['known_completed_refresh_prefix']
    bindings = copy.deepcopy(bindings)
    bindings['refresh_binding'] = bindings['refresh_prefix'].pop()
    bindings['epoch_sha256'] = conditions['last_completed_epoch_sha256']
    m.BINDINGS, m.EPOCH = bindings, bindings['epoch_sha256']
receipt = json.loads((ROOT / bindings['prior_receipt']).read_bytes())
original_refresh = m.validate_refresh
refreshed = original_refresh(receipt)
with tempfile.TemporaryDirectory(prefix='css-research-v127-refresh-check-') as temporary:
    scratch = Path(temporary)
    source = ROOT / bindings['refresh_binding']['directory']
    for name in ['RESULT.json', 'PRE-CURRENT-EPOCH.json', 'EPOCH.json', 'PRE.json', 'POST.json']:
        (scratch / name).write_bytes((source / name).read_bytes())
    test_bindings = copy.deepcopy(bindings)
    test_bindings['refresh_binding']['directory'] = str(scratch)
    m.BINDINGS = test_bindings
    assert original_refresh(receipt) == refreshed
    result = json.loads((source / 'RESULT.json').read_bytes())
    for field, value in [('updated_only', 'other'), ('head', '0' * 40),
                         ('old_epoch_sha256', '0' * 64),
                         ('restoration_independently_verified', False)]:
        changed = copy.deepcopy(result)
        changed[field] = value
        body = json.dumps(changed).encode()
        (scratch / 'RESULT.json').write_bytes(body)
        test_bindings['refresh_binding']['result_sha256'] = sha(body)
        try:
            original_refresh(receipt)
        except AssertionError:
            pass
        else:
            raise AssertionError('Accepted refresh mutation: ' + field)
    m.BINDINGS = bindings
assert not scratch.exists()
if pending_new_refresh:
    m.BINDINGS, m.EPOCH, bindings = future_bindings, None, future_bindings
    try:
        m.saved_admission()
    except AssertionError:
        pass
    else:
        raise AssertionError('Missing post-trace current admitted')
    sys.argv = [str(HERE / 'commit.py'), '--run']
    try:
        m.main()
    except AssertionError as exc:
        assert str(exc) == 'Draft signing execution is disabled'
    else:
        raise AssertionError('Disabled preparation executed')
    assert not (HERE / 'result.json').exists()
    print(json.dumps({'preparation_only':True,'pending_trace_terminal_refresh_and_current':True,
                      'known_completed_refresh_prefix_verified':True,'disabled_run_rejected':True,
                      'selected':len(selected),'bytes':sum(row['bytes'] for row in selected.values()),
                      'closures':len(bindings['completed_packages']),'exact_v126_tail':True,
                      'refresh_copy_positive':True,'refresh_negatives':4,'scratch_removed':True}))
    raise SystemExit(0)
if bindings['pending_current_admission']:
    assert bindings['current_capture_sha256'] is None and bindings['controls'] == {}
    conditions = json.loads((HERE / 'PRECONDITIONS.json').read_bytes())
    assert conditions['pending_new_raw_refresh'] is False
    assert bindings['epoch_sha256'] == conditions['current_epoch_sha256']
    assert bindings['refresh_binding'] == conditions['actual_new_refresh']
    receipt = json.loads((ROOT / bindings['prior_receipt']).read_bytes())
    assert refreshed['index']['head'] == bindings['head']
    try:
        m.saved_admission()
    except AssertionError:
        pass
    else:
        raise AssertionError('Pending admission accepted')
    sys.argv = [str(HERE / 'commit.py'), '--run']
    try:
        m.main()
    except AssertionError as exc:
        assert str(exc) == 'Draft signing execution is disabled'
    else:
        raise AssertionError('Disabled draft execution accepted')
    print(json.dumps({'preparation_only':True,'pending_current_admission_rejected':True,'actual_completed_refresh_verified':True,'disabled_run_rejected':True,'selected':len(selected),'bytes':sum(row['bytes'] for row in selected.values()),'closures':len(bindings['completed_packages']),'exact_v126_tail':True,'refresh_copy_positive':True,'refresh_negatives':4,'scratch_removed':True}))
    raise SystemExit(0)
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
current = json.loads((ROOT / bindings['current_capture']).read_bytes())
receipt = json.loads((ROOT / bindings['prior_receipt']).read_bytes())
research = json.loads((ROOT / bindings['prior_research_receipt']).read_bytes())
m.validate_refresh = lambda receipt: refreshed
with tempfile.TemporaryDirectory(prefix='css-research-v127-check-') as temporary:
    scratch = Path(temporary)
    for label, target, field, value in [
        ('unsigned_native', 'receipt', 'signature_verified', False),
        ('wrong_commit', 'receipt', 'commit', '0' * 40),
        ('wrong_stage', 'receipt', 'stage', 'other'),
        ('wrong_files', 'receipt', 'files', ['dom/base/nsLineBreaker.cpp']),
        ('wrong_parent', 'receipt', 'parent', '0' * 40),
        ('accepted', 'receipt', 'accepted', True),
        ('app_rebuilt', 'receipt', 'app_rebuilt', True),
        ('unsigned_research_parent', 'research', 'signature_verified', False),
        ('incomplete', 'current', 'full_current_state_verified', False),
        ('tracked_dirt', 'current', 'tracked_modified_paths', ['servo/example.rs']),
        ('staged_dirt', 'current', 'staged_paths', ['artifacts/example']),
    ]:
        r, c, research_copy = copy.deepcopy(receipt), copy.deepcopy(current), copy.deepcopy(research)
        {'receipt':r, 'current':c, 'research':research_copy}[target][field] = value
        research_body = json.dumps(research_copy).encode()
        (scratch / 'research.json').write_bytes(research_body)
        rb = json.dumps(r).encode()
        c['prior_receipt_sha256'] = sha(rb)
        cb = json.dumps(c).encode()
        (scratch / 'receipt.json').write_bytes(rb)
        (scratch / 'current.json').write_bytes(cb)
        test_bindings = copy.deepcopy(bindings)
        test_bindings.update(prior_receipt='receipt.json', prior_receipt_sha256=sha(rb), current_capture='current.json', current_capture_sha256=sha(cb), prior_research_receipt='research.json', prior_research_receipt_sha256=sha(research_body))
        m.ROOT, m.BINDINGS = scratch, test_bindings
        try:
            m.saved_admission()
        except AssertionError:
            pass
        else:
            raise AssertionError('Accepted mutation: ' + label)
    m.ROOT, m.BINDINGS = ROOT, bindings
assert not scratch.exists()
m.validate_refresh = original_refresh
print(json.dumps({'refresh_copy_positive':True, 'refresh_negatives':4, 'admission_negatives_scope':'native/current schema isolated from separately checked refresh join', 'selected':len(selected), 'bytes':sum(row['bytes'] for row in selected.values()), 'closures':len(bindings['completed_packages']), 'binding_negatives':11, 'disabled_execution_rejected':True, 'exact_v126_publication_tail':True, 'scratch_removed':True}))
