import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('masked_root_verifier', HERE / 'verify.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
phase_hashes = {'assessment_sha256': 'a', 'raw_sha256': 'b', 'result_sha256': 'c'}


def sample(failures, passed):
    errors = [] if passed else ['changed control signature']
    assessment = {'complete': True, 'errors': [], 'rows': [{'test': '/a' if n < 6 else '/b', 'subtest': str(n), 'status': 'FAIL' if n < failures else 'PASS'} for n in range(7)], 'ends': [{'test': '/a', 'status': 'OK'}, {'test': '/b', 'status': 'OK'}], 'comparison_gate_passed': passed, 'comparison_errors': errors}
    phase = {'execution_error': None, 'preservation_verified': True, 'native_fix_acceptance': False, 'comparison_gate_passed': passed, 'success': True, 'exit': int(failures > 0), 'success_scope': 'complete observation and preservation; comparison verdict retained separately'}
    result = {'success': True, 'restoration_verified': True, 'runtime_controls_unchanged': True, 'empty_staging_preserved': True, 'publication_errors': [], 'native_fix_acceptance': False, 'candidate_phase': phase_hashes, 'error': None, 'success_scope': 'build, complete observation and restoration; callback PASS is separate'}
    return result, phase, assessment, 0


for failures in range(8):
    for passed in (False, True):
        assert module.outcome_join(*sample(failures, passed), phase_hashes) == passed
negative = []


def reject(name, index, key, value):
    data = copy.deepcopy(sample(2, False))
    data[index][key] = value
    try:
        module.outcome_join(*data, phase_hashes)
    except AssertionError:
        negative.append(name)
        return
    raise AssertionError(name)


for name, index, key, value in [
    ('incomplete', 2, 'complete', False), ('infra error', 2, 'errors', ['crash']),
    ('timeout', 2, 'rows', [{'status': 'TIMEOUT'}] * 7), ('missing row', 2, 'rows', []),
    ('missing end', 2, 'ends', []), ('bad end', 2, 'ends', [{'status': 'ERROR'}] * 2),
    ('execution error', 1, 'execution_error', 'timeout'), ('phase preservation', 1, 'preservation_verified', False),
    ('phase false success', 1, 'success', False), ('outer false success', 0, 'success', False),
    ('wrong browser exit', 1, 'exit', 0), ('phase comparison changed', 1, 'comparison_gate_passed', True),
    ('errors erased', 2, 'comparison_errors', []), ('restoration failure', 0, 'restoration_verified', False),
    ('controls changed', 0, 'runtime_controls_unchanged', False), ('staging changed', 0, 'empty_staging_preserved', False),
    ('publication failure', 0, 'publication_errors', ['error']), ('native acceptance', 0, 'native_fix_acceptance', True),
    ('phase acceptance', 1, 'native_fix_acceptance', True), ('outer error', 0, 'error', 'unrelated'),
    ('phase hashes', 0, 'candidate_phase', {}), ('success meaning', 0, 'success_scope', 'all tests pass'),
]:
    reject(name, index, key, value)
data = sample(2, False)
try:
    module.outcome_join(*data[:3], 1, phase_hashes)
except AssertionError:
    negative.append('wrong terminal exit')
else:
    raise AssertionError('wrong terminal exit')

original = sample(1, False)[2]
assessment = sample(3, False)[2]
saved = {'callbacks_passed': 4, 'callbacks_failed': 3, 'all_callbacks_passed': False, 'comparison_gate_passed': False, 'comparison_errors': assessment['comparison_errors'], 'rows': [{'original': a, 'candidate': b} for a, b in zip(original['rows'], assessment['rows'])], 'original_endings': original['ends'], 'candidate_endings': assessment['ends'], 'native_acceptance': False}
assert module.outcomes_join(original, assessment, saved) == saved
for key, value in [('callbacks_failed', 0), ('all_callbacks_passed', True), ('comparison_errors', []), ('rows', []), ('candidate_endings', []), ('native_acceptance', True)]:
    altered = copy.deepcopy(saved)
    altered[key] = value
    try:
        module.outcomes_join(original, assessment, altered)
    except AssertionError:
        negative.append('outcomes ' + key)
    else:
        raise AssertionError(key)

old = (HERE.parents[1] / 'artifacts/css-contextual-duration-base-timing-root-review-v1/verify.py').read_text()
new = (HERE / 'verify.py').read_text()
start = "    for name, role in roles.items():"
end = "    if passed:\n"
old_block = old[old.index(start):old.index(end, old.index(start))]
assert new[new.index(start):new.index(start) + len(old_block)] == old_block
start = "    if observation['before'] != observation['after']:"
assert old[old.index(start):] == new[new.index(start):]
assert 'shutil.rmtree' not in new
assert "read(PAIR / 'PHASES-PRE.json') == read(PAIR / 'PHASES-POST.json') == compiled['snapshot']" in new
assert module.CONFIG['execution_enabled'] is False
print(json.dumps({'positive_outcomes': 16, 'paired_outcomes_positive': 1, 'negative_checks': negative, 'source_app_fullstate_prefix_unchanged': True, 'raw_index_write_rollback_tail_unchanged': True, 'retained_backup_deletion_not_supported': True, 'live_operations': False}, indent=2))
