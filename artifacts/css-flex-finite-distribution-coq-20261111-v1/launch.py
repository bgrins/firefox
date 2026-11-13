import argparse
import json
import hashlib
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('attempt', type=int)
args = parser.parse_args()
root = Path(__file__).resolve().parent
target = json.loads((root / 'TARGET.json').read_text())
assert hashlib.sha256((root / target['source']).read_bytes()).hexdigest() == target['sha256']
attempt = root / ('attempt-' + str(args.attempt))
attempt.mkdir(exist_ok=False)
shutil.copytree(root / 'inputs', attempt / 'inputs')
shutil.copyfile(root / 'check_kernel.py', attempt / 'check_kernel.py')
(attempt / 'output').mkdir()
image = json.loads((root.parent / 'css-flex-gappa-envelope-20261111-v1/image.json').read_text())['Id']
name = 'css-flex-finite-distribution-20261111-' + str(args.attempt)
command = [
    'docker', 'run', '--rm', '--name', name, '--network=none', '--read-only',
    '--cap-drop=ALL', '--security-opt=no-new-privileges', '--memory=1g',
    '--cpus=1', '--pids-limit=128',
    '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m',
    '--tmpfs', '/work:rw,nosuid,nodev,size=256m',
    '--mount', f'type=bind,source={attempt}/inputs,target=/inputs,readonly',
    '--mount', f'type=bind,source={attempt}/check_kernel.py,target=/check_kernel.py,readonly',
    '--mount', f'type=bind,source={attempt}/output,target=/output',
    image, 'python3', '-I', '-B', '/check_kernel.py',
]
(attempt / 'COMMAND.json').write_text(json.dumps(command, indent=2) + '\n')
with (attempt / 'console.log').open('wb') as log:
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
inspection = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=^/' + name + '$',
                             '--format', '{{.ID}}'], capture_output=True, text=True)
report = {'exit': result.returncode, 'container_name': name,
          'inspection_exit': inspection.returncode, 'inspection_stdout': inspection.stdout,
          'inspection_stderr': inspection.stderr,
          'container_absent': inspection.returncode == 0 and not inspection.stdout.strip()}
(attempt / 'TERMINAL.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)
raise SystemExit(result.returncode if report['container_absent'] else 2)
