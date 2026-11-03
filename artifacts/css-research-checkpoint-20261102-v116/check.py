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
    for name, record in manifest.get('files', manifest).items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        full = str((Path(path).parent / name))
        assert selected[full]['sha256'] == (record['sha256'] if isinstance(record, dict) else record)
old = (ROOT / 'artifacts/css-research-checkpoint-20261102-v103/commit.py').read_text()
new = (HERE / 'commit.py').read_text()
marker = "    controls = {name: (RUNTIME / name).read_bytes()"
assert old[old.index(marker):].replace('v103','v116').replace('V103','V116').replace('No bug - Record signed hyphenation publication and close validation evidence.','No bug - Record signed declaration capacity publication and diagnostic preparation.') == new[new.index(marker):]
if bindings['pending_current_admission']:
    assert bindings['current_capture_sha256'] is None
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
    print(json.dumps({'preparation_only':True,'pending_admission_rejected':True,'disabled_run_rejected':True,'selected':len(selected),'bytes':sum(row['bytes'] for row in selected.values()),'closures':len(bindings['completed_packages']),'exact_v103_tail':True}))
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
with tempfile.TemporaryDirectory(prefix='css-research-v116-check-') as temporary:
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
print(json.dumps({'selected':len(selected), 'bytes':sum(row['bytes'] for row in selected.values()), 'closures':len(bindings['completed_packages']), 'binding_negatives':11, 'disabled_execution_rejected':True, 'exact_v103_publication_tail':True, 'scratch_removed':True}))
