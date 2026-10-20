import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SNAPSHOT = OUT / 'format-v1/before'
assert not SNAPSHOT.exists()
GIT = ['git', '-c', 'core.fsmonitor=false']
allowed = {'layout/generic/StickyScrollContainer.cpp'}
paths = set()
for args in [['diff', '--name-only', '-z'],
             ['diff', '--cached', '--name-only', '-z'],
             ['ls-files', '--others', '--exclude-standard', '-z',
              'testing/web-platform/tests']]:
    paths.update(n for n in subprocess.check_output(GIT + args, cwd=ROOT).decode().split('\0') if n)
before = {}
for name in sorted(paths):
    path = ROOT / name
    if path.is_file():
        before[name] = path.read_bytes()
        saved = SNAPSHOT / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(before[name])
changed = []
restored = []
try:
    with (OUT / 'format-v1.log').open('x') as output:
        result = subprocess.run(
            ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'format'],
            cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
            env={**os.environ, 'MOZ_SKIP_PATH_PERFORMANCE_CHECK': '1'})
finally:
    for name, data in before.items():
        if (ROOT / name).read_bytes() != data:
            changed.append(name)
            if name not in allowed:
                (ROOT / name).write_bytes(data)
                restored.append(name)
record = {'exit': result.returncode, 'snapshotted': len(before),
          'changed': changed, 'restored_unrelated': restored,
          'native_sha256': {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest()
                            for n in sorted(allowed)}}
(OUT / 'FORMAT-v1.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
raise SystemExit(result.returncode)
