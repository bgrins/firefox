import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

for name, row in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / name) == row['sha256'] and (ROOT / name).stat().st_size == row['bytes']
policy = read(HERE / 'PREPARATION.json')
assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
for key in ('current_binding', 'capture_owner', 'refresh_lineage', 'epoch_sha256', 'controls', 'current_owner_restoration'):
    assert policy[key] is None
assert policy['additional_source_paths'] == []
roles = read(HERE / 'SOURCE-ROLES.json')
assert set(roles) == {'servo/ports/geckolib/glue.rs'}
for row in roles.values():
    for kind in ('base', 'candidate'):
        assert sha(ROOT / row[kind + '_capture']) == row[kind + '_sha256']
lanes = read(HERE / 'WPT-LANES.json')
assert sum(x['expected_subtest_count'] for x in lanes.values()) == 61
assert sum(x['expected_page_count'] for x in lanes.values()) == 5
original = read(HERE / 'ORIGINAL61.json')
for name, expected in original['input_runtime_manifests'].items():
    manifest = ROOT / name
    assert sha(manifest) == expected
    data = read(manifest)
    for path, row in data.get('files', data).items():
        assert sha(manifest.parent / path) == (row if isinstance(row, str) else row['sha256'])
controls_dir = ROOT / 'artifacts/css-explicit-attribute-taint-controls-archived-original-runtime-v1'
helper = load('controls_assessor', 'artifacts/css-explicit-attribute-taint-controls-archived-original-v1/run.py')
events = [json.loads(line) for line in (controls_dir / 'raw.jsonl').read_text().splitlines()]
a = helper.assess(events, lanes['controls']['expected_subtests'], read(controls_dir / 'RESULT.json')['exit'])
assert a == read(controls_dir / 'ASSESSMENT.json') and a['counts'] == {'PASS': 47}
fix = ROOT / policy['source_binding']['directory']
isolated = read(fix / 'ISOLATED-BASELINE.json')
assert original['rows'] == isolated['subtests'] + a['subtests']
assert original['endings'] == isolated['endings'] + a['endings']
assert original['counts'] == {'PASS': 54, 'FAIL': 7}
expected = {(page, name) for lane in lanes.values() for page, names in lane['expected_subtests'].items() for name in names}
assert expected == {(row['test'], row['subtest']) for row in original['rows']} and len(expected) == 61
wpt = load('stage', 'artifacts/css-keyframe-font-unit-candidate-browser-v1/wpt.py')
scratch = Path(tempfile.mkdtemp(prefix='root-self61-preparation-', dir='/private/tmp'))
try:
    for name, settings in lanes.items():
        out = scratch / name
        out.mkdir()
        config, capture = wpt.prepare_inputs(ROOT, out, settings, 'candidate')
        assert config.is_file() and capture is None
        for url, row in settings['resources'].items():
            assert sha(out / 'tests' / url.lstrip('/')) == row['sha256']
finally:
    shutil.rmtree(scratch)
assert not scratch.exists()
print(json.dumps({'preparation_only': True, 'current_admission_pending': True, 'source_roles': 1, 'canonical_glue_claim': True, 'additional_roles': 0, 'original_PASS': 54, 'original_FAIL': 7, 'callbacks': 61, 'endings': 5, 'staged_lanes': 2, 'scratch_removed': True, 'native_or_browser_execution': False}))
