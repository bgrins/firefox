import hashlib
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / 'artifacts/css-prioritary-declaration-capacity-browser-runtime-1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (RUNTIME/'FILES.json').exists() and not (RUNTIME/'SYMLINKS.json').exists()
result = read(RUNTIME/'RESULT.json')
terminal = read(RUNTIME/'ROOT-OWNER-TERMINAL.json')
assert terminal['session'] == 68207 and terminal['launch'] == 'b1490c'
assert terminal['terminal'] and terminal['exit'] == (0 if result['success'] else 1) and terminal['result_sha256'] == sha(RUNTIME/'RESULT.json')
assert result['restoration_verified'] and not result['native_fix_acceptance']
audit = read(RUNTIME/'ROOT-LIVE-RESTORATION.json')
audit_terminal = read(RUNTIME/'ROOT-LIVE-AUDIT-TERMINAL.json')
assert audit_terminal['terminal'] and audit_terminal['exit'] == 0
assert audit_terminal['audit_sha256'] == sha(RUNTIME/'ROOT-LIVE-RESTORATION.json')
assert audit['independent_live_restoration_verified'] and audit['owner_result_sha256'] == sha(RUNTIME/'RESULT.json')
assert audit['audit_script_sha256'] == sha(ROOT/'artifacts/css-prioritary-declaration-capacity-browser-live-audit-v1.py')
historical = read(RUNTIME/'BACKUP-CLEANUP.json')
if historical['removed']:
    assert result['success'] and audit['backup_removed'] and not historical['retained_after_failure']
else:
    cleanup = read(RUNTIME/'ROOT-BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['inventory_verified_before_removal']
    assert cleanup['owned_backup_bytes'] == read(RUNTIME/'BACKUPS.json')['bytes']
    assert cleanup['independent_restoration_report_sha256'] == sha(RUNTIME/'ROOT-LIVE-RESTORATION.json')
    assert cleanup['historical_owner_cleanup_sha256'] == sha(RUNTIME/'BACKUP-CLEANUP.json')
    assert cleanup['cleanup_script_sha256'] == sha(ROOT/'artifacts/css-prioritary-declaration-capacity-browser-backup-cleanup-v1.py')
    assert historical['retained_after_failure'] is True and not result['success']
assert not (RUNTIME/'backups').exists() and not (RUNTIME/'backups').is_symlink()
expected = {role+'-wpt-capacity/tests/tools':str(ROOT/'testing/web-platform/tests/tools') for role in ('original','candidate') if (RUNTIME/(role+'-wpt-capacity/tests/tools')).is_symlink()}
for role in ('original','candidate'):
    if (RUNTIME/(role+'-wpt-capacity/PROCESS.json')).exists():
        assert role+'-wpt-capacity/tests/tools' in expected
links = {}
paths = []
for directory, subdirs, files in os.walk(RUNTIME, followlinks=False):
    for name in subdirs + files:
        path = Path(directory)/name
        if path.is_symlink():
            links[str(path.relative_to(RUNTIME))] = os.readlink(path)
        elif path.is_file():
            paths.append(path)
        else:
            assert path.is_dir()
assert links == expected
with (RUNTIME/'SYMLINKS.json').open('x') as stream:
    json.dump(links,stream,indent=2,sort_keys=True);stream.write('\n')
paths.append(RUNTIME/'SYMLINKS.json')
manifest = {str(p.relative_to(RUNTIME)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(paths)}
with (RUNTIME/'FILES.json').open('x') as stream:
    json.dump(manifest,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps({'manifest_sha256':sha(RUNTIME/'FILES.json'),'regular_payloads':len(manifest),'symlinks_not_dereferenced':len(links)}))
