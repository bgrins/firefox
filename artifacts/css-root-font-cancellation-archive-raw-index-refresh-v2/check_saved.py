import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from collections import Counter

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
parent = ROOT / 'artifacts/css-root-font-cancellation-archive-raw-index-refresh-v1'
assert (HERE / 'run.py').read_bytes() == (parent / 'run.py').read_bytes()
policy = read(HERE / 'POLICY.json')
assert policy['execution_enabled'] is False and not policy['pending_runtime_binding']
for name, pin in policy['references'].items():
    assert sha(ROOT / name) == pin, name
spec = importlib.util.spec_from_file_location('actual_bound_archive_refresh', HERE / 'run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
started = time.monotonic()
print('Starting one actual saved runtime/archive/restoration replay; no live main.', flush=True)
owner, report, pre, post, raw = module.saved(policy)
previous = ROOT / policy['refresh_parent']['directory']
assert sha(previous / 'RESULT.json') == policy['refresh_parent']['result_sha256']
assert sha(previous / 'EPOCH.json') == policy['controls']['CURRENT-EPOCH.json']
epoch = read(previous / 'EPOCH.json')
updated = module.derive(epoch, pre['snapshot'], post, raw)
projected = json.loads(json.dumps(updated))
projected['raw_index_observation']['current'] = raw['before']
assert projected == epoch
runtime = ROOT / policy['runtime']
assessment = read(runtime / 'candidate-wpt-cancellation/ASSESSMENT.json')
result = {
    'references': len(policy['references']), 'run_byte_identical_to_preparation': True,
    'actual_saved_runtime_replay': True, 'saved_elapsed_seconds': round(time.monotonic() - started, 3),
    'callbacks': len(assessment['rows']), 'counts': dict(Counter(row['status'] for row in assessment['rows'])),
    'endings': len(assessment['ends']), 'archive_receipts': policy['archive_receipts'],
    'runtime_manifest_sha256': policy['runtime_manifest_sha256'],
    'owner_result_sha256': sha(runtime / 'RESULT.json'), 'audit_sha256': policy['live_audit']['sha256'],
    'restored_source_identities': report['source_identities'], 'raw': raw,
    'full_pre_post_projection_verified': True, 'one_field_epoch_transition_only': True,
    'execution_enabled': False, 'live_main_executed': False, 'unchanged_suites_rerun': False,
    'tested_inputs': {name: sha(HERE / name) for name in ('run.py', 'POLICY.json', 'check_saved.py')},
}
with (HERE / 'CHECK-RESULT.json').open('x') as stream:
    json.dump(result, stream, indent=2, sort_keys=True)
    stream.write('\n')
print(json.dumps(result, indent=2, sort_keys=True))
