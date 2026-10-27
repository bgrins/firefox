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
    for rel, digest in json.loads((P / 'REFERENCES.json').read_text()).items():
        m = ROOT / rel
        assert sha(m) == digest
        for n, d in json.loads(m.read_text()).items():
            assert sha(m.parent / n) == d
    assert (P / 'Range.lean').read_bytes() == (ROOT / 'artifacts/css-counter-range-representation-model-v1/Range.lean').read_bytes()
    for n, d in inputs['modules'].items():
        assert sha(P / n) == d
    with tempfile.TemporaryDirectory(prefix='additive-order-lean-') as t:
        t = Path(t)
        env = {**os.environ, 'LEAN_PATH': str(t), 'LEAN_NUM_THREADS': '2'}
        for n in inputs['modules']:
            (t / n).write_bytes((P / n).read_bytes())
        for n, count in [('Range', 8), ('Ordering', 3)]:
            r = subprocess.run([str(lean), '-o', n + '.olean', n + '.lean'], cwd=t, env=env, capture_output=True, text=True, timeout=60)
            (out / (n + '.log')).write_text(r.stdout + r.stderr)
            assert r.returncode == 0 and not r.stderr and 'sorryAx' not in r.stdout, r.stdout + r.stderr
            assert len(r.stdout.splitlines()) == count
        for name, claim in [
            ('boxed-first-old', 'inlineGreater (.boxedResolved 3) (.inline 1) = true'),
            ('boxed-second-old', 'inlineGreater (.inline 1) (.boxedResolved 3) = false'),
            ('clamp-invisible', 'resolvedOrder [.boxedResolved (-1), .boxedResolved (-2)] = resolvedOrder [.boxedResolved 0, .boxedResolved 0]')]:
            source = 'import Ordering\nopen AdditiveOrder CounterRangeRepresentation\nexample : ' + claim + ' := by decide +kernel\n'
            (t / 'Negative.lean').write_text(source)
            (out / (name + '.lean.txt')).write_text(source)
            r = subprocess.run([str(lean), 'Negative.lean'], cwd=t, env=env, capture_output=True, text=True, timeout=60)
            log = r.stdout + r.stderr
            (out / (name + '.log')).write_text(log)
            assert r.returncode != 0 and 'Tactic `decide` proved that the proposition' in log and 'is false' in log
    check = {'status': 'PASS', 'new_general_results': 3, 'reused_results_not_new': 8,
        'anonymous_controls': 8, 'false_claims_rejected': 3, 'threads': 2,
        'native_refinement': False, 'canonical_registrations': 0, 'temporary_products_removed': True}
    (out / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
    print(json.dumps(check, indent=2))


if __name__ == '__main__':
    main()
