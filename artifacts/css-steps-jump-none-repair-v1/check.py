import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
args = argparse.ArgumentParser()
args.add_argument('--output', required=True)
out = Path(args.parse_args().output).resolve()
assert not out.exists()
out.mkdir()
pre = json.loads((HERE / 'PREIMAGES.json').read_text())
post = json.loads((HERE / 'POSTIMAGES.json').read_text())
for role, pins in [('original', pre), ('candidate', post)]:
    for name, pin in pins.items():
        path = HERE / role / name
        assert (not path.exists()) if pin is None else hashlib.sha256(path.read_bytes()).hexdigest() == pin['sha256']
rows = json.loads((HERE / 'HISTORICAL-BASELINE-ROWS.json').read_text())
old = {r['test']: [] for r in rows}
for row in rows:
    old[row['test']].append(row['subtest'])
roster = {}
with tempfile.TemporaryDirectory(prefix='steps-jump-none-', dir='/private/tmp') as tmp:
    scratch = Path(tmp)
    for name, pin in pre.items():
        if pin:
            target = scratch / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / 'original' / name, target)
    for reverse, expected in [(False, post), (True, pre)]:
        args = ['git', 'apply', *(['--reverse'] if reverse else []), str(HERE / 'gecko-wpt.patch')]
        subprocess.run(args[:2] + ['--check'] + args[2:], cwd=scratch, check=True, capture_output=True)
        subprocess.run(args, cwd=scratch, check=True, capture_output=True)
        for name, pin in expected.items():
            path = scratch / name
            assert (not path.exists()) if pin is None else hashlib.sha256(path.read_bytes()).hexdigest() == pin['sha256']
    for path in sorted((HERE / 'candidate/testing').rglob('*.html')) + sorted((HERE / 'readonly/testing').rglob('*.html')):
        script = '\n'.join(re.findall(r'<script>([\s\S]*?)</script>', path.read_text()))
        js = scratch / 'test.js'
        js.write_text(script)
        subprocess.run(['node', '--check', str(js)], check=True, capture_output=True)
        js.write_text('''const names=[];
global.document={getElementById:()=>({})};
global.test=(fn,name)=>names.push(name);
global.test_valid_value=(p,v)=>names.push(`e.style['${p}'] = "${v}" should set the property value`);
global.test_invalid_value=(p,v)=>names.push(`e.style['${p}'] = "${v}" should not set the property value`);
global.test_computed_value=(p,v)=>names.push(`Property ${p} value '${v}'`);
''' + script + '\nconsole.log(JSON.stringify(names));\n')
        names = json.loads(subprocess.check_output(['node', str(js)]))
        assert len(names) == len(set(names))
        test = '/' + str(path).split('/testing/web-platform/tests/')[1]
        roster[test] = names
    assert sum(map(len, roster.values())) == 77
    fixture = '/css/css-easing/steps-jump-none-constant-calc.html'
    assert roster[fixture] == old[fixture]
    valid = '/css/css-easing/timing-functions-syntax-valid.html'
    assert roster[valid] == old[valid]
    changes = {test: {'added': [n for n in names if n not in old[test]], 'removed': [n for n in old[test] if n not in names]} for test, names in roster.items()}
    assert sum(len(v['added']) for v in changes.values()) == 2
    assert sum(len(v['removed']) for v in changes.values()) == 1
    rust = (HERE / 'candidate/servo/components/style/values/specified/easing.rs').read_text()
    assert 'if steps.resolve().is_none()' in rust
    assert 'StepPosition::JumpNone && steps.get() == Some(1)' in rust
    assert '*pos == StepPosition::JumpNone && steps.get().is_none()' in rust
    assert 'self.to_computed_value_without_context()' in rust
    original = (HERE / 'original/servo/components/style/values/specified/easing.rs').read_text()
    for start, end in [('    fn parse_cubic_bezier', '    fn parse_steps'), ('    fn parse_linear_function', '// We need this'), ('impl ToComputedValue', None)]:
        if start not in original:
            continue
        def part(s):
            return s[s.index(start):s.index(end)] if end else s[s.index(start):]
        assert part(original) == part(rust)
(out / 'CANDIDATE-ROSTER.json').write_text(json.dumps(roster, indent=2) + '\n')
(out / 'ROSTER-DELTA.json').write_text(json.dumps(changes, indent=2) + '\n')
(out / 'STATIC.json').write_text(json.dumps({'status': 'ISOLATED_STEPS_PROPOSAL_STATIC_PASS', 'patch_apply_reverse': True, 'candidate_cases': 77, 'historical_cases': 76, 'fixture_names_unchanged': 18, 'js_syntax': True, 'registration_only_no_callbacks': True, 'scratch_removed': not scratch.exists(), 'native_compiled': False, 'browser_executed': False}, indent=2) + '\n')
print('PASS: four-path transport/reverse, 77 unique per-file registrations, 18 stable fixture names, shared guarded conversion')
