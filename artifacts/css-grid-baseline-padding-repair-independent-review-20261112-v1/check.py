from pathlib import Path
import base64
import contextlib
import hashlib
import io
import json
import runpy
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
repo = here.parents[1]
p = repo / 'artifacts/css-grid-baseline-padding-repair-20261112-v1'
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(p / 'FILES.json') == '76fc25a02c536d3fae1cdd862b3ad1be2b36dda8ad8759f51b285705beab9145'
files = json.loads((p / 'FILES.json').read_text())
assert len(files) == 77
for name, rec in files.items():
    assert sha(p / name) == rec['sha256']
    assert (p / name).stat().st_size == rec['bytes']
output = io.StringIO()
with contextlib.redirect_stdout(output):
    runpy.run_path(str(p / 'verify.py'), run_name='__main__')
verified = json.loads(output.getvalue())
assert all(r['identical_screenshots'] is True for r in verified['controls'].values() if r['status'] == 'FAIL')
phases = {}
for phase in ['baseline-v3', 'fixed']:
    raw = [json.loads(s) for s in (p / phase / 'raw.log').read_text().splitlines() if s.startswith('{')]
    report = json.loads((p / phase / 'wptreport.json').read_text())
    tests = {r['test']: r for r in report['results']}
    endings = {r['test']: r for r in raw if r.get('action') == 'test_end'}
    assert endings.keys() == tests.keys()
    pictures = {}
    for name, r in tests.items():
        assert endings[name]['status'] == r['status']
        actual = {a['subtest']: a['status'] for a in raw if a.get('action') == 'test_status' and a['test'] == name}
        assert actual == {s['name']: s['status'] for s in r.get('subtests', [])}
        for image in endings[name].get('extra', {}).get('reftest_screenshots', []):
            if isinstance(image, dict):
                b = base64.b64decode(image['screenshot'], validate=True)
                pictures[image['url']] = hashlib.sha256(b).hexdigest()
    assert len(pictures) == 4
    phases[phase] = pictures
assert phases['baseline-v3'] == phases['fixed']
inputs = json.loads((p / 'INPUTS.json').read_text())
assert json.loads((p / 'build/INSTALL.json').read_text()) == {n: r['candidate'] for n, r in inputs.items()}
for phase, exit_code in [('baseline-v3', 1), ('build', 0), ('fixed', 0)]:
    record = json.loads((p / phase / 'COMMANDS.json').read_text())[0]
    assert record['exit'] == exit_code and record['group_absent'] and record['safe_cleanup']
    assert not any(k.endswith('error') for k in record)
    assert record['seconds'] < (1800 if phase == 'build' else 300)
    if phase != 'build':
        expected = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless', '--no-pause-after-test', '--processes=1',
                    '--binary=' + str(repo / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'),
                    '--log-raw=' + str(p / phase / 'raw.log'), '--log-wptreport=' + str(p / phase / 'wptreport.json')]
        expected += [next(n for n in inputs if n.endswith('.html'))]
        expected += ['testing/web-platform/tests/css/css-grid/alignment/' + n for n in ['grid-baseline-align-001.html', 'grid-baseline-align-cycles-001.html', 'grid-baseline-justify-001.html']]
        assert record['argv'] == expected

head = json.loads((p / 'STANDALONE-HEAD-CHECK.json').read_text())
scratch = Path(tempfile.mkdtemp(prefix='baseline-padding-head-review-', dir='/private/tmp'))
commands = []
def run(argv, cwd):
    r = subprocess.run(argv, cwd=cwd, capture_output=True)
    commands.append({'argv': argv, 'cwd': str(cwd), 'exit': r.returncode, 'stdout': r.stdout.decode(), 'stderr': r.stderr.decode()})
    assert r.returncode == 0
    return r.stdout
try:
    for name, digest in head['before'].items():
        b = run(['git', '-c', 'core.fsmonitor=false', 'show', head['head'] + ':' + name], repo)
        f = scratch / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b)
        assert sha(f) == digest
    run(['git', '-c', 'core.fsmonitor=false', 'apply', str(p / 'candidate.patch')], scratch)
    for name, digest in head['applied'].items():
        assert sha(scratch / name) == digest
    run(['git', '-c', 'core.fsmonitor=false', 'apply', '--reverse', str(p / 'candidate.patch')], scratch)
    for name, digest in head['before'].items():
        assert sha(scratch / name) == digest
    assert not (scratch / next(n for n in inputs if n.endswith('.html'))).exists()
finally:
    for r in commands:
        if r['argv'][3:4] == ['show']:
            r['stdout'] = '<authenticated source bytes omitted>'
    (here / 'HEAD-COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    shutil.rmtree(scratch)
print(json.dumps({'authenticated_files': len(files), 'retained_verifier': verified,
                  'raw_and_report_match': True, 'decoded_control_screenshots_sha256': phases['fixed'],
                  'fresh_HEAD_patch_roundtrip': True, 'owned_scratch_removed': not scratch.exists(),
                  'fresh_compiler': False, 'fresh_browser': False}, indent=2))
