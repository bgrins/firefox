import ast
from collections import Counter
import copy
import difflib
import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
binding = json.loads((HERE / 'BINDINGS.json').read_bytes())
assert binding['execution_enabled'] is False and binding['pending_owner_terminal'] is True
assert binding['result_sha256'] is binding['terminal_sha256'] is None
assert binding['outer_group'] == 35872
for path, pin in binding['references'].items():
    assert sha(ROOT / path) == pin
parent = ROOT / 'artifacts/css-resumable-font-selection-integrated-pair-root-audit-v1/audit.py'
source = (HERE / 'audit.py').read_text()
compile(source, 'audit.py', 'exec')
assert (HERE / 'AUDIT-DELTA.patch').read_text() == ''.join(difflib.unified_diff(parent.read_text().splitlines(True), source.splitlines(True), fromfile=str(parent.relative_to(ROOT)), tofile=str((HERE / 'audit.py').relative_to(ROOT))))
node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'raw_summary')
namespace = {'Counter': Counter}
exec(ast.get_source_segment(source, node), namespace)
summary = namespace['raw_summary']
policy = json.loads((ROOT / 'artifacts/css-attr-fallback-candidate-browser-v2/POLICY.json').read_bytes())
expected = policy['wpt_lanes']['fallback']['expected_subtests']
page = next(iter(expected))
events = [{'action': 'suite_start'}, {'action': 'test_start', 'test': page}]
events += [{'action': 'test_status', 'test': page, 'subtest': name, 'status': 'PASS'} for name in expected[page]]
events += [{'action': 'test_end', 'test': page, 'status': 'OK'}, {'action': 'suite_end'}]
assert summary(events, expected)['all_24_pass']
failed = copy.deepcopy(events)
failed[2]['status'] = 'FAIL'
assert summary(failed, expected)['complete_raw_roster'] and not summary(failed, expected)['all_24_pass']
mutants = []
mutants.append(events[:2] + events[3:])
mutants.append(events[:2] + [events[2]] + events[2:])
mutants.append(events + [{'action': 'crash'}])
wrong = copy.deepcopy(events)
wrong[-2]['test'] = '/wrong.html'
mutants.append(wrong)
mutants.append([events[-1]] + events[:-1])
wrong = copy.deepcopy(events)
wrong[2]['status'] = 'TIMEOUT'
mutants.append(wrong)
assert all(not summary(rows, expected)['complete_raw_roster'] for rows in mutants)
assert not summary([], expected)['complete_raw_roster']
print(json.dumps({'pins': len(binding['references']), 'exact_parent_delta': True, 'pure_raw_positives': 2, 'pure_raw_negatives': len(mutants) + 1, 'owner_terminal_pending': True, 'audit_executed': False}, sort_keys=True))
