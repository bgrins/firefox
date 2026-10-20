import collections
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
paths = {
 'pair.json': 'css-animation-interpolation-taint-paired-root-v1/PAIR.json',
 'pair-run.py': 'css-animation-interpolation-taint-paired-root-v1/run.py',
 'supplemental.json': 'css-animation-interpolation-taint-paired-root-v1/SUPPLEMENTAL-PINS.json',
 'prior79.json': 'css-animation-base-metadata-paired-root-v1/PAIR.json',
 'prior79-raw.json': 'css-animation-base-metadata-paired-root-v1/candidate/raw.json',
 'diagnostic.json': 'css-animation-interpolation-taint-root-v1/RUN.json',
 'diagnostic-raw.json': 'css-animation-interpolation-taint-root-v1/raw.json',
 'focused-raw.json': 'css-animation-interpolation-taint-paired-root-v1/baseline/raw.json',
 'candidate-raw.json': 'css-animation-interpolation-taint-paired-root-v1/candidate/raw.json',
 'packaging.json': 'css-animation-interpolation-taint-final-root-v1/PACKAGING.json',
 'package.py': 'css-animation-interpolation-taint-final-root-v1/package.py',
 'help-transfer.json': 'css-animation-interpolation-taint-final-root-v1/HELP-LINK-TRANSFER.json',
 'landing.html': 'css-animation-interpolation-taint-final-root-v1/landing.html',
 'stack.patch': 'css-animation-interpolation-taint-final-root-v1/stack-native-wpt.patch',
 'standalone.patch': 'css-animation-interpolation-taint-final-root-v1/standalone-native-wpt.patch',
}
def sha(b):
    return hashlib.sha256(b).hexdigest()
def read(name):
    return json.loads((EVIDENCE / name).read_text())
for target, source in paths.items():
    (EVIDENCE / target).write_bytes((ROOT / 'artifacts' / source).read_bytes())

def raw(name):
    events = [json.loads(line) for line in (EVIDENCE / name).read_text().splitlines()]
    assert sum(e.get('action') == 'suite_start' for e in events) == 1
    assert sum(e.get('action') == 'suite_end' for e in events) == 1
    rows = [e for e in events if e.get('action') == 'test_status']
    ends = [e for e in events if e.get('action') == 'test_end']
    assert len({(r['test'], r['subtest']) for r in rows}) == len(rows)
    assert len({r['test'] for r in ends}) == len(ends)
    assert {r['test'] for r in rows} == {r['test'] for r in ends}
    assert all(e['status'] == 'OK' for e in ends)
    return rows, ends
pair, prior, diagnostic = read('pair.json'), read('prior79.json'), read('diagnostic.json')
sources = [('prior79-raw.json', prior['candidate'], 189, 14),
           ('diagnostic-raw.json', diagnostic, 40, 1),
           ('focused-raw.json', pair['baseline'], 24, 1),
           ('candidate-raw.json', pair['candidate'], 253, 16)]
before, before_ends = [], []
for i, (name, receipt, n, h) in enumerate(sources):
    rows, ends = raw(name)
    assert rows == receipt['rows'] and ends == receipt['harness']
    assert len(rows) == n and len(ends) == h
    if i < 3:
        before += rows
        before_ends += ends
    else:
        after, after_ends = rows, ends
key = lambda r: (r['test'], r['subtest'])
bm, am = {key(r): r for r in before}, {key(r): r for r in after}
assert len(bm) == len(before) == 253 and bm.keys() == am.keys()
assert {r['test'] for r in before_ends} == {r['test'] for r in after_ends}
assert len(before_ends) == len({r['test'] for r in before_ends}) == 16
changes = [{'identity': list(k), 'before': bm[k]['status'], 'after': am[k]['status']} for k in bm if bm[k]['status'] != am[k]['status']]
assert changes == pair['changes'] and len(changes) == 5
expected_changes = {("/css/css-values/animation-interpolation-attribute-taint-probe.html", f"clean-to-tainted, progress {progress}, bundle") for progress in ["0.25", "0.75", "1"]}
expected_changes |= {("/css/css-values/registered-number-interpolation-attr-taint.html", f"clean-to-tainted, progress {progress}, bundle") for progress in ["0.25", "0.75"]}
assert {tuple(c['identity']) for c in changes} == expected_changes
expected_focused = {f"Static {value}, {observer} observer" for observer in ["bundle", "direct"] for value in ["initial", "inherit", "8", "12"]}
expected_focused |= {f"{direction}, progress {progress}, {observer}" for direction in ["clean-to-clean", "clean-to-tainted", "tainted-to-clean", "tainted-to-tainted"] for progress in ["0.25", "0.75"] for observer in ["bundle", "direct"]}
assert {r['subtest'] for r in pair['baseline']['rows']} == expected_focused
assert all(c['before'] == 'FAIL' and c['after'] == 'PASS' for c in changes)
assert collections.Counter(r['status'] for r in before) == {'PASS': 248, 'FAIL': 5}
assert all(r['status'] == 'PASS' for r in after)
assert all('URL' in bm[tuple(c['identity'])].get('message', '') for c in changes)
assert pair['build']['exit'] == pair['format']['exit'] == pair['candidate']['exit'] == 0
assert pair['baseline']['exit'] == 1 and pair['complete'] and pair['stable_after'] and pair['baseline']['stable']
assert prior['complete'] and prior['stable_after'] and diagnostic['stable']
for earlier in [prior['pins_after'], diagnostic['pins']]:
    for k in earlier.keys() & pair['pins_before'].keys():
        assert earlier[k] == pair['pins_before'][k], k
changed_pins = [k for k in pair['pins_before'] if pair['pins_before'][k] != pair['pins_after'][k]]
assert set(changed_pins) == {'servo/components/style/properties_and_values/value.rs', 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox', 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL'}
proposal = ROOT / 'artifacts/css-animation-interpolation-taint-native-independent-v1/proposal'
tested = (proposal / 'registered-number-interpolation-attr-taint.html').read_bytes()
landing = (EVIDENCE / 'landing.html').read_bytes()
old = b'css-properties-values-api-1/#animation-behavior"'
new = b'css-properties-values-api-1/#animation-behavior-of-custom-properties"'
assert tested.count(old) == 1 and tested.replace(old, new) == landing
assert sha(landing) == '5d4b616f048f17ac8a7cd1bdc56b15a4a7854eb20333fdfc52f6d33203dcf2cd'
assert read('help-transfer.json')['tested_sha256'] == sha(tested)
assert read('help-transfer.json')['final_sha256'] == sha(landing)
patch_checks = []
scratch = HERE / 'apply-check'
for mode, original, candidate in [('stack', 'value.original.rs', 'value.candidate.rs'), ('standalone', 'value.upstream.rs', 'value.upstream-candidate.rs')]:
    info = read('packaging.json')[mode]
    patch = EVIDENCE / (mode + '.patch')
    assert sha(patch.read_bytes()) == info['sha256']
    assert info['exact_apply_reverse']
    tree = scratch / mode
    src = tree / 'servo/components/style/properties_and_values/value.rs'
    test = tree / 'testing/web-platform/tests/css/css-values/registered-number-interpolation-attr-taint.html'
    src.parent.mkdir(parents=True)
    src.write_bytes((proposal / 'source' / original).read_bytes())
    for reverse in [False, True]:
        cmd = ['patch', '--batch', '--fuzz=0', '-p1'] + (['-R'] if reverse else []) + ['-i', str(patch)]
        r = subprocess.run(cmd, cwd=tree, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert src.read_bytes() == (proposal / 'source' / (original if reverse else candidate)).read_bytes()
        assert (not test.exists()) if reverse else test.read_bytes() == landing
        assert {str(f.relative_to(tree)) for f in tree.rglob('*') if f.is_file()} == ({str(src.relative_to(tree))} if reverse else set(info['paths']))
        patch_checks.append({'mode': mode, 'reverse': reverse, 'exit': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr, 'exact_roster_and_bytes': True})
size = sum(f.stat().st_size for f in scratch.rglob('*') if f.is_file())
shutil.rmtree(scratch)
assert all((EVIDENCE / target).read_bytes() == (ROOT / 'artifacts' / source).read_bytes() for target, source in paths.items())
result = {'baseline_sources': [189, 40, 24], 'joined_baseline': {'PASS': 248, 'FAIL': 5}, 'candidate': {'PASS': 253, 'harness_OK': 16}, 'changes': changes, 'pin_roster': len(pair['pins_before']), 'changed_pins': changed_pins, 'help_transfer_exact': True, 'whole_two_file_apply_reverse': patch_checks, 'removed_generated_bytes': size, 'runtime_scope': 'Historical baseline joins matched at common pins; candidate build/run fresh. No isolated upstream runtime. PASS status is not full observation equality.'}
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS independent raw joins, pins, exact help transfer and four two-file apply/reverse checks')
