#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument('--replay', action='store_true')
p.add_argument('--output', type=Path)
p.add_argument('--lean', type=Path, default=Path('/Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'))
a = p.parse_args()
root = Path(__file__).resolve().parent
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
freeze = json.loads((root / 'FREEZE.json').read_text())
assert sha(root / 'MANIFEST.json') == freeze['manifest_sha256']
manifest = json.loads((root / 'MANIFEST.json').read_text())
for name, digest in manifest.items():
    file = root / name
    assert not file.is_symlink() and file.is_file() and sha(file) == digest, name
assert sha(root / 'input/FREEZE.json') == 'fb3e9cc30c276a3cce92324666aa078fbaefb4656e21ca942ffd6396013c88f1'
assert sha(root / 'input/MANIFEST.json') == '8c804f1ea9d82b91b186f2dacd94a5a08b153d5e3e10c8ffffaaceccb8422d2b'
result = json.loads((root / 'evidence/RESULT.json').read_text())
assert result['status'] == 'PASS' and result['theorem_audits'] == 158 and result['new_theorem_audits'] == 28
if a.replay:
    assert a.output is not None and not a.output.exists()
    subprocess.run([sys.executable, str(root / 'input/check.py'), '--lean', str(a.lean.resolve()), '--output', str(a.output.resolve())], check=True)
print(json.dumps({'authenticated': len(manifest), 'scope': 'conditional lexical transfer; numerical and whole-tokenizer correctness remain open', 'replayed': a.replay}))
