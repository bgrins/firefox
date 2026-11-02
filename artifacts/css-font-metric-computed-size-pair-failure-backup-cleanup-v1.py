import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
assert len(sys.argv) == 2
ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / 'artifacts/css-font-metric-computed-size-pair-runtime-1'
OWNER = ROOT / 'artifacts/css-font-metric-computed-size-pair-v1'
sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda path: json.loads(path.read_bytes())
assert sha((OWNER / 'FILES.json').read_bytes()) == 'bbcc1d5fbc7bde467171a8eb7f92bc5bc587824bd82035a7e025c69ae132f3bc'
for name, record in read(OWNER / 'FILES.json').items():
    assert sha((OWNER / name).read_bytes()) == record['sha256']
report_path = RUNTIME / 'ROOT-LIVE-RESTORATION.json'
assert sha(report_path.read_bytes()) == sys.argv[1]
report = read(report_path)
assert report['independent_live_restoration_verified'] and report['retained_backup_inventory_verified']
assert report['backup_removed'] is False and report['native_acceptance'] is False
assert report['audit_script_sha256'] == sha((ROOT / 'artifacts/css-font-metric-computed-size-pair-failure-audit-v1.py').read_bytes())
for name, digest in report['failure_pins'].items():
    assert sha((RUNTIME / name).read_bytes()) == digest
policy = read(OWNER / 'POLICY.json')
helper = ROOT / policy['bundle_helper']
assert str(helper.relative_to(ROOT)) == 'artifacts/css-round-context-quotient-reversible-pair-v2/bundle.py'
assert sha(helper.read_bytes()) == '353b68ff0e6b33c2a991c5208fe8b52a3dd6da0d3f717e8b848a7f69d9193140'
spec = importlib.util.spec_from_file_location('failure_cleanup_bundle', helper)
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)
backups = RUNTIME / 'backups'
assert backups.is_dir() and not backups.is_symlink()
inventory = read(RUNTIME / 'BACKUPS.json')
assert sha((RUNTIME / 'BACKUPS.json').read_bytes()) == report['backup_inventory_sha256']
assert inventory['bytes'] == 1008605176
assert bundle.scan(backups) == inventory['owned_inventory']
output = RUNTIME / 'ROOT-BACKUP-CLEANUP.json'
assert not output.exists() and not output.is_symlink()
assert not (ROOT / 'artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock').exists()
shutil.rmtree(backups)
assert not backups.exists() and not backups.is_symlink()
with output.open('x') as stream:
    json.dump({'removed': True, 'owned_backup_bytes': inventory['bytes'],
               'inventory_verified_before_removal': True, 'independent_restoration_report_sha256': sys.argv[1],
               'backup_inventory_sha256': report['backup_inventory_sha256'],
               'historical_owner_cleanup_sha256': report['failure_pins']['BACKUP-CLEANUP.json'],
               'cleanup_script_sha256': sha(Path(__file__).read_bytes())}, stream, indent=2)
    stream.write('\n')
print('Removed only the independently verified owned backup')
