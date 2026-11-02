import hashlib
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / 'artifacts/css-hyphenation-ownership-native-pair-runtime-2'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (RUNTIME/'FILES.json').exists() and not (RUNTIME/'SYMLINKS.json').exists()
result = read(RUNTIME/'RESULT.json')
terminal = read(RUNTIME/'ROOT-OWNER-TERMINAL.json')
assert terminal['session'] == 25179 and terminal['launch'] == '8b41d2'
assert terminal['terminal'] and terminal['exit'] == 0 and terminal['result_sha256'] == sha(RUNTIME/'RESULT.json')
assert result['success'] and result['restoration_verified'] and not result['native_fix_acceptance']
audit = read(RUNTIME/'ROOT-LIVE-RESTORATION.json')
audit_terminal = read(RUNTIME/'ROOT-LIVE-AUDIT-TERMINAL.json')
assert audit_terminal['terminal'] and audit_terminal['exit'] == 0
assert audit_terminal['audit_sha256'] == sha(RUNTIME/'ROOT-LIVE-RESTORATION.json')
assert audit['independent_live_restoration_verified'] and audit['owner_result_sha256'] == sha(RUNTIME/'RESULT.json')
assert audit['audit_script_sha256'] == sha(ROOT/'artifacts/css-hyphenation-ownership-native-live-audit-v2.py')
assert not (RUNTIME/'backups').exists()
expected = {role+'-wpt-'+lane+'/tests/tools':str(ROOT/'testing/web-platform/tests/tools') for role in ('original','candidate') for lane in ('target','regression','context')}
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
