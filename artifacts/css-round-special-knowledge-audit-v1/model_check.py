import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output
    out.mkdir(exist_ok=False)
    lean = HERE.parents[1] / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
    original = json.loads((HERE / 'MODEL-CHECK.json').read_text())
    assert hashlib.sha256(lean.read_bytes()).hexdigest() == original['lean_sha256']
    with tempfile.TemporaryDirectory(prefix='round-knowledge-replay-') as tmp:
        root = Path(tmp)
        (root / 'Knowledge.lean').write_bytes((HERE / 'Knowledge.lean').read_bytes())
        env = dict(os.environ, LEAN_PATH=str(root))
        run = subprocess.run([str(lean), '-j', '2', '-o', str(root / 'Knowledge.olean'),
                              str(root / 'Knowledge.lean')], cwd=root, env=env, capture_output=True, text=True)
        assert run.returncode == 0
        (out / 'lean.log').write_text(run.stdout + run.stderr)
        assert (out / 'lean.log').read_bytes() == (HERE / 'lean.log').read_bytes()
        results = []
        for control in original['false_claims']:
            path = root / (control['name'] + '.lean')
            path.write_text(control['source'])
            run = subprocess.run([str(lean), '-j', '2', str(path)], cwd=root, env=env, capture_output=True, text=True)
            assert run.returncode != 0 and 'false' in run.stdout
            results.append({'name': control['name'], 'exit': run.returncode})
    (out / 'CHECK.json').write_text(json.dumps({'core_exit': 0, 'negative_controls': results,
        'owned_compiler_products_removed': True, 'native_refinement_claim': False}, indent=2) + '\n')


if __name__ == '__main__':
    main()
