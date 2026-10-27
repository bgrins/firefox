from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
out = parser.parse_args().output.resolve()
out.mkdir(exist_ok=False)
fixture = ROOT / 'artifacts/css-finite-mod-rem-repair-v1/head90/candidate/testing/web-platform/tests/css/css-values/mod-rem-exact-finite-remainder.html'
worker = ROOT / 'artifacts/css-round-parse-negative-zero-repair-v2/check.py'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(worker) == '610f5b2f463a6cddef930b9a824ee5a5e1d14afa73e5bfb33116bbfe49ba4cc8'
relative = 'css/css-values/mod-rem-exact-finite-remainder.html'
rev = '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
with tempfile.TemporaryDirectory(prefix='mod-rem-lint-') as tmp:
    scratch = Path(tmp)
    subprocess.run(['git','init','-q',str(scratch)],check=True,capture_output=True)
    support = {}
    for name in ['.gitignore','lint.ignore']:
        data = subprocess.run(['git','show',f'{rev}:testing/web-platform/tests/{name}'],cwd=ROOT,check=True,capture_output=True).stdout
        (scratch/name).write_bytes(data)
        support[name] = sha(scratch/name)
    target = scratch/relative
    target.parent.mkdir(parents=True)
    target.write_bytes(fixture.read_bytes())
    command = [str(ROOT/'testing/web-platform/tests/_venv3/bin/python3'),'-I','-B',str(worker),'--lint-worker',str(scratch),relative]
    result = subprocess.run(command,cwd=scratch,capture_output=True,text=True)
    (out/'stdout.log').write_text(result.stdout)
    (out/'stderr.log').write_text(result.stderr)
    assert result.returncode == 0 and not result.stdout and not result.stderr
record = dict(status='WPT_SCRATCH_LINT_PASS',command=command,cwd=tmp,exit=result.returncode,
    stdout_empty=True,stderr_empty=True,fixture_sha256=sha(fixture),worker_sha256=sha(worker),
    support_revision=rev,support_sha256=support,owned_scratch_removed=not Path(tmp).exists(),
    main_wpt_paths_written=False,browser_run=False,native_build=False,main_index_actions=False)
(out/'CHECK.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
