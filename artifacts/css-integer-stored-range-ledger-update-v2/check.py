import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prepare', HERE / 'prepare.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sequence = json.loads((HERE / 'SEQUENCE.json').read_text())
mapping = {r['old_commit']: hashlib.sha1(('inert-only:' + r['old_commit']).encode()).hexdigest() for r in sequence}
result = {'status': 'FIX121_HISTORY_PUBLICATION_RECOVERY_VERIFIED', 'published': True,
          'errors': [], 'signatures_verified': True, 'final_tree_exact_carrier': True,
          'current_ledgers_modified': False, 'rewrites': mapping,
          'new_tip': mapping[sequence[-1]['old_commit']]}
result.update(reused_signed_commits=37, git_writers_serialized=True, non_atomic_symbolic_head_check=True, carrier='c' * 40, backup='refs/heads/inert-backup')
failed_result = {'status': 'FAILED', 'published': False, 'failure_preservation_verified': True,
                 'errors': ['inert publication failure'], 'rewrites': mapping,
                 'carrier': result['carrier'], 'backup': result['backup']}
failed_execution = {'exit': 1, 'session': 2, 'terminal_chunk': 'inert-failed'}
execution = {'exit': 0, 'session': 1, 'terminal_chunk': 'inert-only'}
refs = {k: {'path': 'artifacts/INERT-NOT-ACTUAL/' + k + '.json', 'sha256': '0' * 64}
        for k in ['rewrite_map', 'result', 'execution']}
before, after = module.build(mapping, result, execution, refs, failed_result, failed_execution)
assert len(after) == 5
old, new = json.loads(before[module.CURRENT]), json.loads(after[module.CURRENT])
assert new['pre_fix121_rewrite_summaries']['latest_signing'] == old['latest_signing']
assert len(old['new_queue']) == len(new['new_queue'])
changed = {b['fix'] for a, b in zip(old['new_queue'], new['new_queue']) if a != b}
assert changed == set(range(121, 132)) | {133, 134}
for n in after:
    if n.endswith('css-fix-readout-20261023/README.md'):
        assert after[n].split('Historical checkpoint text follows', 1)[1] == before[n].split('Historical checkpoint text follows', 1)[1]
for key, value in [('published', False), ('errors', ['bad']), ('signatures_verified', False),
                   ('final_tree_exact_carrier', False), ('current_ledgers_modified', True),
                   ('new_tip', '0' * 40), ('reused_signed_commits', 36),
                   ('git_writers_serialized', False), ('non_atomic_symbolic_head_check', False)]:
    bad = copy.deepcopy(result)
    bad[key] = value
    try:
        module.validate(mapping, bad, execution, failed_result, failed_execution)
    except AssertionError:
        pass
    else:
        raise AssertionError(key)
bad = dict(mapping)
bad.pop(next(iter(bad)))
for m, e in [(bad, execution), (mapping, dict(execution, exit=1))]:
    try:
        module.validate(m, result, e, failed_result, failed_execution)
    except AssertionError:
        pass
    else:
        raise AssertionError('failed receipt admitted')
for key, value in [('published', True), ('failure_preservation_verified', False), ('rewrites', {}), ('errors', [])]:
    bad = copy.deepcopy(failed_result)
    bad[key] = value
    try:
        module.validate(mapping, result, execution, bad, failed_execution)
    except AssertionError:
        pass
    else:
        raise AssertionError('failed run relabeled: ' + key)
print('PASS: five candidate bodies, exact thirteen affected fixes, historical preservation, fifteen rejected invalid bindings; no live writes')
