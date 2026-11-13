import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

inputs = Path('/inputs')
output = Path('/output')
work = Path('/work')
names = json.loads((inputs / 'MODULES.json').read_text())
base_names = json.loads((inputs / 'BASE-MODULES.json').read_text())
cache = Path('/cache')
cache_manifest = json.loads((cache / 'CACHE.json').read_text()) if cache.exists() else None
rows = []
shutil.copyfile('/certificate-checker-packages.txt', output / 'packages.txt')


def run(command, label, hashes):
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=work, capture_output=True, timeout=120)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as error:
        stdout, stderr, code = error.stdout or b'', error.stderr or b'', None
    (output / (label + '.stdout')).write_bytes(stdout)
    (output / (label + '.stderr')).write_bytes(stderr)
    row = {'command': command, 'exit': code, 'input_sha256': hashes,
           'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
           'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
           'seconds': time.monotonic() - start}
    rows.append(row)
    (output / 'RESULTS.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps(row), flush=True)


hashes = {}
for name in names:
    source = inputs / (name + '.v')
    hashes[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
    shutil.copyfile(source, work / source.name)
    if cache_manifest is not None and name in base_names:
        entry = cache_manifest[name]
        assert entry['source_sha256'] == hashes[source.name]
        cached_object = cache / (name + '.vo')
        assert hashlib.sha256(cached_object.read_bytes()).hexdigest() == entry['object_sha256']
        shutil.copyfile(cached_object, work / cached_object.name)
        rows.append({'command': ['cache-import', name], 'exit': 0, 'reused': True,
                     'source_sha256': hashes[source.name], 'object_sha256': entry['object_sha256']})
        (output / 'RESULTS.json').write_text(json.dumps(rows, indent=2) + '\n')
    else:
        run(['coqc', '-q', source.name], name, {source.name: hashes[source.name]})
    if name == base_names[-1] and all(row['exit'] == 0 for row in rows):
        export = output / 'base-cache'
        export.mkdir(exist_ok=False)
        entries = {}
        for base in base_names:
            obj = work / (base + '.vo')
            shutil.copyfile(obj, export / obj.name)
            entries[base] = {'source_sha256': hashlib.sha256((inputs / (base + '.v')).read_bytes()).hexdigest(),
                             'object_sha256': hashlib.sha256(obj.read_bytes()).hexdigest()}
        (export / 'CACHE.json').write_text(json.dumps(entries, indent=2) + '\n')
    if rows[-1]['exit'] != 0:
        break
if len(rows) == len(names) and all(row['exit'] == 0 for row in rows):
    run(['coqchk', '-silent'] + names, 'coqchk', hashes)
passed = len(rows) == len(names) + 1 and all(row['exit'] == 0 for row in rows)
(output / 'RESULT.json').write_text(json.dumps({
    'status': 'PASS' if passed else 'FAIL', 'scope': 'proof-development',
    'target_acceptance': False, 'commands': len(rows), 'inherited_cache_reused': cache_manifest is not None}, indent=2) + '\n')
raise SystemExit(0 if passed else 1)
