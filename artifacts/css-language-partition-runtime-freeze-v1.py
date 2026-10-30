import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / 'artifacts/css-language-partition-native-pair-runtime-1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (RUNTIME / 'FILES.json').exists()
assert not (RUNTIME / 'SYMLINKS.json').exists()
terminal = read(RUNTIME / 'ROOT-OWNER-TERMINAL.json')
assert terminal['session'] == 73082 and terminal['launch'] == '4a858d'
assert terminal['terminal'] and isinstance(terminal['exit'], int)
assert terminal['result_sha256'] == sha(RUNTIME / 'RESULT.json')
result = read(RUNTIME / 'RESULT.json')
assert result['restoration_verified'] and result['runtime_controls_unchanged']
live_terminal = read(RUNTIME / 'ROOT-LIVE-AUDIT-TERMINAL.json')
assert live_terminal['exit'] == 0 and live_terminal['terminal']
assert live_terminal['audit_sha256'] == sha(RUNTIME / 'ROOT-LIVE-RESTORATION.json')
live = read(RUNTIME / 'ROOT-LIVE-RESTORATION.json')
assert live['owner_result_sha256'] == terminal['result_sha256']
assert live['audit_script_sha256'] == sha(ROOT / 'artifacts/css-language-partition-native-live-audit-v1.py')
assert live['independent_live_restoration_verified'] and live['backup_removed']
assert len(live['independently_absent_process_groups']) == 10
expected_links = {f'{role}-wpt-{lane}/tests/tools': str(ROOT / 'testing/web-platform/tests/tools')
                  for role in ('original', 'candidate') for lane in ('target', 'regression', 'context')}
links, files = {}, {}
for directory, dirs, names in os.walk(RUNTIME, followlinks=False):
    for name in sorted(dirs + names):
        path = Path(directory) / name
        relative = str(path.relative_to(RUNTIME))
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            links[relative] = os.readlink(path)
            if name in dirs:
                dirs.remove(name)
        elif stat.S_ISREG(info.st_mode):
            files[relative] = {'sha256': sha(path), 'bytes': info.st_size}
        else:
            assert stat.S_ISDIR(info.st_mode), relative
assert links == expected_links
with (RUNTIME / 'SYMLINKS.json').open('x') as stream:
    json.dump(links, stream, indent=2, sort_keys=True)
    stream.write('\n')
files['SYMLINKS.json'] = {'sha256': sha(RUNTIME / 'SYMLINKS.json'), 'bytes': (RUNTIME / 'SYMLINKS.json').stat().st_size}
with (RUNTIME / 'FILES.json').open('x') as stream:
    json.dump(files, stream, indent=2, sort_keys=True)
    stream.write('\n')
print(json.dumps({'runtime': str(RUNTIME.relative_to(ROOT)), 'manifest_sha256': sha(RUNTIME / 'FILES.json'),
                  'regular_payloads': len(files), 'symlinks_recorded_not_followed': len(links),
                  'bytes': sum(item['bytes'] for item in files.values()), 'native_acceptance': False}))
