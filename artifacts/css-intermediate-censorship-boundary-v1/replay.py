import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
output = parser.parse_args().output.resolve()
assert not output.exists()
inputs = json.loads((HERE / 'INPUTS.json').read_text())
lean = ROOT / inputs['compiler']
assert sha(lean) == inputs['compiler_sha256']
assert sha(HERE / 'Boundary.lean') == inputs['Boundary.lean']
for entry in inputs['dependencies_topological']:
    assert sha(ROOT / entry['path']) == entry['sha256']
assert len(inputs['dependencies_topological']) == 12
output.mkdir()
prelude = '''import Boundary
open CssSemantics CssNumericClipping CssNumericCensorship CssExtendedScalar
open CssSemantics.IntermediateCensorshipBoundary
def bounds : Bounds := ⟨0, 2⟩
def offset : Value := .finite (CssFiniteScalar.source 1)
'''
claims = {
    'nan_offset': 'complete bounds (add .nan offset) = complete bounds (add (censoredLeaf bounds .nan) offset)',
    'nan_zero_offset': 'complete bounds (add (multiply .nan (zero false)) offset) = complete bounds (add (multiply (censoredLeaf bounds .nan) (zero false)) offset)',
    'positive_infinity_zero_offset': 'complete bounds (add (multiply (.infinity false) (zero false)) offset) = complete bounds (add (multiply (censoredLeaf bounds (.infinity false)) (zero false)) offset)',
}
results = []
negative = {}
with tempfile.TemporaryDirectory(prefix='censorship-boundary-replay-') as td:
    work = Path(td)
    env = dict(os.environ, LEAN_NUM_THREADS='2', LEAN_PATH=str(work))
    def run(name, source, product=False):
        args = [str(lean)]
        if product:
            args += ['-o', str(source.with_suffix('.olean'))]
        args += [str(source.relative_to(work))]
        proc = subprocess.run(args, cwd=work, env=env, capture_output=True, text=True, timeout=55)
        log = proc.stdout + proc.stderr
        (output / (name + '.log')).write_text(log)
        return proc.returncode, log
    version = subprocess.run([str(lean), '--version'], capture_output=True, text=True, timeout=10, check=True).stdout
    (output / 'version.log').write_text(version)
    for i, entry in enumerate(inputs['dependencies_topological']):
        source = work / (entry['module'].replace('.', '/') + '.lean')
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes((ROOT / entry['path']).read_bytes())
        code, log = run(f'dependency-{i:02d}', source, True)
        assert code == 0 and 'error:' not in log and 'sorryAx' not in log and 'warning:' not in log, (entry, log)
        results.append({'module': entry['module'], 'source_sha256': entry['sha256'], 'exit': code})
    boundary = work / 'Boundary.lean'
    boundary.write_bytes((HERE / 'Boundary.lean').read_bytes())
    code, log = run('boundary', boundary, True)
    assert code == 0 and log.count('depends on axioms:') == 4 and 'sorryAx' not in log and 'warning:' not in log
    assert log == (HERE / 'lean-final.log').read_text()
    witness = work / 'Witnesses.lean'
    witness.write_text(prelude + '\n'.join('example : ¬ (' + claim + ') := by decide +kernel' for claim in claims.values()) + '\n')
    code, log = run('witnesses', witness)
    assert code == 0 and not log, log
    for name, claim in claims.items():
        source = work / (name + '.lean')
        left, right = claim.split(' = ')
        values = 'theorem values : (' + left + ' = 0) ∧ (' + right + ' = 1) := by decide +kernel\n'
        source.write_text(prelude + '\n' + values + 'example : ' + claim + ' := by\n  rw [values.1, values.2]\n  decide +kernel\n')
        code, log = run(name, source)
        assert code != 0 and 'decide' in log and 'false' in log and 'error:' in log
        assert 'got stuck' not in log and 'failed to reduce' not in log
        assert 'unknown identifier' not in log and 'unexpected token' not in log and 'sorryAx' not in log
        negative[name] = {'claim': claim, 'exit': code, 'concrete_negation_compiled': True}
assert not work.exists()
for entry in inputs['dependencies_topological']:
    assert sha(ROOT / entry['path']) == entry['sha256']
assert sha(HERE / 'Boundary.lean') == inputs['Boundary.lean']
receipt = {'status': 'PASS_CONDITIONAL_MATHEMATICAL_BOUNDARY', 'compiler_sha256': sha(lean), 'dependencies_rebuilt_from_pinned_source': results, 'boundary_sha256': sha(HERE / 'Boundary.lean'), 'named_audits': 4, 'negative_controls': negative, 'threads': 2, 'per_process_timeout_seconds': 55, 'temporary_sources_and_oleans_removed': True, 'canonical_sources_unchanged': True, 'canonical_objects_used': False, 'native_IEEE_or_Stylo_refinement': False, 'canonical_registrations': 0}
(output / 'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
print(json.dumps(receipt, indent=2, sort_keys=True))
