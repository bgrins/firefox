import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S without -O')
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
if (ROOT / 'FILES.json').exists() or (ROOT / 'FREEZE.json').exists():
    raise SystemExit('Already sealed')
if not (ROOT / 'REPORT.md').is_file():
    raise SystemExit('Final report required')
subprocess.run([sys.executable, '-I', '-S', '-B', str(ROOT / 'analyze.py'), '--check'], check=True)
sha = lambda b: hashlib.sha256(b).hexdigest()
files = {}
for path in sorted(ROOT.rglob('*')):
    if path.is_symlink():
        raise SystemExit('Symlink')
    if path.is_file():
        files[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
(ROOT / 'FILES.json').write_text(json.dumps(files, indent=2) + '\n')
freeze = {'files_sha256': sha((ROOT / 'FILES.json').read_bytes()), 'payloads': len(files),
          'report_sha256': sha((ROOT / 'REPORT.md').read_bytes()),
          'verifier_sha256': sha((ROOT / 'verify.py').read_bytes()),
          'status': 'STANDALONE_WITHOUT_102_FINITE_GATE_PASS', 'producer_evidence': True,
          'independent_review': False, 'native_accepted': False}
(ROOT / 'FREEZE.json').write_text(json.dumps(freeze, indent=2) + '\n')
print(json.dumps({**freeze, 'freeze_sha256': sha((ROOT / 'FREEZE.json').read_bytes())}))
