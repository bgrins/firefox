import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROPOSAL = ROOT / 'artifacts/css-steps-jump-none-repair-v2'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'testing/web-platform/tests'))
from tools.lint import lint

paths = sorted(str(p.relative_to(PROPOSAL / 'candidate/testing/web-platform/tests'))
               for p in (PROPOSAL / 'candidate/testing/web-platform/tests').rglob('*.html'))
with tempfile.TemporaryDirectory(prefix='steps-wpt-lint-', dir='/private/tmp') as tmp:
    scratch = Path(tmp)
    shutil.copyfile(ROOT / 'testing/web-platform/tests/lint.ignore', scratch / 'lint.ignore')
    for path in paths:
        dest = scratch / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROPOSAL / 'candidate/testing/web-platform/tests' / path, dest)
    subprocess.run(['git', '-c', 'init.defaultBranch=lint-scratch', 'init', '--quiet', str(scratch)], check=True)
    previous = Path.cwd()
    os.chdir(scratch)
    try:
        lint.setup_logging(False)
        errors = lint.lint(str(scratch), paths, 'json', jobs=1)
    finally:
        os.chdir(previous)
receipt = {'errors': errors, 'paths': paths,
           'source_hashes': {n: hashlib.sha256((PROPOSAL / 'candidate/testing/web-platform/tests' / n).read_bytes()).hexdigest() for n in paths},
           'python': sys.executable, 'scratch_removed': not scratch.exists(),
           'browser_executed': False}
(HERE / 'LINT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
raise SystemExit(1 if errors else 0)
