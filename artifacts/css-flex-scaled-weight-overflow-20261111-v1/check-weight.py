import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOLVER = Path('/opt/homebrew/bin/z3').resolve()
BASE = '''(set-logic QF_FPBV)
(set-option :timeout 30000)
(set-option :smt.random_seed 0)
(declare-fun x () (_ FloatingPoint 11 53))
(declare-fun y () (_ FloatingPoint 11 53))
(define-fun zero () (_ FloatingPoint 11 53) (_ +zero 11 53))
(define-fun one () (_ FloatingPoint 11 53) ((_ to_fp 11 53) #x3ff0000000000000))
'''
WEIGHT = BASE + '''
(declare-fun shrink () (_ FloatingPoint 8 24))
(declare-fun base () (_ BitVec 32))
(define-fun shrink64 () (_ FloatingPoint 11 53) ((_ to_fp 11 53) RNE shrink))
(define-fun base64 () (_ FloatingPoint 11 53) ((_ to_fp 11 53) RNE base))
(define-fun corrected () (_ FloatingPoint 11 53) (fp.mul RNE shrink64 base64))
'''
QUERIES = {
'finite-weight-bound': WEIGHT + '''
(assert (fp.geq shrink (_ +zero 8 24)))
(assert (not (fp.isInfinite shrink)))
(assert (bvsge base #x00000000))
(define-fun limit () (_ FloatingPoint 11 53) ((_ to_fp 11 53) #x49e0000000000000))
(assert (not (and (fp.geq corrected zero) (fp.leq corrected limit))))
(check-sat)
(get-info :reason-unknown)
''',
'overflow-witness': WEIGHT + '''
(assert (= shrink ((_ to_fp 8 24) #x7e967699)))
(assert (= base #x00001770))
(define-fun original () (_ FloatingPoint 8 24) (fp.mul RNE shrink ((_ to_fp 8 24) RNE base)))
(assert (fp.isInfinite original))
(assert (not (fp.isInfinite corrected)))
(assert (fp.gt corrected zero))
(check-sat)
(get-value (original corrected))
''',
}
out = HERE / 'solver' / 'run-1'
out.mkdir(exist_ok=False)
engine = ROOT / 'artifacts/css-flex-main-positioning-target-20261111-v2'
assert hashlib.sha256((engine / 'FILES.json').read_bytes()).hexdigest() == 'eb2bbc722e548fb13d6f9bd306998990344628fced432eb0dcde431e8a24e7f2'
assert hashlib.sha256((engine / 'process.py').read_bytes()).hexdigest() == json.loads((engine / 'FILES.json').read_text())['process.py']
(out / 'INPUTS.json').write_text(json.dumps({
    'solver': str(SOLVER),
    'solver_sha256': hashlib.sha256(SOLVER.read_bytes()).hexdigest(),
    'version': subprocess.check_output([str(SOLVER), '--version'], text=True).strip(),
    'source_sha256': hashlib.sha256((ROOT / 'layout/generic/nsFlexContainerFrame.cpp').read_bytes()).hexdigest(),
    'model': 'SMT-LIB binary64 RNE; manual source mapping; no Lean certificate or native refinement',
}, indent=2) + '\n')
helper = runpy.run_path(str(engine / 'process.py'))
runner = helper['Runner'](out)
results = {}
for name, query in QUERIES.items():
    path = out / (name + '.smt2')
    path.write_text(query)
    record, log = runner.run([str(SOLVER), '-memory:1024', '-smt2', str(path)],
                             ROOT, os.environ.copy(), name, timeout=45)
    results[name] = {'exit': record['exit'], 'output': log,
                     'query_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    (out / 'RESULTS.json').write_text(json.dumps(results, indent=2) + '\n')
    assert record['exit'] == 0 and '(error' not in log
    assert log.splitlines()[0] in ['sat', 'unsat', 'unknown']
    print(name + ': ' + log.strip(), flush=True)
assert runner.safe_cleanup and all(helper['absent'](g) for g in runner.groups)
(out / 'LIFECYCLE.json').write_text(json.dumps({'groups_absent': True, 'groups': runner.groups}, indent=2) + '\n')
