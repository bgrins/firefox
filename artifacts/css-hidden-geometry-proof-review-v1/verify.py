import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S verify.py EXPECTED_FILES_SHA256')
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import re
import stat

root = Path(__file__).resolve().parent
def require(value, reason):
    if not value:
        raise RuntimeError(reason)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    return json.loads(path.read_text())
def closed(directory, files, seals):
    expected = set(files) | set(seals)
    dirs = {str(p) for n in expected for p in Path(n).parents if str(p) != '.'}
    seen_files, seen_dirs = set(), set()
    for p in directory.rglob('*'):
        mode = p.lstat().st_mode
        name = str(p.relative_to(directory))
        if stat.S_ISDIR(mode):
            seen_dirs.add(name)
        else:
            require(stat.S_ISREG(mode), 'NONREGULAR:' + name)
            seen_files.add(name)
    require(seen_files == expected and seen_dirs == dirs, 'CLOSED_ROSTER:' + str(directory))
    for name, digest in files.items():
        require(sha(directory / name) == digest, 'HASH:' + name)

require(len(sys.argv) == 2, 'EXPECTED_EXTERNAL_PIN_REQUIRED')
require(sha(root / 'FILES.json') == sys.argv[1], 'EXTERNAL_PIN')
files = load(root / 'FILES.json')['files']
closed(root, files, ['FILES.json'])
capsule = root / 'capsule'
external = load(root / 'AUTHENTICATION.json')['external_pins']
for name, digest in external.items():
    require(sha(capsule / name) == digest, 'PRODUCER_PIN:' + name)
closed(capsule, load(capsule / 'FILES.json')['files'], ['FILES.json', 'FREEZE.json'])
names = re.findall(r'^theorem (\w+)', (capsule / 'lean/Hidden.lean').read_text(), re.M)
audited = re.findall(r'^#print axioms Hidden\.(\w+)$', (capsule / 'lean/Audit.lean').read_text(), re.M)
require(names == audited and len(set(names)) == 30, 'EXACT_AUDIT_ROSTER')
summary = load(root / 'replay/SUMMARY.json')
require(summary['outcome'] == 'PASS_SCOPED_MODEL_AND_CALIBRATION', 'REPLAY')
require(summary['audits'] == 30 and summary['bindings'] == 15, 'COUNTS')
for variant in ['old', 'repaired']:
    oracle = (root / ('replay/lean-rows-' + variant + '.stdout')).read_text()
    require(len(oracle.splitlines()) == 192, 'ORACLE_ROWS')
    for opt in ['O0', 'O2']:
        require((root / ('replay/run-' + variant + '-' + opt + '.stdout')).read_text() == oracle, 'RAW_MATCH')
oracle = (root / 'replay/lean-rows-repaired.stdout').read_text().splitlines()
expected_mutants = {'drop_dirty_mark': 32, 'reuse_dirty': 64, 'omit_cb_key': 32,
                    'skip_publication': 80, 'force_clean_query': 96, 'ignore_forced_set': 80}
require(len(summary['mutants']) == 12, 'MUTANT_ROSTER')
for name, count in expected_mutants.items():
    for opt in ['O0', 'O2']:
        actual = (root / ('replay/run-' + name + '-' + opt + '.stdout')).read_text().splitlines()
        require(len(actual) == 192 and sum(a != b for a, b in zip(actual, oracle)) == count, 'MUTANT_CAUSE')
        require(not (root / ('replay/run-' + name + '-' + opt + '.stderr')).read_text(), 'MUTANT_STDERR')
for name in ['clean_refreshes', 'descendant_forces', 'immediate_geometry', 'old_recovers']:
    raw = (root / ('replay/false-' + name + '.stdout')).read_text()
    require('Tactic `decide` proved that the proposition' in raw and '\nis false' in raw, 'FALSECLAIM_CAUSE')
challenge = (root / 'independent/challenges.stdout').read_text()
challenge_names = re.findall(r'^theorem (\w+)', (root / 'Independent.lean').read_text(), re.M)
require(len(challenge_names) == 9 and len(challenge.splitlines()) == 9, 'CHALLENGE_ROSTER')
require('sorryAx' not in challenge and 'warning' not in challenge and 'error' not in challenge, 'CHALLENGE_KERNEL')
for name in challenge_names:
    require("'Independent." + name + "'" in challenge, 'CHALLENGE_NAME')
require(load(root / 'independent/FINAL-COMMAND.json')['exit'] == 0, 'CHALLENGE_EXIT')
guards = load(root / 'GUARDS.json')
require(len(guards) == 10 and all(x['passed'] and not x['output_created'] for x in guards), 'GUARDS')
require(not any(capsule.rglob('__pycache__')), 'NO_NESTED_BYTECODE')
for n in summary['removed_products']:
    require(not (root / 'replay' / n).exists(), 'COMPLETED_PRODUCT_RETAINED')
print(json.dumps({'verdict': 'ACCEPT_SCOPED_MODEL_AND_EXTRACTED_CALIBRATION',
                  'payloads': len(files), 'producer_audits': 30,
                  'independent_challenges': 9, 'guard_checks': 10}))
