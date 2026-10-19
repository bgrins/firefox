import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
if digest(root / 'MANIFEST.json') != args.manifest_sha:
    raise SystemExit('Manifest authentication failed')
manifest = json.loads((root / 'MANIFEST.json').read_text())
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
if actual != set(manifest['files']) | {'MANIFEST.json', 'FREEZE.json'}:
    raise SystemExit('Inventory mismatch')
for name, expected in manifest['files'].items():
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise SystemExit('Unsafe path')
    if digest(path) != expected:
        raise SystemExit('Input authentication failed: ' + name)
freeze = json.loads((root / 'FREEZE.json').read_text())
assert freeze['manifest_sha256'] == args.manifest_sha
package = root / 'candidate-package'
assert digest(package / 'MANIFEST.json') == '8814399049cbf897b2dfb226cfd7f8fba74090eafd13c64f74c89736b2a8fd90'
assert digest(package / 'check.py') == '0eeb97fc8b41780ecbb9ca1938341094d0f6929b3f13b8f44eb2b22ee63d8ec0'
tool = json.loads((package / 'TOOLCHAIN.json').read_text())
assert digest(Path(sys.executable).resolve()) == tool['python_sha256']
subprocess.run([sys.executable, '-I', '-S', '-B', str(package / 'check.py'),
                '--manifest-sha', '8814399049cbf897b2dfb226cfd7f8fba74090eafd13c64f74c89736b2a8fd90'], check=True)

originals = json.loads((root / 'LIVE-ORIGINALS.json').read_text())
assert len(originals) == 16 and all(r['equal'] and r['original_sha'] == r['live_sha'] for r in originals)
context = json.loads((root / 'LIVE-CONTEXT.json').read_text())
assert [r['path'] for r in context if not r['equal']] == ['servo/ports/geckolib/glue.rs']
old = (package / 'context/servo/ports/geckolib/glue.rs').read_text()
new = (root / 'live-context/servo/ports/geckolib/glue.rs').read_text()
for row in json.loads((root / 'GLUE-COMPARISON.json').read_text()):
    def body(text):
        start = text.index('fn ' + row['function'] + '(')
        return text[start:text.index('\n}', start) + 2]
    assert body(old) == body(new)
    assert hashlib.sha256(body(old).encode()).hexdigest() == row['sha256']

face = (package / 'candidate/layout/style/FontFaceImpl.cpp').read_text()
for name in ['Family', 'Style', 'Weight', 'Width', 'UnicodeRange',
             'FeatureSettings', 'VariationSettings', 'Display',
             'AscentOverride', 'DescentOverride', 'LineGapOverride', 'SizeAdjust']:
    start = face.index('void FontFaceImpl::Set' + name + '(')
    body = face[start:face.index('\n}', start) + 2]
    assert 'if (SetDescriptor(' in body and 'DescriptorUpdated();' in body
assert '[self = RefPtr{impl}, status] { self->SetStatus(status); }' in face
assert 'SetUserFontEntry(entry, false);' in face
print(json.dumps({'status': 'SOURCE_REPLAY_PASS', 'files': len(manifest['files']),
                  'recorded_live_original_matches': 16, 'descriptor_callers': 12,
                  'native_compilation': False, 'browser_execution': False}))
