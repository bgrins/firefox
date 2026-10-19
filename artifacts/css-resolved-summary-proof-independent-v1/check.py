#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    frozen = json.loads((ROOT / 'FREEZE.json').read_text())
    assert sha(ROOT / 'MANIFEST.json') == frozen['manifest_sha256']
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    for name, expected in manifest.items():
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT.resolve()), name
        assert sha(path) == expected, name
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    stages = []
    for script, directory in [('input/replay.py', 'proof'), ('primitive-control.py', 'primitive-control')]:
        result = subprocess.run([sys.executable, str(ROOT / script), '--lean', str(args.lean.resolve()),
                                 '--output', str(output / directory)], text=True, capture_output=True)
        (output / (directory + '.log')).write_text(result.stdout + result.stderr)
        assert result.returncode == 0, (script, result.stdout, result.stderr)
        stages.append({'script': script, 'exit': result.returncode})
    result = {'authenticated_files': len(manifest), 'stages': stages,
              'scope': 'conditional selected-token composition; native admission remains open'}
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
