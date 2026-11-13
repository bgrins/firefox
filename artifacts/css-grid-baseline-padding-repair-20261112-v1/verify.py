import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


inputs = read(HERE / 'INPUTS.json')
for name, hashes in inputs.items():
    assert sha(ROOT / name) == sha(HERE / 'candidate' / name) == hashes['candidate']
    if 'original' in hashes:
        assert sha(HERE / 'original' / name) == hashes['original']
for phase in ['baseline-v3', 'build', 'fixed']:
    out = HERE / phase
    assert read(out / 'INPUTS.json') == inputs
    assert (out / 'runner.py').read_bytes() == (HERE / 'run.py').read_bytes()
    commands = read(out / 'COMMANDS.json')
    assert len(commands) == 1
    command = commands[0]
    assert command['exit'] == (1 if phase == 'baseline-v3' else 0)
    assert command['safe_cleanup'] and command['group_absent']
    assert not command.get('timeout')
    assert read(out / 'CLEANUP.json') == dict(groups_absent=True, sources_match=True)
    assert command['cwd'] == str(ROOT)
    if phase == 'build':
        assert command['argv'] == ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
    else:
        assert '--headless' in command['argv']
        assert command['argv'][-4:] == [next(n for n in inputs if n.endswith('.html'))] + [
            'testing/web-platform/tests/css/css-grid/alignment/' + n for n in
            ['grid-baseline-align-001.html', 'grid-baseline-align-cycles-001.html', 'grid-baseline-justify-001.html']]
base = read(HERE / 'baseline-v3/wptreport.json')['results']
fixed = read(HERE / 'fixed/wptreport.json')['results']
assert len(base) == len(fixed) == 4
by_name = lambda rows: {row['test']: row for row in rows}
base = by_name(base)
fixed = by_name(fixed)
assert base.keys() == fixed.keys()
regression = next(n for n in base if n.endswith('grid-baseline-content-reflow-root.html'))
assert base[regression]['status'] == fixed[regression]['status'] == 'OK'
old = {s['name']: s['status'] for s in base[regression]['subtests']}
new = {s['name']: s['status'] for s in fixed[regression]['subtests']}
assert len(old) == len(new) == 120 and old.keys() == new.keys()
assert list(old.values()).count('FAIL') == 28 and list(old.values()).count('PASS') == 92
assert set(new.values()) == {'PASS'}
controls = {}
for name in base.keys() - {regression}:
    assert base[name]['status'] == fixed[name]['status']
    controls[name] = dict(status=fixed[name]['status'],
                         identical_screenshots=(base[name]['screenshots'] == fixed[name].get('screenshots')
                                                if 'screenshots' in base[name] else None))
before = read(HERE / 'build/BINARIES-BEFORE.json')
after = read(HERE / 'build/BINARIES-AFTER.json')
assert before == read(HERE / 'baseline-v3/BINARIES-BEFORE.json') == read(HERE / 'baseline-v3/BINARIES-AFTER.json')
assert after == read(HERE / 'fixed/BINARIES-BEFORE.json') == read(HERE / 'fixed/BINARIES-AFTER.json')
xul = next(name for name in before if Path(name).name == 'XUL')
assert before[xul]['sha256'] != after[xul]['sha256']
assert all(sha(Path(name)) == value['sha256'] for name, value in after.items())
assert read(HERE / 'STANDALONE-HEAD-CHECK.json')['patch_sha256'] == sha(HERE / 'candidate.patch')
print(json.dumps(dict(status='PASS local native repair evidence', regression_cases=120,
    corrected=28, preserved=92, controls=controls, native_refinement=False,
    universal_browser_correctness=False), indent=2))
