import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-steps-origin-clamping-model-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
out = parser.parse_args().output.resolve()
assert not out.exists()
plan = read(HERE / 'PLAN.json')
for name, digest in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / name) == digest
for name, pins in plan['changes'].items():
    assert sha(HERE / 'candidate' / name) == pins['after']
    before = HERE / 'original' / name
    assert (sha(before) if before.exists() else None) == pins['before']
old = ast.parse((HERE / 'original/check.py').read_text())
new = ast.parse((HERE / 'candidate/check.py').read_text())
def cases(tree):
    return next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'EXECUTABLE_CASES' for t in n.targets))
old_cases = ast.literal_eval(cases(old).value)
assert ast.literal_eval(cases(new).value) == old_cases + [tuple(x) for x in plan['cases']]
cases(new).value = cases(old).value
assert ast.dump(old) == ast.dump(new)
for name in ['CssSemantics.lean', 'tests/Audit.lean', 'tests/RunExamples.lean', 'README.md', 'ARTIFACT.md', 'research/coverage-map.md']:
    assert (HERE / 'candidate' / name).read_bytes().startswith((HERE / 'original' / name).read_bytes())
source_model = (SOURCE / 'Steps.lean').read_text()
expected_model = source_model.replace('namespace StepsOrigin', 'namespace CssSemantics.StepsOrigin').replace('end StepsOrigin', 'end CssSemantics.StepsOrigin')
assert (HERE / 'candidate/CssSemantics/StepsOrigin.lean').read_text() == expected_model
source_examples = (SOURCE / 'Examples.lean').read_text().split('#print axioms')[0].rstrip() + '\n'
transferred = source_examples.replace('import Steps', 'import CssSemantics.StepsOrigin').replace('open StepsOrigin', 'open CssSemantics.StepsOrigin')
examples = (HERE / 'candidate/CssSemantics/StepsOriginExamples.lean').read_text()
assert examples.startswith(transferred)
assert len(re.findall(r'^example :', examples, re.M)) == 11
assert all('decide (' + claim + ')' in examples for claim in plan['claims'])
named = ['CssSemantics.StepsOrigin.' + n for n in re.findall(r'^theorem (\S+)', source_model, re.M)]
assert set(named) == set(plan['audits']) and len(named) == 10
audit_before = re.findall(r'#print axioms (\S+)', (HERE / 'original/tests/Audit.lean').read_text())
audit_after = re.findall(r'#print axioms (\S+)', (HERE / 'candidate/tests/Audit.lean').read_text())
assert audit_after == audit_before + plan['audits'] and not set(named) & set(audit_before)
report = read(HERE / 'previous-report.json')
assert sha(HERE / 'previous-report.json') == plan['base_report_sha256']
assert set(audit_before) == set(report['declaration_axioms']) and len(audit_before) == 11830
assert old_cases == [(r['name'], r['result']) for r in report['executable_cases']]
assert len(report['source_sha256']) == 2153 and sum(not x[1] for x in old_cases) == 170
assert 'coverage.json' not in plan['changes']
for name in plan['existing']:
    assert plan['existing'][name] + plan['delta'][name] == plan['intended'][name]
inputs = read(HERE / 'INPUTS.json')
compiler = ROOT / inputs['compiler']
assert sha(compiler) == inputs['compiler_sha256']
imports = read(HERE / 'IMPORT-PINS.json')
for name, digest in imports.items():
    assert sha(ROOT / name) == digest
out.mkdir()
commands = []
def run(command, cwd, env=None):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=90)
    commands.append({'command': command, 'exit': result.returncode,
                     'stdout': result.stdout, 'stderr': result.stderr})
    return result.returncode, result.stdout + result.stderr
with tempfile.TemporaryDirectory(prefix='steps-library-transport-', dir='/private/tmp') as td:
    scratch = Path(td)
    shutil.copytree(HERE / 'original', scratch, dirs_exist_ok=True)
    for reverse in (False, True):
        code, log = run(['patch', '--batch', '-p1', '-i', str(HERE / 'library.patch')] + (['-R'] if reverse else []), scratch)
        assert code == 0, log
        for name, pins in plan['changes'].items():
            expected = pins['before' if reverse else 'after']
            assert (sha(scratch / name) if (scratch / name).exists() else None) == expected
assert not scratch.exists()
expected_negative = read(HERE / 'EXPECTED-LOGS.json')
gate_negatives = 0
for name, log in expected_negative.items():
    def rejected(exit, output):
        return exit == 1 and output == log
    assert rejected(1, log) and log.endswith('is false\n')
    for exit, bad in [(0, log), (2, log), (1, log + 'extra error\n'),
                      (1, 'error: unknown identifier missing\n'),
                      (1, 'error: Tactic `decide` failed to reduce the proposition to true or false\n'),
                      (1, (SOURCE / 'author-replay/calculation-rejected.log').read_text()),
                      (1, log.replace('some 2', 'some 3'))]:
        assert not rejected(exit, bad)
        gate_negatives += 1
with tempfile.TemporaryDirectory(prefix='steps-library-lean-', dir='/private/tmp') as td:
    scratch = Path(td)
    shutil.copytree(HERE / 'candidate/CssSemantics', scratch / 'CssSemantics')
    for name in imports:
        if name.endswith('.olean'):
            original = ROOT / name
            shutil.copyfile(original, scratch / 'CssSemantics' / original.name)
    env = dict(os.environ, LEAN_PATH=str(scratch) + ':' + str(ROOT / inputs['canonical_olean_root']))
    for name in ['StepsOrigin', 'StepsOriginExamples']:
        code, log = run([str(compiler), '-j1', '-o', 'CssSemantics/' + name + '.olean', 'CssSemantics/' + name + '.lean'], scratch, env)
        (out / (name + '.log')).write_text(log)
        assert code == 0 and not log, log
    (scratch / 'Audit.lean').write_text('import CssSemantics.StepsOriginExamples\n' + '\n'.join('#print axioms ' + n for n in plan['audits']) + '\n')
    code, log = run([str(compiler), '-j1', 'Audit.lean'], scratch, env)
    (out / 'audits.log').write_text(log)
    expected_audit = (SOURCE / 'replay-final/positive.log').read_text().replace('StepsOrigin.', 'CssSemantics.StepsOrigin.')
    assert code == 0 and log == expected_audit and 'sorryAx' not in log, log
    (scratch / 'Run.lean').write_text('import CssSemantics.StepsOriginExamples\ndef main : IO Unit := do\n  for (name, accepted) in CssSemantics.StepsOrigin.Examples.checks do\n    IO.println s!"PASS {name}: {accepted}"\n')
    code, log = run([str(compiler), '-j1', '--run', 'Run.lean'], scratch, env)
    (out / 'cases.log').write_text(log)
    assert code == 0 and log.splitlines() == [f'PASS {n}: {str(v).lower()}' for n, v in plan['cases']], log
    for name, expected in expected_negative.items():
        shutil.copyfile(HERE / 'false' / (name + '.lean'), scratch / (name + '.lean'))
        code, log = run([str(compiler), '-j1', name + '.lean'], scratch, env)
        (out / (name + '.log')).write_text(log)
        assert code == 1 and log == expected, log
assert not scratch.exists()
for name, digest in imports.items():
    assert sha(ROOT / name) == digest
assert sha(compiler) == inputs['compiler_sha256']
result = {'status': 'STEPS_ORIGIN_LIBRARY_PROPOSAL_CHECK_PASS', 'audits': 10,
          'positive_proof_examples': 11, 'executable_cases': 14, 'false_controls': 3,
          'negative_gate_checks': gate_negatives, 'old_case_audit_prefixes_preserved': True,
          'checker_AST_only_case_append': True, 'proof_bodies_unchanged': True,
          'scratch_removed': True, 'canonical_mutation': False, 'full_canonical_check': False,
          'new_proof_discovery_credit': 0, 'normative_coverage_increment': 0, 'commands': commands}
(out / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS: 10 transferred audits, 11 proof examples, 14 observations, 3 decisive false controls; shared library untouched')
