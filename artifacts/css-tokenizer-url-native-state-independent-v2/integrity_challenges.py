from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site
p = argparse.ArgumentParser()
p.add_argument('--package', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
results = []
for case in ['source-change', 'extra-file', 'extra-directory', 'symlink',
             'duplicate-key', 'missing-input', 'no-isolation', 'no-no-site']:
    folder = a.output / case
    shutil.copytree(a.package, folder)
    flags = ['-I', '-S', '-B']
    reason = 'input authentication' if case == 'source-change' else None
    if case == 'source-change':
        path = folder / 'lean/URLNativeState.lean'
        path.write_text(path.read_text() + '\n')
    elif case == 'extra-file':
        (folder / 'json.py').write_text('raise RuntimeError("shadow executed")\n')
        reason = 'closed input roster'
    elif case == 'extra-directory':
        (folder / 'unlisted').mkdir()
        reason = 'closed directory roster'
    elif case == 'symlink':
        (folder / 'unlisted').symlink_to('check.py')
        reason = 'symlink input'
    elif case == 'duplicate-key':
        path = folder / 'MANIFEST.json'
        path.write_text(path.read_text().replace('{', '{"check.py":"duplicate",', 1))
        freeze = json.loads((folder / 'FREEZE.json').read_text())
        freeze['manifest_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        (folder / 'FREEZE.json').write_text(json.dumps(freeze))
        reason = 'duplicate JSON key'
    elif case == 'missing-input':
        (folder / 'lean/URLNativeState.lean').unlink()
        reason = 'closed input roster'
    elif case == 'no-isolation':
        flags = ['-S', '-B']
        reason = 'invoke Python with -I -S'
    elif case == 'no-no-site':
        flags = ['-I', '-B']
        reason = 'invoke Python with -I -S'
    target = a.output / (case + '-run')
    command = [sys.executable, *flags, str(folder / 'check.py'), '--run', '--output', str(target)]
    done = subprocess.run(command, capture_output=True, text=True)
    log = done.stdout + done.stderr
    (a.output / (case + '.log')).write_text(log)
    assert done.returncode != 0 and reason in log and not target.exists()
    assert 'shadow executed' not in log
    results.append({'case': case, 'exit': done.returncode, 'reason': reason,
                    'output_created': False, 'command': command})
    shutil.rmtree(folder)
(a.output / 'CHECK.json').write_text(json.dumps({'status': 'PASS', 'cases': results}, indent=2) + '\n')
print('PASS', len(results), 'integrity challenges')
