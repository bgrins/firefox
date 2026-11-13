from pathlib import Path
import contextlib
import hashlib
import io
import json
import re
import runpy
import sys

sys.dont_write_bytecode = True
repo = Path(__file__).resolve().parents[2]
art = repo / 'artifacts'
proof = art / 'css-baseline-padding-feedback-model-20261112-v1'
target_review = art / 'css-baseline-padding-feedback-model-target-review-20261112-v1'
probe = art / 'css-grid-baseline-peer-priming-system-probe-20261112-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pins = [(proof, '0037874851411d730f396c6dff77694be5f8c57f96f4a7dbd8730649a7cb839b'),
        (target_review, 'f2dc79221cb1921f6a7ace6f52771e0f5b34590a182c38511f4c894d133988a6')]
probe_pin = sha(probe / 'FILES.json')
assert probe_pin.startswith('b421f079')
pins.append((probe, probe_pin))
counts = {}
for folder, pin in pins:
    assert sha(folder / 'FILES.json') == pin
    files = json.loads((folder / 'FILES.json').read_text())
    for name, rec in files.items():
        digest = rec if isinstance(rec, str) else rec['sha256']
        assert sha(folder / name) == digest, name
        if isinstance(rec, dict):
            assert (folder / name).stat().st_size == rec['bytes']
    counts[folder.name] = {'files': len(files), 'manifest': pin}
for name in ['Target.lean', 'CONTRACT.md']:
    assert (proof / name).read_bytes() == (target_review / name).read_bytes()

old = (proof / 'proof-1/Proof.lean').read_text()
new = (proof / 'Proof.lean').read_text()
assert old.replace(':= by decide\n\ntheorem concrete_fixed_witness', ':= by\n  unfold consistent\n  decide\n\ntheorem concrete_fixed_witness') == new
for attempt, exit_code in [('proof-1', 1), ('proof-2', 0)]:
    directory = proof / attempt
    records = json.loads((directory / 'COMMANDS.json').read_text())
    assert len(records) == 1
    row = records[0]
    assert row['exit'] == exit_code and row['group_absent'] and row['safe_cleanup']
    assert row['seconds'] < 45
    inputs = json.loads((directory / 'INPUTS.json').read_text())
    for path, pin in inputs.items():
        p = Path(path)
        if (directory / p.name).exists():
            p = directory / p.name
        assert sha(p) == pin, path
assert 'sorryAx' in (proof / 'proof-1/strength.log').read_text()

names = re.findall(r'^  (\w+) :', (proof / 'Target.lean').read_text().split('structure Obligations : Prop where')[1], re.M) + ['obligations']
nonempty = {'old_repeated_child', 'old_nonzero_drift', 'obligations'}
expected = []
for name in names:
    suffix = 'depends on axioms: [propext, Quot.sound]' if name in nonempty else 'does not depend on any axioms'
    expected.append("'BaselineFeedback." + name + "' " + suffix)
assert (proof / 'proof-2/strength.log').read_text().splitlines() == expected

def retained_check(path, args):
    saved = sys.argv
    output = io.StringIO()
    try:
        sys.argv = [str(path), *args]
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(path), run_name='__main__')
    finally:
        sys.argv = saved
    return json.loads(output.getvalue())

proof_result = retained_check(proof / 'check.py', ['proof-2'])
probe_result = retained_check(probe / 'verify.py', [])
report = json.loads((probe / 'wptreport.json').read_text())
assert report['run_info']['browser_build_id'] == '20261007201254'
assert report['run_info']['browser_changeset'] == 'eb9a6e3a736802c8e080a76c44dc81f409d99d54'
raw_rows = [json.loads(line) for line in (probe / 'raw.log').read_text().splitlines() if line.startswith('{')]
observed = [json.loads(r['subtest'][4:]) for r in raw_rows if r.get('action') == 'test_status' and r.get('subtest', '').startswith('OBS ')]
assert observed == json.loads((probe / 'OBSERVATIONS.json').read_text())
assert all(r['status'] == 'PASS' for r in raw_rows if r.get('action') == 'test_status')
print(json.dumps({'authenticated': counts, 'target_exact': True, 'proof_delta_tactic_only': True,
                  'exact_audits': 11, 'retained_proof_check': proof_result,
                  'retained_probe_check': probe_result, 'raw_observations_exact': len(observed),
                  'fresh_compiler': False, 'fresh_browser': False}, indent=2))
