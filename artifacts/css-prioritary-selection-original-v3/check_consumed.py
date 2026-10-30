import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = json.loads((HERE / 'POLICY.json').read_bytes())
guard = ROOT / policy['intermediate_guard_binding']['directory']
mocks = load('guard_mocks', guard / 'check.py')
intermediate = load('owner_guard', HERE / 'intermediate.py')
binding = load('owner_binding', HERE / 'inputs.py')
scope = load('owner_scope', HERE / 'review_scope.py')
manifest = json.dumps({name: {'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest()}
                       for name in ['POLICY.json', 'run.py', 'baseline.py', 'closure.py', 'intermediate.py', 'inputs.py']}).encode()
manifest_digest = hashlib.sha256(manifest).hexdigest()
effective = binding.bind_inputs(policy['owner_directory'], manifest, manifest_digest, policy['intermediate_consumed_inputs'])
epoch = {
    'raw_index_observation': {'current': 'R'},
    'semantic_index': {'head': 'H', 'entries': 'E', 'cached_diff': 'D'},
    'nested_semantic_index': {'head': 'H', 'entries': 'E', 'cached_diff': 'D'},
    'pins': {'native': 'N'}, 'staged_working': {'staged': 'S'},
    'committed_research_working_payloads': {'unrelated-archive': 'A'},
    'installed_identities': {'native': [1, 2]},
    'modified_native_paths': ['native'], 'untracked_native': ['untracked'],
}
checks = mocks.MockChecks()
checks.bodies.update(effective)
snapshot = intermediate.verify_intermediate(checks, mocks.MockPath(), {}, epoch, effective)
scope.require_intermediate(snapshot, effective)
assert set(checks.reads) == {'native', 'staged'} | set(effective)
assert 'unrelated-archive' not in checks.reads
targets = [
    policy['owner_directory'] + '/run.py',
    'artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py',
    'artifacts/css-prioritary-zoom-capture-v1/candidate.html',
    policy['suite_binding']['directory'] + '/MANIFEST.json',
    policy['wpt_lanes']['forced_colors']['resources']['/forced-colors-mode/registered-prioritary-forced-color-selection.tentative.html']['path'],
]
for path in targets:
    changed = mocks.MockChecks()
    changed.bodies.update(effective)
    changed.bodies[path] = 'changed'
    mocks.rejected(lambda: intermediate.verify_intermediate(changed, mocks.MockPath(), {}, epoch, effective))
mocks.rejected(lambda: scope.require_full(snapshot))
assert binding.bind_inputs(policy['owner_directory'], manifest, manifest_digest, policy['intermediate_consumed_inputs']) == effective
print(json.dumps({'real_external_map_pins': len(policy['intermediate_consumed_inputs']),
                  'synthetic_partial_owner_manifest': True, 'effective_pins': len(effective),
                  'consumed_mutations_rejected': len(targets), 'limited_rejected_as_full': True,
                  'unrelated_archive_not_read': True, 'live_operations': False}))
