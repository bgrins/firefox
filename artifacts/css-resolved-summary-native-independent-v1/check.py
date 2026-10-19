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
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    freeze = json.loads((ROOT / 'FREEZE.json').read_text())
    assert sha(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    for name, expected in manifest.items():
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT.resolve()) and not path.is_symlink(), name
        assert sha(path) == expected, name
    assert sha(ROOT / 'input/FREEZE.json') == 'dc9453175d210471da6595fe189311d932a8011f4edd2c2265bd89112dd8d0a8'
    assert sha(ROOT / 'input/MANIFEST.json') == 'bff4e313ba82a721da30258b592de2b52a920a9ab7acabf0eaa76536331d27dc'
    for name, expected in json.loads((ROOT / 'draft-read-v1/PINS.json').read_text())['files'].items():
        assert sha(ROOT / 'input' / name) == expected, name
    output = args.output.resolve()
    assert not output.exists()
    result = subprocess.run([sys.executable, str(ROOT / 'input/check.py'), '--output', str(output)],
                            text=True, capture_output=True)
    assert result.returncode == 0, (result.stdout, result.stderr)
    print(json.dumps({'review_files': len(manifest), 'static_replay_exit': result.returncode,
                      'producer_stdout': result.stdout, 'rust_rebuilt': False,
                      'browser_run': False}, indent=2))


if __name__ == '__main__':
    main()
