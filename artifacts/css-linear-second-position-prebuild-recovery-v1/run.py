import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PAIR = ROOT / 'artifacts/css-linear-second-position-reversible-pair-runtime-1'
OWNER = ROOT / 'artifacts/css-linear-second-position-reversible-pair-v1'
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
read = lambda p: json.loads(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


state = load('prebuild_state', RUNTIME / 'state.py')
bundle = load('prebuild_bundle', OWNER / 'bundle.py')
policy = read(OWNER / 'POLICY.json')
assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
assert set(p.name for p in PAIR.iterdir()) == {'BACKUPS.json', 'PRE-CURRENT-EPOCH.json', 'PRE-OWNED.json', 'APP-PRE.json', 'PRE-ROLE.json', 'PRE.json', 'PRE-OBSERVATION-EPOCH.json', 'backups', 'EXTRA-PRE.json'}
log = (ROOT / 'artifacts/css-linear-second-position-reversible-pair-v1-driver.log').read_text()
assert 'line 141, in <module>' in log and 'assert free() >= 35 * 1024**3' in log and log.rstrip().endswith('AssertionError')
epoch = read(PAIR / 'PRE-OBSERVATION-EPOCH.json')
before = state.a.verify_current(state.h, ROOT, ENV, epoch)
assert before == read(PAIR / 'PRE.json')
assert all((RUNTIME / n).read_bytes() == (PAIR / ('PRE-' + n)).read_bytes() for n in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json'))
assert bundle.scan(ROOT / policy['bundle_path']) == read(PAIR / 'APP-PRE.json')
assert {n: bundle.entry(ROOT / n) for n in policy['extra_backup_paths']} == read(PAIR / 'EXTRA-PRE.json')
backup = PAIR / 'backups'
saved = read(PAIR / 'BACKUPS.json')
assert backup.is_dir() and not backup.is_symlink()
assert bundle.scan(backup) == saved['owned_inventory']
state.save(HERE / 'BEFORE.json', {'terminal_session': 40597, 'terminal_chunk': '972325', 'exit': 1,
    'failure': 'backup completed, build-start disk floor not met', 'source_build_browser_never_started': True,
    'full_original_state_verified': True, 'backup_bytes': saved['bytes'],
    'backup_inventory_sha256': hashlib.sha256((PAIR / 'BACKUPS.json').read_bytes()).hexdigest(),
    'free_bytes': shutil.disk_usage(ROOT).free})
shutil.rmtree(backup)
assert not backup.exists()
assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
assert bundle.scan(ROOT / policy['bundle_path']) == read(PAIR / 'APP-PRE.json')
assert {n: bundle.entry(ROOT / n) for n in policy['extra_backup_paths']} == read(PAIR / 'EXTRA-PRE.json')
assert all((RUNTIME / n).read_bytes() == (PAIR / ('PRE-' + n)).read_bytes() for n in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json'))
state.save(HERE / 'RESULT.json', {'success': True, 'unused_backup_removed': True,
    'source_application_controls_preserved': True, 'build_or_browser_ran': False,
    'free_bytes_after': shutil.disk_usage(ROOT).free})
print('Verified untouched prebuild state and removed only the exact unused backup')
