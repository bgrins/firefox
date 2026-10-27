import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok, why):
    if not ok:
        raise RuntimeError(why)
def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def check():
    c = read(HERE / 'CONFIG.json')
    assert c['ready_for_execution'] is False and c['epoch'] is None and c['epoch_receipt'] is None
    for n, h in read(HERE / 'REFERENCES.json').items():
        assert sha(ROOT / n) == h, n
    for name in ['run.py', 'tests.py', 'baseline_gate.py', 'check.py']:
        compile((HERE / name).read_text(), str(HERE / name), 'exec')
    old_driver = (ROOT / 'artifacts/css-cssom-integer-rounding-candidate-only-v1/run.py').read_text()
    driver = (HERE / 'run.py').read_text()
    marker = "finally:\n    state.update(status='restoring', recovery_errors=errors)"
    assert driver[driver.index(marker):] == old_driver[old_driver.index(marker):]
    start, end = 'def replace_source(', "\ntry:\n    for n in c['sources']:"
    assert driver[driver.index(start):driver.index(end)] == old_driver[old_driver.index(start):old_driver.index(end)]
    assert sum(map(len, c['baseline_expected_subtests'].values())) == 61 and len(c['baseline_tests']) == 5
    assert sum(map(len, c['expected_subtests'].values())) == 141 and len(c['tests']) == 13
    assert len(c['expected_subtests'][c['main_test']]) == 32
    assert all(len(v) == len(set(v)) for v in c['expected_subtests'].values())
    assert len(c['baseline_failures']) == 8
    assert sha(HERE / 'fixture.html') == sha(ROOT / c['proposal'] / 'offset-scroll-integer-precision.html')
    assert sha(ROOT / c['candidate_sources']['dom/base/Element.cpp']) == c['candidate_pins']['dom/base/Element.cpp']
    assert all(not (HERE / n).exists() for n in ['wpt-baseline', 'wpt-candidate', 'STATE.json', 'BEFORE.json', 'original'])
    class Wpt:
        CONFIG = c
        need = staticmethod(need)
        receipts = {}
        @staticmethod
        def save(n, data):
            Wpt.receipts[n] = data
    wpt = Wpt()
    old_runtime = ROOT / c['retained_baseline']
    old_config = read(old_runtime / 'CONFIG.json')
    old_config['epoch'] = c['retained_baseline']
    old_resources = read(old_runtime / 'RESOURCES.json')
    old_owned, old_copy = next(iter(old_config['install'].items()))
    reanalysis = ROOT / c['reanalysis']
    old_tests = load('old_tests_check', reanalysis / 'tests.py')
    gate = load('old_gate_check', HERE / 'baseline_gate.py')
    wpt.CONFIG = old_config
    retained = gate.validate(wpt, old_tests, old_runtime, reanalysis,
        read(old_runtime / 'STATE.json'), old_resources, sha(old_runtime / old_copy), sha)
    wpt.CONFIG = c
    resources = read(HERE / 'RESOURCES.json')
    before = {**resources, **c['head_pins'], **c['baseline_pins']}
    old = {**old_resources, **old_config['head_pins'], **old_config['baseline_pins']}
    assert all(before.get(n) == h for n, h in old.items() if n != old_owned)
    controls = [r for r in retained['rows'] if r['test'] in c['expected_subtests']]
    assert len(controls) == 80 and sum(r['status'] == 'FAIL' for r in controls) == 4
    tests = load('new_tests_check', HERE / 'tests.py')
    rows = []
    for test, names in c['baseline_expected_subtests'].items():
        for name in names:
            failure = test == c['main_test'] and name in c['baseline_failures']
            row = {'test': test, 'subtest': name, 'status': 'FAIL' if failure else 'PASS'}
            if failure:
                row.update(message=c['baseline_failures'][name], expected='PASS')
            rows.append(row)
    ends = [{'test': test, 'status': 'OK'} for test in c['baseline_expected_subtests']]
    tests.require_phase(wpt, 'baseline', {'rows': rows, 'ends': ends})
    paired = {'rows': rows + controls}
    candidate = copy.deepcopy(paired)
    for row in candidate['rows']:
        if row['test'] == c['main_test']:
            row['status'] = 'PASS'
            row.pop('message', None)
            row.pop('expected', None)
    candidate['ends'] = [{'test': test, 'status': 'OK'} for test in c['expected_subtests']]
    tests.require_phase(wpt, 'candidate', candidate)
    tests.compare(wpt, paired, candidate)
    assert len(wpt.receipts['COMPARISON.json']['repaired']) == 8
    def rejected(fn):
        try:
            fn()
        except RuntimeError:
            return
        raise AssertionError('negative accepted')
    bad = copy.deepcopy(candidate)
    bad['rows'][0]['status'] = 'FAIL'
    rejected(lambda: tests.compare(wpt, paired, bad))
    bad = copy.deepcopy(candidate)
    next(r for r in bad['rows'] if r['status'] == 'FAIL')['message'] = 'changed diagnosis'
    rejected(lambda: tests.compare(wpt, paired, bad))
    bad = copy.deepcopy(candidate)
    bad['rows'].pop()
    rejected(lambda: tests.compare(wpt, paired, bad))
    bad = copy.deepcopy(rows)
    next(r for r in bad if r['status'] == 'FAIL')['message'] = 'calibration failed'
    rejected(lambda: tests.require_phase(wpt, 'baseline', {'rows': bad, 'ends': ends}))
    source = ast.parse(driver)
    node = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'require_epoch')
    namespace = dict(c=copy.deepcopy(c), need=need, read=read, sha=sha, reanalysis=reanalysis)
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<epoch-only>', 'exec'), namespace)
    previous = ROOT / 'artifacts/css-cssom-integer-rounding-candidate-runtime-v1'
    epoch, receipt = read(previous / 'STATE.json'), read(previous / 'ROOT-FINAL-CHECK.json')
    namespace['c']['epoch_receipt'] = receipt
    namespace['require_epoch'](previous, epoch, receipt)
    for key, value in [('restored', False), ('restore_build_exit', 1), ('recovery_errors', ['error']), ('paired_preservation_passed', False)]:
        broken = copy.deepcopy(epoch)
        broken[key] = value
        rejected(lambda: namespace['require_epoch'](previous, broken, receipt))
    result = {'disabled_unbound': True, 'baseline_rows_files': [61, 5], 'candidate_rows_files': [141, 13],
        'archived_control_rows_authenticated': 80, 'archived_expected_failures': 4,
        'historical_resource_transfer': True, 'restoration_tail_unchanged': True, 'atomic_source_replacement_unchanged': True,
        'synthetic_expected_repairs': 8, 'negative_checks': 8, 'actual_terminal_epoch_schema_checked': True,
        'native_browser_build_or_index_actions': False}
    (HERE / 'STATIC-CHECK.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result))
if __name__ == '__main__':
    check()
