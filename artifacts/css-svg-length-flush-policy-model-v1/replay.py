import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    return json.loads(path.read_text())

inputs = read(HERE / 'INPUTS.json')
for name, digest in inputs['pins'].items():
    assert sha(ROOT / name) == digest, name
for name, digest in read(HERE / 'INPUT-FILES.json').items():
    assert sha(HERE / name) == digest, name
out = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else HERE / 'replay'
out.mkdir(exist_ok=False)
environment = {**os.environ, 'LEAN_NUM_THREADS': '2', 'LEAN_PATH': str(ROOT / inputs['library_objects'])}
compiler = ROOT / inputs['compiler']
source = (HERE / 'FlushPolicy.lean').read_text()
names = read(HERE / 'AUDIT-NAMES.json')
allowed = {'propext', 'Classical.choice', 'Quot.sound'}
result = subprocess.run([str(compiler), str(HERE / 'FlushPolicy.lean')], cwd=ROOT,
                        env=environment, capture_output=True, text=True, timeout=60)
log = result.stdout + result.stderr
(out / 'lean.log').write_text(log)
assert result.returncode == 0 and 'error:' not in log and 'sorryAx' not in log
matches = re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])", log)
assert [name for name, _ in matches] == names
audit = {name: [a.strip() for a in axioms.split(',') if a.strip()] for name, axioms in matches}
assert all(set(axioms) <= allowed for axioms in audit.values())
negative = {
    'same-tier-is-identity': 'example : request .em .ex = .none := by decide +kernel',
    'style-covers-percentage': 'example : Sufficient .px .percentage .style := by unfold Sufficient; decide +kernel',
    'source-only-preserves': 'example : Preserves (basis fresh) ⟨.px, 100⟩ .percentage ⟨.percentage, 50⟩ := by unfold Preserves; decide +kernel',
    'selection-alone-completes': 'example : run incompleteForce basis stale ⟨.px, 100⟩ .percentage = some (fresh, ⟨.percentage, 25⟩) := by decide +kernel',
}
rejected = {}
for name, claim in negative.items():
    path = out / (name + '.lean')
    try:
        path.write_text(source + '\nopen SvgLengthFlushPolicy CssSemantics.UnitConversion\n' + claim + '\n')
        failed = subprocess.run([str(compiler), str(path)], cwd=ROOT, env=environment,
                                capture_output=True, text=True, timeout=60)
        output = failed.stdout + failed.stderr
        (out / (name + '.log')).write_text(output)
        assert failed.returncode != 0 and 'error:' in output and 'false' in output and 'decide' in output
        assert 'unknown identifier' not in output and 'unknown module' not in output
        rejected[name] = {'exit': failed.returncode, 'false_claim_rejected': True}
    finally:
        path.unlink(missing_ok=True)
assert not list(out.glob('*.lean')) and not list(out.glob('*.olean'))
for name, digest in inputs['pins'].items():
    assert sha(ROOT / name) == digest, name
summary = {'status': 'PASS', 'positive_exit': result.returncode, 'audited_theorems': len(audit),
           'axioms': audit, 'negative_claims': rejected, 'threads': 2,
           'source_sha256': sha(HERE / 'FlushPolicy.lean'), 'compiler_sha256': sha(compiler),
           'imported_library_unchanged': True, 'native_inputs_unchanged': True,
           'new_target_directory': False, 'owned_temporary_sources_removed': True}
(out / 'CHECK.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'axioms'}, indent=2))
