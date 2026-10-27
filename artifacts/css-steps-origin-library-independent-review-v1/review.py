import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
P = ROOT / 'artifacts/css-steps-origin-library-proposal-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
manifest = read(P / 'FILES.json')
for name, digest in manifest.items():
    assert sha(P / name) == digest, name
for name, digest in read(P / 'REFERENCES.json').items():
    assert sha(ROOT / name) == digest, name
plan = read(P / 'PLAN.json')
report = read(P / 'previous-report.json')
assert sha(P / 'previous-report.json') == plan['base_report_sha256']
for name, pins in plan['changes'].items():
    assert sha(P / 'candidate' / name) == pins['after']
    old = P / 'original' / name
    assert (sha(old) if old.exists() else None) == pins['before']
    live = ROOT / 'artifacts/css-spec-lean' / name
    assert (sha(live) if live.exists() else None) == pins['before'], name
    if old.exists() and name != 'check.py':
        assert (P / 'candidate' / name).read_bytes().startswith(old.read_bytes())
assert 'coverage.json' not in plan['changes']
coverage = ROOT / 'artifacts/css-spec-lean/coverage.json'
assert sha(coverage) == report['source_sha256']['coverage.json']
old, new = [ast.parse((P / branch / 'check.py').read_text()) for branch in ['original', 'candidate']]
def cases(tree):
    return next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'EXECUTABLE_CASES' for t in n.targets))
old_cases = ast.literal_eval(cases(old).value)
assert old_cases == [(r['name'], r['result']) for r in report['executable_cases']]
assert ast.literal_eval(cases(new).value) == old_cases + [tuple(x) for x in plan['cases']]
cases(new).value = cases(old).value
assert ast.dump(old) == ast.dump(new)
audit = lambda branch: re.findall(r'#print axioms (\S+)', (P / branch / 'tests/Audit.lean').read_text())
assert audit('candidate') == audit('original') + plan['audits']
assert set(audit('original')) == set(report['declaration_axioms'])
assert len(audit('original')) == 11830 and len(old_cases) == 12424
assert sum(not value for _, value in old_cases) == 170
assert len(report['source_sha256']) == 2153
source = ROOT / 'artifacts/css-steps-origin-clamping-model-v1'
model = (source / 'Steps.lean').read_text()
assert (P / 'candidate/CssSemantics/StepsOrigin.lean').read_text() == model.replace('namespace StepsOrigin', 'namespace CssSemantics.StepsOrigin').replace('end StepsOrigin', 'end CssSemantics.StepsOrigin')
examples = (source / 'Examples.lean').read_text().split('#print axioms')[0].rstrip() + '\n'
assert (P / 'candidate/CssSemantics/StepsOriginExamples.lean').read_text().startswith(examples.replace('import Steps', 'import CssSemantics.StepsOrigin').replace('open StepsOrigin', 'open CssSemantics.StepsOrigin'))
replay = read(P / 'replay/CHECK.json')
assert [c['exit'] for c in replay['commands']] == [0, 0, 0, 0, 0, 0, 1, 1, 1]
for name, command in zip(['StepsOrigin', 'StepsOriginExamples', 'audits', 'cases', 'calculation-rejected', 'literal-clamped', 'unresolved-admitted'], replay['commands'][2:]):
    assert (P / 'replay' / (name + '.log')).read_text() == command['stdout'] + command['stderr']
assert (P / 'replay/cases.log').read_text().splitlines() == [f'PASS {n}: {str(v).lower()}' for n, v in plan['cases']]
axioms = (P / 'replay/audits.log').read_text()
assert re.findall(r"^'([^']+)'", axioms, re.M) == plan['audits']
assert set(re.findall(r'\[([^]]*)\]', axioms)) <= {'propext, Quot.sound', 'propext, Classical.choice, Quot.sound'}
assert not any(x in axioms for x in ['sorryAx', 'ofReduceBool'])
for name, expected in read(P / 'EXPECTED-LOGS.json').items():
    assert (P / 'replay' / (name + '.log')).read_text() == expected
    assert expected.endswith('is false\n') and expected.count('error:') == 1
    assert 'proved that the proposition' in expected
    assert 'failed to reduce' not in expected
    for bad in [expected + 'warning: extra\n', expected + 'error: extra\n', expected.replace('some 2', 'some 3'), (P / 'replay-initial/StepsOrigin.log').read_text(), 'error: Tactic `decide` failed to reduce the proposition to true or false\n']:
        assert bad != expected
for name, digest in read(P / 'IMPORT-PINS.json').items():
    assert sha(ROOT / name) == digest
inputs = read(P / 'INPUTS.json')
assert sha(ROOT / inputs['compiler']) == inputs['compiler_sha256']
transport = []
with tempfile.TemporaryDirectory(prefix='steps-origin-independent-', dir='/private/tmp') as td:
    scratch = Path(td)
    shutil.copytree(P / 'original', scratch, dirs_exist_ok=True)
    for reverse in [False, True]:
        command = ['patch', '--batch', '-p1', '-i', str(P / 'library.patch')] + (['-R'] if reverse else [])
        result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
        transport.append({'command': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        assert result.returncode == 0
        for name, pins in plan['changes'].items():
            path = scratch / name
            assert (sha(path) if path.exists() else None) == pins['before' if reverse else 'after']
assert not scratch.exists()
result = {'status': 'STEPS_ORIGIN_LIBRARY_INDEPENDENT_REVIEW_GO', 'proposal_manifest_sha256': sha(P / 'FILES.json'), 'authenticated_payloads': len(manifest), 'changed_paths': len(plan['changes']), 'old_audits': 11830, 'old_cases': 12424, 'added_audits': 10, 'added_cases': 14, 'added_false_cases': 3, 'checker_AST_only_case_append': True, 'old_prefixes_exact': True, 'coverage_unchanged': True, 'proof_transfer_exact': True, 'decisive_false_controls': 3, 'retained_focused_execution': read(P / 'EXECUTION.json'), 'compiler_invoked_by_review': False, 'full_canonical_check': False, 'canonical_mutation': False, 'scratch_removed': True, 'transport': transport}
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'transport'}, indent=2))
