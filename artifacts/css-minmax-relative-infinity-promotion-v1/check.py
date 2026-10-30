import ast
import difflib
import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path:json.loads(path.read_bytes())
sha = lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
policy = read(HERE / 'POLICY.json')
assert policy['install_enabled'] is False and policy['accepted_fix_id'] is None and policy['acceptance'] is False
assert policy['activation_pending']
for key in ('head','epoch_sha256','role_sha256','owned_sha256','current_restoration','prepared_application_metadata'):
    assert policy[key] is None
assert all(value is None for value in policy['reference_checkpoint'].values())
assert len(policy['preserved_accepted_payload']) == 29
source = policy['source']
assert source['path'] == 'servo/components/style/values/generics/calc.rs'
assert policy['supersedes_source_pin'] == {'fix':150,'path':source['path'],'sha256':source['base_sha256']}
assert policy['accepted_preservation_markers']['accepted_pow_special_value']['files'][source['path']] == source['base_sha256']
assert set(policy['tests']) == {'testing/web-platform/tests/css/css-values/minmax-relative-infinity.html','testing/web-platform/tests/css/css-values/minmax-relative-infinity-ordering.html'}
assert not any(key.startswith('deleted_') for key in policy)
assert policy['held_provider_sha256'] == '2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774'
for kind in ('base','candidate'):
    assert sha(ROOT / source[kind + '_capture']) == source[kind + '_sha256']
for record in policy['tests'].values():
    assert sha(ROOT / record['capture']) == record['sha256']
verified, deferred = [], []
for name,pin in policy['references'].items():
    if not name.startswith('artifacts/'):
        deferred.append(name)
        continue
    assert sha(ROOT / name) == pin,name
    verified.append(name)
for directory,pin in policy['packages'].items():
    package = ROOT / directory
    assert sha(package / 'FILES.json') == pin
    for name,digest in read(package / 'FILES.json').items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert sha(package / name) == (digest['sha256'] if isinstance(digest,dict) else digest)
        if isinstance(digest,dict):assert (package / name).stat().st_size == digest['bytes']
manifest = read(ROOT / 'artifacts/css-minmax-log-native-payload-review-v1/MANIFEST.json')['sequence'][0]
patch = ''.join(difflib.unified_diff((ROOT/source['base_capture']).read_text().splitlines(True),
    (ROOT/source['candidate_capture']).read_text().splitlines(True), fromfile='a/'+source['path'], tofile='b/'+source['path']))
for name in manifest['native_paths'][1:]:
    patch += ''.join(difflib.unified_diff([], (ROOT/policy['tests'][name]['capture']).read_text().splitlines(True), fromfile='/dev/null', tofile='b/'+name))
assert patch == (ROOT / 'artifacts/css-minmax-log-native-payload-review-v1/01-minmax.patch').read_text()
for path in HERE.glob('*.py'):
    ast.parse(path.read_text(),filename=str(path))
print(json.dumps({'artifact_references_authenticated':len(verified),'mutable_or_live_reference_checks_deferred':deferred,
    'packages_authenticated':len(policy['packages']),'complete_exact_three_path_patch_reconstructed':True,
    'syntax_passed':True,'historical_browser_comparisons_replayed':False,
    'live_state_guard_or_mutation':False,'install_enabled':False},indent=2))
