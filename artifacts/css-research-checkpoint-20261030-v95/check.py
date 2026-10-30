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
prior = ROOT / 'artifacts/css-research-checkpoint-20261030-v94'
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
    for name, record in json.loads((ROOT / path).read_bytes()).items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        full = str((Path(path).parent / name))
        assert selected[full]['sha256'] == record['sha256']
old = (ROOT / 'artifacts/css-research-checkpoint-20261030-v93/commit.py').read_text()
new = (HERE / 'commit.py').read_text()
marker = "    controls = {name: (RUNTIME / name).read_bytes()"
assert old[old.index(marker):].replace("prefix='css-research-v93-'", "prefix='css-research-v95-'").replace('No bug - Record CSS scheduling trace and publication proof preparation.', 'No bug - Record font demand projection and metric research.') == new[new.index(marker):]
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
with tempfile.TemporaryDirectory(prefix='css-research-v95-check-') as temporary:
    scratch = Path(temporary)
    for label, target, field, value in [
        ('unsigned', 'receipt', 'signature_verified', False),
        ('wrong_head', 'receipt', 'head', '0' * 40),
        ('accepted_increment', 'receipt', 'accepted_fix_increment', 1),
        ('incomplete', 'current', 'full_current_state_verified', False),
        ('tracked_dirt', 'current', 'tracked_modified_paths', ['servo/example.rs']),
        ('staged_dirt', 'current', 'staged_paths', ['artifacts/example']),
    ]:
        r, c = copy.deepcopy(receipt), copy.deepcopy(current)
        (r if target == 'receipt' else c)[field] = value
        rb = json.dumps(r).encode()
        c['prior_receipt_sha256'] = sha(rb)
        cb = json.dumps(c).encode()
        (scratch / 'receipt.json').write_bytes(rb)
        (scratch / 'current.json').write_bytes(cb)
        test_bindings = copy.deepcopy(bindings)
        test_bindings.update(prior_receipt='receipt.json', prior_receipt_sha256=sha(rb), current_capture='current.json', current_capture_sha256=sha(cb))
        m.ROOT, m.BINDINGS = scratch, test_bindings
        try:
            m.saved_admission()
        except AssertionError:
            pass
        else:
            raise AssertionError('Accepted mutation: ' + label)
    m.ROOT, m.BINDINGS = ROOT, bindings
assert not scratch.exists()
print(json.dumps({'selected':len(selected), 'bytes':sum(row['bytes'] for row in selected.values()), 'closures':len(bindings['completed_packages']), 'binding_negatives':6, 'disabled_execution_rejected':True, 'exact_v93_publication_tail':True, 'scratch_removed':True}))
