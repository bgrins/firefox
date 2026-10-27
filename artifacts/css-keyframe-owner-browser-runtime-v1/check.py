import ast
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
OLD = ROOT / 'artifacts/css-keyframe-operation-descriptor-capture-preparation-v1'
BASELINE = ROOT / 'artifacts/css-keyframe-operation-descriptor-capture-runtime-v1'
OWNER = ROOT / 'artifacts/css-keyframe-animation-rule-owner-host-combined-v2'
read = lambda p: json.loads(p.read_text())
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c = load('capture', HERE / 'capture.py')
o = load('owner_epoch', HERE / 'owner_epoch.py')
parser = load('classifier', HERE / 'classify.py')
inputs = read(HERE / 'INPUTS.json')
assert inputs['ready'] is False and inputs['execution_epoch'] is None and inputs['owner_runtime_manifest'] is None
assert inputs['reviewed_sources'] is None and inputs['expected_applied'] is None
for name, pin in inputs['local_pins'].items():
    assert digest(HERE / name) == pin
for name, pin in read(HERE / 'REFERENCES.json').items():
    assert digest(ROOT / name) == pin
for directory in [BASELINE, OWNER]:
    for name, pin in read(directory / 'FILES.json').items():
        assert digest(directory / name) == pin
for name in ['CONFIG.json', 'BASELINE-ROWS.json', 'REQUIRED-ROLES.json', 'server-config.json', 'classify.py']:
    assert (HERE / name).read_bytes() == (OLD / name).read_bytes()
old_source = (OLD / 'capture.py').read_text()
source = (HERE / 'capture.py').read_text()
assert source[source.index('    def verify(active):'):] == old_source[old_source.index('    def verify(active):'):]
rows = read(HERE / 'BASELINE-ROWS.json')
run = read(BASELINE / 'wpt-diagnostic/RUN.json')
assert len(rows) == len(run['rows']) == 166 and not c.compare_rows(rows, run['rows'])
config = read(HERE / 'CONFIG.json')
assert len(config['tests']) == 13 and len(config['reftests']) == 2
assert sum(len(v) for v in config['expected_subtests'].values()) == 166
assert sum(r['status'] == 'PASS' for r in rows) == 162
roster = read(ROOT / 'artifacts/css-keyframe-invalid-registered-endpoint-diagnostic-v1/ROSTER.json')
provider = [r for r in rows if r['test'] == '/' + roster['logical_path']]
classified = parser.classify(provider, roster)
assert classified['pass_count'] == 6 and classified['fail_count'] == 4
assert all(r['classification'] == 'CALIBRATED_FINAL_HISTORY_MISMATCH' for r in classified['rows'][:4])
for mutation in ['remove', 'status', 'message']:
    changed = copy.deepcopy(rows)
    if mutation == 'remove':
        changed.pop()
    else:
        changed[0][mutation] = 'different'
    assert c.compare_rows(changed, rows)
try:
    c.compare_rows(rows + rows[:1], rows)
except RuntimeError:
    pass
else:
    raise AssertionError('duplicate admitted')
producer = read(HERE / 'OWNER-PRODUCER.json')
applied = read(ROOT / producer['applied']['path'])
reviewed = read(OLD / 'EXPECTED-SOURCES.json') | applied['postimages'] | applied['preserved']
assert set(read(HERE / 'REQUIRED-SOURCE-PATHS.json')) <= set(reviewed)
assert len(applied['postimages']) == 18
selection = read(OWNER / 'GTEST-SELECTION.json')
binary_names = ['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
                'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
                'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL',
                'objdir-full.noindex/dist/bin/gtest/XUL']
source_epoch = {'pins': reviewed | {p: '1' * 64 for p in binary_names},
                'provenance': {}, 'modified_native_paths': list(applied['postimages']), 'untracked_native': [],
                'semantic_index': dict(head='a', entries='b', cached_diff='c', working_diff='d'),
                'nested_semantic_index': dict(head='e', entries='f', cached_diff='g', working_diff='h'),
                'raw_index_observation': {'current': 'i'}}
events = [event for name in selection['names'] for event in [('START', name), ('END', 'PASS')]]
gtest = ''.join('TEST_' + kind + ': ' + value + '\n' for kind, value in events)
gtest += 'Ran 17 test(s) from 4 test suite(s) (0 disabled), with 0 failure(s).\n'
negative_count = 0
with tempfile.TemporaryDirectory(prefix='owner-admission-') as directory:
    runtime = Path(directory) / 'artifacts/run'
    runtime.mkdir(parents=True)

    def write_case(fault=None):
        test_producer = copy.deepcopy(producer)
        payloads = {'SOURCE-EPOCH.json': copy.deepcopy(source_epoch), 'APPLIED.json': copy.deepcopy(applied),
                    'BINARIES.json': {'before': {p: '1' * 64 for p in binary_names}, 'after': {p: '2' * 64 for p in binary_names}},
                    'gtest.log': gtest,
                    'RESULT.json': {'status': 'COMPACT_OWNER_BUILD_AND_17_TESTS_PASS', 'source_composition': 'owner17_plus_corrected_borrow4_equals_18', 'preservation': True, 'events': [list(e) for e in events]},
                    'run.py': (ROOT / 'artifacts/css-keyframe-owner-runtime-v2/run.py').read_text(),
                    'ROOT-EXECUTION.json': {'session': 1, 'launch': 'synthetic', 'terminal': 'synthetic', 'outer_exit': 0},
                    'BEFORE.json': {'current_raw_stable_during_check': True, 'working_sources_binaries_research_preserved': True,
                        'index': source_epoch['semantic_index'] | {'raw_index': 'i'},
                        'nested_index': source_epoch['nested_semantic_index'] | {'raw_index': 'j'}}}
        payloads['PRESERVATION.json'] = copy.deepcopy(payloads['BEFORE.json'])
        execution = []
        for step, phase in enumerate(['metadata', 'export', 'binaries', 'gtest']):
            log = payloads.setdefault(phase + '.log', 'synthetic ' + phase)
            record = {'phase': phase, 'exit': 0, 'finished': step + 1, 'log_sha256': hashlib.sha256(log.encode()).hexdigest()}
            execution.append(record)
            payloads[phase + '-EXECUTION.json'] = record
            payloads[phase + '-COMMAND.json'] = {'command': producer['commands'][phase], 'started': step}
        payloads['EXECUTION.json'] = execution
        current = copy.deepcopy(source_epoch)
        current['pins'].update(payloads['BINARIES.json']['after'])
        dump = lambda value: json.dumps(value, sort_keys=True) + '\n'
        current['provenance']['compact_owner_execution'] = {'path': 'artifacts/run/EXECUTION.json', 'sha256': hashlib.sha256(dump(execution).encode()).hexdigest()}
        payloads['CURRENT-EPOCH.json'] = current
        for key, value in [('source_epoch', source_epoch), ('applied', applied),
                           ('unit_result', {'status': 'UNIT_AND_DOC_TESTS_PASS', 'preservation': True, 'diagnostics': {'E0597': 2, 'E0277': 2}})]:
            relative = 'artifacts/unit/' + key + '.json'
            path = Path(directory) / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(dump(value))
            test_producer[key] = {'path': relative, 'sha256': digest(path)}
        if fault == 'terminal': payloads['ROOT-EXECUTION.json']['outer_exit'] = 1
        if fault == 'preservation': payloads['PRESERVATION.json']['working_sources_binaries_research_preserved'] = False
        if fault == 'nested_raw': payloads['PRESERVATION.json']['nested_index']['raw_index'] = 'changed'
        if fault == 'command': payloads['export-COMMAND.json']['command'] = ['wrong']
        if fault == 'producer': payloads['run.py'] += '\n# changed\n'
        if fault == 'log': payloads['binaries.log'] += 'changed'
        if fault == 'composition': payloads['APPLIED.json']['postimages'].pop('servo/components/servo_arc/lib.rs')
        if fault == 'phase': execution[2]['exit'] = 2
        if fault == 'test': payloads['gtest.log'] = gtest.replace(selection['names'][0], 'Missing.Test')
        if fault == 'binary': current['pins'][binary_names[0]] = '3' * 64
        if fault == 'source': payloads['SOURCE-EPOCH.json']['pins'][next(iter(reviewed))] = '4' * 64
        if fault == 'applied': payloads['APPLIED.json']['postimages'] = {}
        if fault == 'inventory': current['modified_native_paths'].append('dom/unpinned.cpp')
        manifest = {}
        for name, value in payloads.items():
            body = value if isinstance(value, str) else dump(value)
            (runtime / name).write_text(body)
            manifest[name] = digest(runtime / name)
        path = runtime / 'FILES.json'
        path.write_text(dump(manifest))
        return current, path, test_producer

    current, manifest, test_producer = write_case()
    assert o.admit(current, manifest, reviewed, selection, applied, test_producer) == {p: source_epoch['pins'][p] for p in sorted(reviewed)}
    for fault in ['phase', 'test', 'binary', 'source', 'applied', 'inventory', 'terminal', 'preservation', 'nested_raw', 'command', 'producer', 'log', 'composition']:
        current, manifest, test_producer = write_case(fault)
        try:
            o.admit(current, manifest, reviewed, selection, applied, test_producer)
        except RuntimeError:
            negative_count += 1
        else:
            raise AssertionError(fault)
print(json.dumps({'status': 'COMPACT_OWNER_BROWSER_PREPARATION_STATIC_PASS', 'rows': 166,
                  'files': 13, 'crashes': 2, 'historical_outcomes': {'PASS': 162, 'FAIL': 4},
                  'required_source_paths': len(reviewed), 'owner_admission_inert_negatives': negative_count,
                  'exact_composed_source_count': 18,
                  'capture_preservation_and_finally_unchanged': True,
                  'actual_owner_runtime_bound': False, 'live_operations': False}, indent=2))
