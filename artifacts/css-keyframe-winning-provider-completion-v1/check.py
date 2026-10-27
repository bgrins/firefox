import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
here = Path(__file__).resolve().parent
assert args.output.is_absolute() and not args.output.exists()
for name, sha in json.loads((here / 'FILES.json').read_text()).items():
    assert hashlib.sha256((here / name).read_bytes()).hexdigest() == sha, name
args.output.mkdir()
for name in ['winning_provider_completion.rs', 'scheduler_tests.rs', 'replay.py',
             'native.patch', 'PREIMAGES.json', 'POSTIMAGES.json']:
    shutil.copy2(here / name, args.output / name)
shutil.copytree(here / 'original', args.output / 'original')
raise SystemExit(subprocess.run([sys.executable, '-I', '-S', '-B', str(args.output / 'replay.py')]).returncode)
