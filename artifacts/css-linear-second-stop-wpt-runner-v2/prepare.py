import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'artifacts/css-random-counter-paired-wpt-runner-v2'
PLAN = ROOT / 'artifacts/css-linear-second-stop-paired-plan-v1'
SOURCE = ROOT / 'artifacts/css-linear-second-position-guard-proposal-v2'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


policy = read(OLD / 'POLICY.json')
plan = read(PLAN / 'POLICY.json')
target = plan['target_page']
calibration = '/css/css-easing/linear-endpoint-feature-calibration.html'
tests = {name: 'testharness' for name in [*plan['regressions'], calibration, target]}
source_name = 'servo/components/style/values/specified/easing.rs'
roles = {role: {source_name: sha(SOURCE / directory / source_name)}
         for role, directory in [('original', 'base'), ('candidate', 'candidate')]}
policy.update(execution_enabled=False,
              frozen_head='b1cae69e67ccfb707b4d9010d34386009e01d9c2',
              owner_runtime='artifacts/css-linear-second-position-reversible-pair-runtime-1',
              source_package_manifest=sha(SOURCE / 'FILES.json'),
              tests=tests, source_roles=roles, regression_subtests=plan['regressions'],
              target_subtests={target: plan['target_subtests']},
              calibration_subtests={calibration: plan['feature_calibration']['subtests']},
              held_subtests={}, expected_subtest_count=48,
              cardinality_description='Six crash/recovery targets, forty regression subtests, two feature calibrations',
              live_oracle_sources={'testing/web-platform/tests' + target: None,
                                   'testing/web-platform/tests' + calibration: None},
              unchanged_native_sources={})
policy['helpers']['epoch'] = str((HERE / 'epoch.py').relative_to(ROOT))
policy['phase_outputs'] = {'original-baseline-1': 'original-baseline-wpt',
                           'original-crash-1': 'original-crash-wpt',
                           'candidate-1': 'candidate-wpt'}
policy['phase_tests'] = {'original-baseline-1': {n: k for n, k in tests.items() if n != target},
                         'original-crash-1': {target: 'testharness'}, 'candidate-1': tests}
policy['known_absent_resource'] = 'testing/web-platform/tests/css/css-easing/support/util.js'
save('POLICY.json', policy)
save('EXPERIMENT.json', {k: policy[k] for k in ('phase_tests', 'regression_subtests', 'target_subtests', 'calibration_subtests')})
(HERE / 'SIGNING-BASELINE-EPOCH.json').write_bytes((ROOT / 'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json').read_bytes())
(HERE / 'epoch.py').write_bytes((OLD / 'epoch.py').read_bytes())
names = set()
for test in tests:
    rel = Path(test.lstrip('/'))
    names.add('testing/web-platform/tests/' + str(rel))
    names.add('testing/web-platform/tests/' + str(rel) + '.headers')
    names.add('testing/web-platform/meta/' + str(rel) + '.ini')
    for parent in [rel.parent, *rel.parents[1:]]:
        names.add(str(Path('testing/web-platform/tests') / parent / '__dir__.headers'))
        names.add(str(Path('testing/web-platform/meta') / parent / '__dir__.ini'))
names.update('testing/web-platform/tests/' + n for n in (
    'resources/testharness.js', 'resources/testharnessreport.js',
    'css/support/parsing-testcommon.js', 'css/support/computed-testcommon.js',
    'css/css-easing/testcommon.js', 'css/css-easing/support/util.js'))
overrides = {'testing/web-platform/tests' + target: PLAN / 'linear-contextual-second-position-crash.html',
             'testing/web-platform/tests' + calibration: PLAN / 'feature-calibration.html'}
pins = {}
for name in sorted(names):
    origin = overrides.get(name, ROOT / name)
    exists = origin.exists()
    item = {'origin': str(origin.relative_to(ROOT)), 'exists': exists,
            'capture': 'capture/' + name, 'sha256': sha(origin) if exists else None}
    if exists:
        assert origin.is_file() and not origin.is_symlink()
        destination = HERE / item['capture']
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(origin.read_bytes())
        item['bytes'] = origin.stat().st_size
    pins[name] = item
assert not pins[policy['known_absent_resource']]['exists']
for name in plan['regressions']:
    assert (ROOT / ('testing/web-platform/tests' + name)).read_bytes() == (PLAN / Path(name).name).read_bytes()
save('SOURCE-PINS.json', pins)
manifest = {'version': 9, 'url_base': '/', 'items': {'testharness': {}}}
for name in tests:
    body = (HERE / pins['testing/web-platform/tests' + name]['capture']).read_bytes()
    entry = [hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest(), [None, {}]]
    node = manifest['items']['testharness']
    parts = name.lstrip('/').split('/')
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = entry
save('SUBSET-MANIFEST.json', manifest)
references = {str((OLD / n).relative_to(ROOT)): sha(OLD / n) for n in ('run.py', 'assess.py', 'bindings.py', 'epoch.py', 'FILES.json')}
references.update({n: sha(ROOT / n) for n in policy['helpers'].values() if n != policy['helpers']['epoch']})
references.update({str((p / 'FILES.json').relative_to(ROOT)): sha(p / 'FILES.json') for p in (PLAN, SOURCE)})
save('REFERENCES.json', references)
runner = (OLD / 'run.py').read_text()
runner = runner.replace('original-1|candidate-1', 'original-baseline-1|original-crash-1|candidate-1')
runner = runner.replace('phase in ("original-1", "candidate-1")', 'phase in policy["phase_outputs"]')
runner = runner.replace('(role + "-wpt")', 'policy["phase_outputs"][phase]')
runner = runner.replace('css-random-counter-wpt-', 'css-linear-guard-wpt-')
runner = runner.replace('and assessment["complete"]', 'and assessment["phase_gate_passed"]')
runner = runner.replace('"comparison_gate_passed": comparison, "native_fix_acceptance": False,',
                        '"comparison_gate_passed": comparison, "phase_gate_passed": bool(passed), "native_fix_acceptance": False,')
(HERE / 'run.py').write_text(runner)
bindings = (OLD / 'bindings.py').read_text()
bindings = bindings[:bindings.index('\ndef validate_original(')]
bindings = bindings.replace('reversible_random_counter_phase', 'reversible_linear_guard_phase')
bindings = bindings.replace('four-source', 'one-source')
bindings = bindings.replace("q['build_epoch_sha256'] = epoch_sha", "q['tests'] = fixed['phase_tests'][phase]\n    q['build_epoch_sha256'] = epoch_sha")
start = bindings.index("    if role == 'candidate':")
end = bindings.index('    return q', start)
bindings = bindings[:start] + '''    if role == 'candidate':
        captures = {}
        for label in ('original-baseline', 'original-crash'):
            runtime = root / owner / (label + '-wpt')
            files, links = inventory(runtime, h)
            captures[label] = {'runtime': str(runtime.relative_to(root)), 'files': files, 'symlinks': links}
        q['original_binding'] = {'capsule': str(here.relative_to(root)),
                                 'capsule_sha256': h.sha(here / 'FILES.json'), 'captures': captures}
''' + bindings[end:]
(HERE / 'bindings.py').write_text(bindings)
print('Prepared immutable fixture copies and adapted lifecycle helpers; assessment and original replay remain to implement')
