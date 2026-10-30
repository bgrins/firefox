import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('root_postrun_verifier', HERE / 'verify.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
phase_hashes = {'assessment_sha256': 'a', 'raw_sha256': 'b', 'result_sha256': 'c'}


def sample(failures):
    passed = failures == 0
    errors = [] if passed else ['changed control signature']
    assessment = {'complete': True, 'errors': [], 'rows': [{'status': 'FAIL' if n < failures else 'PASS'} for n in range(2)], 'ends': [{'status': 'OK'}], 'comparison_gate_passed': passed, 'comparison_errors': errors}
    phase = {'execution_error': None, 'preservation_verified': True, 'native_fix_acceptance': False, 'comparison_gate_passed': passed, 'success': passed, 'exit': int(not passed)}
    result = {'success': passed, 'restoration_verified': True, 'runtime_controls_unchanged': True, 'empty_staging_preserved': True, 'publication_errors': [], 'native_fix_acceptance': False, 'candidate_phase': phase_hashes if passed else None, 'error': None if passed else repr(AssertionError((None, True, [], errors)))}
    return result, phase, assessment, int(not passed)


for failures in (0, 1, 2):
    assert module.outcome_join(*sample(failures), phase_hashes) == (failures == 0)
negative = []


def reject(name, index, key, value, failures=2):
    data = copy.deepcopy(sample(failures))
    data[index][key] = value
    try:
        module.outcome_join(*data, phase_hashes)
    except AssertionError:
        negative.append(name)
        return
    raise AssertionError(name)


reject('incomplete stream', 2, 'complete', False)
reject('infrastructure error', 2, 'errors', ['crash'])
reject('unallowed status', 2, 'rows', [{'status': 'TIMEOUT'}, {'status': 'FAIL'}])
reject('missing callback', 2, 'rows', [{'status': 'FAIL'}])
reject('bad ending', 2, 'ends', [{'status': 'ERROR'}])
reject('phase execution error', 1, 'execution_error', 'timeout')
reject('phase preservation failure', 1, 'preservation_verified', False)
reject('restoration failure', 0, 'restoration_verified', False)
reject('canonical mutation', 0, 'runtime_controls_unchanged', False)
reject('staging mutation', 0, 'empty_staging_preserved', False)
reject('publication errors', 0, 'publication_errors', ['error'])
reject('native acceptance', 0, 'native_fix_acceptance', True)
reject('wrong failure origin', 0, 'error', "RuntimeError('unrelated failure')")
reject('failed outer relabeled success', 0, 'success', True)
reject('failure with successful phase joins', 0, 'candidate_phase', phase_hashes)
reject('failure without failing callback', 2, 'rows', [{'status': 'PASS'}, {'status': 'PASS'}])
reject('wrong phase exit', 1, 'exit', 0)
reject('successful phase hash mismatch', 0, 'candidate_phase', {}, failures=0)
reject('successful outer carries error', 0, 'error', 'error', failures=0)
print(json.dumps({'synthetic_positive_outcomes': ['2 PASS', '1 PASS / 1 FAIL', '2 FAIL'], 'negative_checks': negative, 'live_reads_or_mutations': False}, indent=2))
