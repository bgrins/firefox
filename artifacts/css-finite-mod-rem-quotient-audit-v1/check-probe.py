from pathlib import Path
import argparse
import json
import re
import subprocess
import tempfile

p = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
out = Path(parser.parse_args().output)
assert not out.exists()
out.mkdir()
script, = re.findall(r'<script>([\s\S]*?)</script>', (p / 'probe.html').read_text())
with tempfile.TemporaryDirectory(prefix='finite-mod-js-', dir='/private/tmp') as tmp:
    js = Path(tmp) / 'probe.js'
    js.write_text(script)
    r = subprocess.run(['node', '--check', str(js)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    registration = Path(tmp) / 'register.js'
    registration.write_text('const names=[];global.test=(f,n)=>names.push(n);\n' + script +
                            '\nconsole.log(JSON.stringify({names,cases,guards}));')
    r = subprocess.run(['node', str(registration)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    result = json.loads(r.stdout)
    assert len(result['names']) == len(set(result['names'])) == 24
    assert len(result['cases']) == len(result['guards']) == 8
    for row in result['cases']:
        for a, key in [(row['a'], 'expected'), (17 if row['a'] > 0 else -17, 'small')]:
            b = row['b']
            q = a // b if row['op'] == 'mod' else abs(a) // abs(b) * (1 if a * b >= 0 else -1)
            assert row[key] == a - b * q
        assert 0 <= .5 + row['expected'] / 8 <= 1
    (out / 'ROSTER.json').write_text(json.dumps(result['names'], indent=2) + '\n')
    (out / 'LITERAL-ORACLES.json').write_text(json.dumps(result['cases'], indent=2) + '\n')
(out / 'CHECK.json').write_text(json.dumps(dict(status='UNEXECUTED_PROBE_STATIC_PASS', cases=24,
    semantic_targets=16, strict_guard_cases=8, independent_integer_table=True, js_syntax=True,
    scratch_removed=not Path(tmp).exists(), browser=False, wpt_lint=False), indent=2) + '\n')
