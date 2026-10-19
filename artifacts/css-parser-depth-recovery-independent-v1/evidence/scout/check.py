import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

args = argparse.ArgumentParser()
args.add_argument('--output', type=Path)
options = args.parse_args()
freeze = json.loads((ROOT / 'FREEZE.json').read_text())
assert digest(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
for name, expected in manifest.items():
    path = ROOT / name
    assert path.is_file() and not path.is_symlink(), name
    assert digest(path) == expected, name
assert digest(ROOT / 'check.py') == freeze['checker_sha256']
for name, expected in json.loads((ROOT / 'SOURCE-PINS.json').read_text()).items():
    assert digest(ROOT / 'source' / name) == expected, name
for name in ['parser.rs', 'tokenizer.rs', 'rules_and_declarations.rs']:
    assert (ROOT / 'source/third_party/rust/cssparser/src' / name).read_bytes() == (ROOT / 'vendor/cssparser/src' / name).read_bytes()
print(f'Authenticated {len(manifest)} files before helper execution', flush=True)
if options.output is None:
    sys.exit(0)
out = options.output.resolve()
out.mkdir(parents=True, exist_ok=False)
config = json.loads((ROOT / 'TOOLCHAIN.json').read_text())
for tool in ['rustc', 'node']:
    assert digest(Path(config[tool])) == config[tool + '_sha256']
commands = []
def run(cmd):
    result = subprocess.run(cmd, cwd=out, capture_output=True, text=True)
    commands.append({'command': cmd, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    (out / 'CHECK-COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert result.returncode == 0, result.stderr

run([sys.executable, str(ROOT / 'native/build.py'), '--output', str(out / 'native')])
actual = [json.loads(line) for line in (out / 'native/OBSERVATIONS.jsonl').read_text().splitlines()]
expected = [json.loads(line) for line in (ROOT / 'evidence/OBSERVATIONS.jsonl').read_text().splitlines()]
assert actual == expected and len(actual) == 16
for name in ['depth-limit-recovery.html', 'depth-limit-padding-recovery.html']:
    text = (ROOT / name).read_text()
    script = re.findall(r'<script>(.*?)</script>', text, re.S)
    assert len(script) == 1
    assert '["inline", "stylesheet"]' in script[0] and '[1, 74, 75, 76]' in script[0]
    js = out / (name + '.js')
    js.write_text(script[0])
    run([config['node'], '--check', str(js)])
assert (ROOT / 'depth-limit-recovery.html').read_text().replace('width:', 'padding-left:') == (ROOT / 'depth-limit-padding-recovery.html').read_text()
(out / 'CHECK.json').write_text(json.dumps({'authenticated_files': len(manifest), 'native_rows': 16, 'browser_probes': 'UNEXECUTED', 'syntax_checked_cases_per_file': 10}, indent=2) + '\n')
print('PASS: 16 source-only observations; two unexecuted probes syntax checked')
