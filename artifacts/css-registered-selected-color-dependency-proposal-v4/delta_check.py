from pathlib import Path
import difflib
import hashlib
import json
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.with_name('css-registered-selected-color-dependency-proposal-v3')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
for path, row in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
    assert sha(ROOT / path) == row['sha256']
for name, row in json.loads((OLD / 'FILES.json').read_bytes()).items():
    assert sha(OLD / name) == row['sha256']
roles = json.loads((HERE / 'SOURCE-ROLES.json').read_bytes())
delta = []
for name, row in roles.items():
    before, after = OLD / 'candidate' / name, HERE / 'candidate' / name
    assert sha(before) == row['v3_candidate_sha256'] and sha(after) == row['candidate_sha256']
    if not name.endswith('/custom_properties.rs'): assert before.read_bytes() == after.read_bytes()
    delta.extend(difflib.unified_diff(before.read_text().splitlines(True), after.read_text().splitlines(True), fromfile='a/'+name, tofile='b/'+name))
assert ''.join(delta) == (HERE/'V4-DELTA.patch').read_text()
name = 'candidate/servo/components/style/custom_properties.rs'
a,b = (OLD/name).read_text(),(HERE/name).read_text()
start = 'pub fn substitute_references_if_needed_and_apply('
end = '    let url_data = &value.url_data;'
assert a[a.index(start):a.index(end,a.index(start))] == b[b.index(start):b.index(end,b.index(start))]
body = '    let Ok(substitution) = substitution else {'
tail = '\nenum PreparedCustomKind'
assert a[a.index(body,a.index('fn apply_substituted_value')):a.index(tail)] == b[b.index(body,b.index('fn apply_substituted_value')):b.index(tail)]
for token in ('.clone()', '.into_owned()', 'Arc::clone('): assert a.count(token) == b.count(token)
print(json.dumps({'predecessor_authenticated':True,'postimages':3,'changed_postimages':1,'exact_delta':True,'fastpath_and_application_body_unchanged':True,'no_added_clone_or_into_owned':True,'native_compile':False}))
