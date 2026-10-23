import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S verify.py EXPECTED_FILES_SHA256')
sys.dont_write_bytecode = True
import ast
import hashlib
import json
from pathlib import Path
import stat

root = Path(__file__).resolve().parent
def require(value, label):
    if not value:
        raise RuntimeError(label)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
require(len(sys.argv) == 2 and sha(root / 'FILES.json') == sys.argv[1], 'EXTERNAL_PIN')
files = json.loads((root / 'FILES.json').read_text())['files']
seen_files, seen_dirs = set(), set()
for p in root.rglob('*'):
    mode = p.lstat().st_mode
    name = str(p.relative_to(root))
    if stat.S_ISDIR(mode):
        seen_dirs.add(name)
    else:
        require(stat.S_ISREG(mode), 'NONREGULAR')
        seen_files.add(name)
dirs = {str(p) for n in files for p in Path(n).parents if str(p) != '.'}
require(seen_files == set(files) | {'FILES.json'} and seen_dirs == dirs, 'ROSTER')
for n, h in files.items():
    require(sha(root / n) == h, 'HASH:' + n)
preflight = json.loads((root / 'FINAL-PREFLIGHT.json').read_text())
for n, h in preflight['external_pins'].items():
    require(sha(root / ('final-' + n)) == h, 'FINAL_EXTERNAL:' + n)
inputs = json.loads((root / 'final-INPUTS.json').read_text())
config = json.loads((root / 'final-CONFIG.json').read_text())
require(sha(root / 'final-CONFIG.json') == inputs['payload_pins']['CONFIG.json'], 'CONFIG_PIN')
for n in ['experiment.py', 'run_wpt.py']:
    ast.parse((root / ('final-' + n)).read_text())
    require(sha(root / ('final-' + n)) == inputs['payload_pins'][n], 'SCRIPT_PIN')
roster = json.loads((root / 'ROSTER-CHECK.json').read_text())
require(roster['exact_ordered_equality'] and roster['total'] == 124, 'ROSTER_COUNTS')
for name, names in roster['independently_reconstructed_from_source_loops'].items():
    require(names == config['expected_new_subtests']['/css/css-contain/content-visibility/' + name], 'NAMES')
    require(sha(root / 'tests' / name) == inputs['payload_pins']['tests/' + name], 'TEST_PIN')
require(preflight['outcome'] == 'FINAL_READONLY_PREFLIGHT_PASS', 'PREFLIGHT')
print(json.dumps({'verdict': 'GO_REVERSIBLE_DIAGNOSTIC_ONLY', 'payloads': len(files),
                  'new_subtests': 124, 'native_source_pairs': 20, 'tests': 15}))
