import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(LEAN) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
assert len(sys.argv) == 2 and Path(sys.argv[1]).name == sys.argv[1]
out = HERE / sys.argv[1]
out.mkdir()
names = re.findall(r'^theorem (\w+)', (HERE / 'Dag.lean').read_text(), re.M)
false_cases = {
    'EmptyMeansConsistent': 'Consistent diamond discarded',
    'TwoRoundsCompleteDiamond': 'Ready (run diamond 2 diamondInitial)',
    'RuleEditNeedsNoAdmission': 'Covered editedDiamond settled',
    'OneRoundEvaluatesWholeDiamond': 'observed (run editedDiamond 1 incremental) = [4, 12, 5, 17]',
    'FirstDependencyNotificationSuffices': 'Covered branchEdit (firstDependencyOnly branchEdit branchAdmission)',
    'SecondInputIrrelevant': 'diamond.rule 3 [6, 0] = 9',
}
(out / 'TOOLCHAIN.txt').write_bytes(subprocess.check_output([str(LEAN), '--version']))
commands = []
with tempfile.TemporaryDirectory(prefix='css-dag-completion-') as temporary:
    scratch = Path(temporary)
    env = dict(os.environ, LEAN_PATH=str(scratch))
    (out / 'SCRATCH.json').write_text(json.dumps({'path': temporary}) + '\n')
    shutil.copyfile(HERE / 'Dag.lean', scratch / 'Dag.lean')
    (scratch / 'Audit.lean').write_text('import Dag\n' + ''.join('#print axioms Dag.' + n + '\n' for n in names))
    for name, claim in false_cases.items():
        (scratch / (name + '.lean')).write_text(
            'import Dag\nopen Dag\nexample : ' + claim +
            ' := by\n  simp only [Ready, Consistent, Covered]\n  decide\n'
            if name not in ('OneRoundEvaluatesWholeDiamond', 'SecondInputIrrelevant') else
            'import Dag\nopen Dag\nexample : ' + claim + ' := by decide\n')
    for source in scratch.glob('*.lean'):
        shutil.copyfile(source, out / source.name)
    for name, expected in [('Dag', True), ('Audit', True)] + [(n, False) for n in false_cases]:
        result = subprocess.run([str(LEAN), '-o', name + '.olean', name + '.lean'],
                                cwd=scratch, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=60)
        (out / (name + '.log')).write_bytes(result.stdout)
        commands.append({'module': name, 'exit': result.returncode, 'expected_success': expected})
        (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
        assert (result.returncode == 0) == expected, (name, result.stdout.decode())
        if not expected:
            assert b'Tactic `decide` proved that the proposition' in result.stdout and b'is false' in result.stdout
    audit = (out / 'Audit.log').read_text()
    assert audit.count('depends on axioms:') + audit.count('does not depend on any axioms') == len(names)
    axioms = {n.strip() for group in re.findall(r'axioms: \[(.*?)\]', audit) for n in group.split(',') if n.strip()}
    assert axioms <= {'propext', 'Quot.sound', 'Classical.choice'}
    assert 'sorryAx' not in audit and 'Lean.ofReduceBool' not in audit
assert not scratch.exists()
(out / 'CHECK.json').write_text(json.dumps({
    'audited_theorems': names, 'false_controls_rejected': len(false_cases),
    'source_sha256': sha(HERE / 'Dag.lean'), 'scratch_removed': True,
    'native_refinement': False, 'canonical_coverage_increment': 0,
}, indent=2) + '\n')
print(len(names), 'audits;', len(false_cases), 'false controls rejected; scratch removed')
