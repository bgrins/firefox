import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use python3 -I -S without optimization')

EXPECTED = {
    'FREEZE.json': '74daebc1cde00d86fe077f5854dac166d0a6ecd3f1604b66d07914de3b17f5ff',
    'MANIFEST.json': '2a7ec9d3fec8a99b48754c7a8d4c0df2a455cc42da7d6ffbe10328d2b81aff19',
    'check.py': 'ef6820483838d8e77f6c3ce08ce219aa320ee168e41a41ad33956def2bb951a7',
}
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
source, output = args.source.resolve(), args.output.resolve()
assert not output.exists() and not output.is_relative_to(source) and not source.is_relative_to(output)
for name,pin in EXPECTED.items():
    assert hashlib.sha256((source/name).read_bytes()).hexdigest() == pin
manifest = json.loads((source/'MANIFEST.json').read_text())
output.mkdir(parents=True)
capsule = output/'capsule'
for name in [*manifest, 'FREEZE.json', 'MANIFEST.json']:
    target = capsule/name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source/name,target)
compiled = output/'compiled'
cmd = [sys.executable,'-I','-S',str(capsule/'check.py'),'--output',str(compiled)]
proc = subprocess.run(cmd,capture_output=True,text=True)
(output/'replay.log').write_text(proc.stdout+proc.stderr)
assert proc.returncode == 0
review = Path(__file__).resolve().parent
shutil.copyfile(review/'Challenges.lean',compiled/'Challenges.lean')
tool = json.loads((capsule/'TOOLCHAIN.json').read_text())
proc = subprocess.run([tool['lean'],'Challenges.lean'],cwd=compiled,
                      env={**os.environ,'LEAN_PATH':str(compiled)},capture_output=True,text=True)
(output/'challenges.log').write_text(proc.stdout+proc.stderr)
assert proc.returncode == 0 and proc.stdout.count("'IndependentReview.") == 14
shutil.copyfile(review/'integrity.py',output/'integrity.py')
(output/'V2-LOCATIONS.json').write_text(json.dumps({'temporary_root':str(output),'capsule':str(capsule),'output':str(compiled)}))
proc = subprocess.run([sys.executable,'-I','-S',str(output/'integrity.py')],capture_output=True,text=True)
(output/'integrity.log').write_text(proc.stdout+proc.stderr)
assert proc.returncode == 0
(output/'RESULT.json').write_text(json.dumps({'status':'PASS','producer_audits':81,'reviewer_boundary_theorems':14,'integrity_rejections':11},indent=2)+'\n')
print(str(output/'RESULT.json'))
