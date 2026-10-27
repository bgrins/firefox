import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    out = ap.parse_args().output.resolve()
    out.mkdir(exist_ok=False)
    inputs = json.loads((P / 'INPUTS.json').read_text())
    lean = ROOT / inputs['lean']
    assert sha(lean) == inputs['lean_sha256']
    for name, digest in inputs['modules'].items():
        assert sha(P / name) == digest
    for rel, digest in json.loads((P / 'REFERENCES.json').read_text()).items():
        manifest = ROOT / rel
        assert sha(manifest) == digest
        for name, expected in json.loads(manifest.read_text()).items():
            assert sha(manifest.parent / name) == expected
    negatives = [
        ('inline-export-admitted-box', 'exportWith inlineGet boxedOne 1 = some true'),
        ('resolve-only-infinite-peer', 'exportWith resolve lowerDeferred 0 = some false'),
        ('skip-finite-validation', 'admitted upperDeferred = true'),
        ('exclusive-endpoint', 'member ⟨.finite 1, .finite 3⟩ 3 = false'),
    ]
    exits = {}
    with tempfile.TemporaryDirectory(prefix='counter-range-representation-') as temp:
        temp = Path(temp)
        for name in inputs['modules']:
            (temp / name).write_bytes((P / name).read_bytes())
        env = {**os.environ, 'LEAN_PATH': str(temp), 'LEAN_NUM_THREADS': '2'}
        for name, count in [('Range', 8), ('Examples', 0)]:
            run = subprocess.run([str(lean), '-o', name + '.olean', name + '.lean'], cwd=temp,
                env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
            (out / (name + '.log')).write_text(run.stdout)
            assert run.returncode == 0, run.stdout
            lines = run.stdout.splitlines()
            assert len(lines) == count and 'sorryAx' not in run.stdout
            assert all(line.endswith(('depends on axioms: [propext]',
                'depends on axioms: [propext, Quot.sound]',
                'depends on axioms: [propext, Classical.choice, Quot.sound]')) for line in lines)
            exits[name] = run.returncode
        for name, claim in negatives:
            source = 'import Examples\nopen CounterRangeRepresentation\nexample : ' + claim + ' := by decide +kernel\n'
            (temp / 'Negative.lean').write_text(source)
            (out / (name + '.lean.txt')).write_text(source)
            run = subprocess.run([str(lean), 'Negative.lean'], cwd=temp, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
            (out / (name + '.log')).write_text(run.stdout)
            assert run.returncode != 0 and 'Tactic `decide` proved that the proposition' in run.stdout and 'is false' in run.stdout, run.stdout
            assert 'unknown' not in run.stdout.lower() and 'unexpected token' not in run.stdout
            exits[name] = run.returncode
    receipt = {'status': 'PASS', 'exits': exits, 'threads': 2,
        'audited_results': 8, 'of_which_representation_fact': 1,
        'anonymous_examples': 14, 'false_claims_rejected': 4,
        'imported_project_results': 0, 'canonical_registrations': 0,
        'native_refinement': False, 'native_compilation': False, 'browser_executed': False,
        'temporary_products_removed': True,
        'admission_scope': 'Implementation publication invariant, not normative rejection of every unresolved CSS expression'}
    (out / 'CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
