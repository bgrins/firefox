import ast
import copy
import importlib.util
import json
import math
from pathlib import Path
import analyze

HERE = Path(__file__).resolve().parent
old_path = HERE.parent / 'css-keyframe-commit-styles-cost-analysis-v1/analyze.py'
spec = importlib.util.spec_from_file_location('old_cost_parser', old_path)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
for name in ('need', 'unique_object', 'decode', 'exact', 'parse_raw', 'summarize', 'main'):
    trees = [ast.parse(p.read_text()) for p in (old_path, HERE / 'analyze.py')]
    definitions = [next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
                   for tree in trees]
    assert ast.dump(definitions[0]) == ast.dump(definitions[1]), name
base = dict(schema='COMMIT_STYLES_COST_V1', config=copy.deepcopy(analyze.CONFIG),
            caseOrder=analyze.CASES[:], rows=[], cleanup=[], valid=True,
            error=None, timingThresholds=False)
for i in range(54):
    round_ = i // 6
    case = analyze.CASES[(i % 6 + round_) % 6]
    family, count = case.split('/')
    base['rows'].append(dict(case=case, family=family, count=int(count), round=round_,
        warmup=round_ < 2, targets=16, calls=16, correctness='PASS', apiMs=1, flushMs=2, totalMs=3))
    base['cleanup'].append(dict(case=case, round=round_, removed=True, effectsCancelled=True))
witnesses = json.loads((HERE / 'TIMESTAMP-WITNESSES.json').read_text())
old_rejections = 0
for witness in witnesses:
    assert 0 <= witness['begin'] <= witness['afterAPI'] <= witness['afterFlush']
    assert witness['apiMs'] == witness['afterAPI'] - witness['begin']
    assert witness['flushMs'] == witness['afterFlush'] - witness['afterAPI']
    assert witness['totalMs'] == witness['afterFlush'] - witness['begin']
    candidate = copy.deepcopy(base)
    candidate['rows'][0].update({m: witness[m] for m in analyze.METRICS})
    snapshot = copy.deepcopy(candidate)
    assert analyze.dataset(candidate) == snapshot
    assert candidate == snapshot
    if not witness['exactAdditionGate']:
        try:
            old.dataset(copy.deepcopy(candidate))
        except ValueError as error:
            assert 'timing addition' in str(error)
            old_rejections += 1
        else:
            raise AssertionError('v1 did not reject the JavaScript witness')
assert old_rejections == 2
first = witnesses[0]
assert not analyze.consistent_timings(first['apiMs'], first['flushMs'],
                                     math.nextafter(first['totalMs'], math.inf))
assert not analyze.consistent_timings(first['apiMs'], first['flushMs'], first['totalMs'] + 1e-12)
assert not analyze.consistent_timings(float.fromhex('0x1.fffffffffffffp+1023'),
                                     float.fromhex('0x1.fffffffffffffp+1023'),
                                     float.fromhex('0x1.fffffffffffffp+1023'))
check = dict(status='BINARY64_COST_CONSISTENCY_CHECK_PASS',
    actual_node_timestamp_vectors=len(witnesses), valid_vectors_rejected_by_v1=old_rejections,
    all_valid_vectors_accepted_unchanged=True, outside_budget_rejections=3,
    unchanged_other_function_asts=7, browser_timing_evidence=False)
(HERE / 'NUMERIC-CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
print(json.dumps(check))
