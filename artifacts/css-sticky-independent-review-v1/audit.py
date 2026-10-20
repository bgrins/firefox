import collections
import hashlib
import itertools
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
E = ROOT / 'evidence'
NAMES = ['css-sticky-auto-inset-fix-v1', 'css-sticky-writing-mode-fix-v1']
CPP = 'layout/generic/StickyScrollContainer.cpp'
PINS = ['001466c48760c278bc639cdb0ae2e8fe2ddb31886fd357f51d51536368b5fc85',
        'e5b36f33024f4ed453bd2e02ab233a84559fb237608f480efb1861cdd765a05f']
VARIANTS = dict(zip(['original', 'auto-only', 'writing-only', 'combined'], [
    '877d9e663bd76a750537c19fe02d2f357be6407bab87484366f0766799ccc817',
    'da6980060b11c467af91c5787702d3ebd218b00bac928848663f3d2e56212726',
    'e3b00298f82ffb33a9c36cb63990595afbb4813247fdc12ee2810f93d94ff23c',
    'fe79e921b6309b75e8d7f7c9292521bb27182567695f74bc6245710cfc75a91f']))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def decode_patch(p):
    files = {}
    current = None
    hunk = None
    for line in p.read_text().splitlines(keepends=True):
        if line.startswith('+++ b/'):
            current = line[6:].strip()
            files[current] = []
            hunk = None
        elif line.startswith(('--- ', 'diff --git ')):
            hunk = None
        elif line.startswith('@@ '):
            hunk = []
            files[current].append(hunk)
        elif hunk is not None and line[:1] in ' +-':
            hunk.append(line)
    return files

def apply(text, hunks, reverse=False):
    for hunk in hunks:
        old = ''.join(x[1:] for x in hunk if x[0] in (' +' if reverse else ' -'))
        new = ''.join(x[1:] for x in hunk if x[0] in (' -' if reverse else ' +'))
        assert text.count(old) == 1, ('nonunique hunk', old[:80])
        text = text.replace(old, new, 1)
    return text

# Explicit physical ends transcribed from CSS Writing Modes 4 logical-to-physical table.
ENDS = {
    ('horizontal-tb', 'ltr'): ('right', 'bottom'),
    ('horizontal-tb', 'rtl'): ('left', 'bottom'),
    ('vertical-rl', 'ltr'): ('left', 'bottom'),
    ('vertical-rl', 'rtl'): ('left', 'top'),
    ('vertical-lr', 'ltr'): ('right', 'bottom'),
    ('vertical-lr', 'rtl'): ('right', 'top'),
    ('sideways-rl', 'ltr'): ('left', 'bottom'),
    ('sideways-rl', 'rtl'): ('left', 'top'),
    ('sideways-lr', 'ltr'): ('right', 'top'),
    ('sideways-lr', 'rtl'): ('right', 'bottom'),
}

def position(size, near, far, scroll, end_near, normalize_auto):
    if near is None and far is None:
        return 200 - scroll
    a, b = near or 0, far or 0
    if normalize_auto or (near is not None and far is not None):
        deficit = max(0, size - (100 - a - b))
        if end_near:
            a -= deficit
        else:
            b -= deficit
    lo = a if near is not None else float('-inf')
    hi = 100 - b - size if far is not None else float('inf')
    # Feasible interval projected into containing-block bounds, then nearest normal position.
    lo = min(max(lo, -scroll), 600 - size - scroll)
    hi = min(max(hi, -scroll), 600 - size - scroll)
    assert lo <= hi
    return max(lo, min(hi, 200 - scroll))

def corpus(auto_fix, writing_fix):
    result = {}
    for axis, size, pair, scroll in itertools.product(
            ['vertical', 'horizontal-ltr', 'horizontal-rtl'], [60, 80, 200],
            [(None, -20), (None, 0), (None, 20), (0, 20), (20, None), (None, None)],
            [0, 160, 260, 400]):
        start, end = pair
        label = lambda v: 'auto' if v is None else str(v)
        name = f'{axis}, size {size}, start {label(start)}, end {label(end)}, scroll {scroll}'
        reverse = axis == 'horizontal-rtl'
        near, far = (end, start) if reverse else (start, end)
        result[('A', name)] = position(size, near, far, scroll, reverse, auto_fix)
    for (mode, direction), child, axis, size, pair, scroll in itertools.product(
            ENDS, ['horizontal-tb/ltr', 'vertical-rl/rtl', 'sideways-lr/ltr'],
            ['x', 'y'], [70, 200], [(0, 0), (20, 10), (-20, 10)], [0, 180, 400]):
        near, far = pair
        name = f'{mode}/{direction}, child {child}, {axis}, size {size}, insets {near}/{far}, scroll {scroll}'
        end = ENDS[(mode, direction)][axis == 'y']
        reduce_near = end in ('top', 'left') if writing_fix else axis == 'x' and direction == 'rtl'
        result[('B', name)] = position(size, near, far, scroll, reduce_near, auto_fix)
    assert len(result) == 1296
    return result

def audit():
    out = {'patches': [], 'runs': [], 'matrix_complete': False}
    fetch = json.loads((E / 'spec/FETCH.json').read_text())
    out['specs'] = []
    for item in fetch:
        if item.get('path') == 'spec/writing4.html':
            item = {**item, 'name': 'writing4', 'time_utc': item['retrieved']}
        if item.get('name') not in ['position3', 'writing4']:
            continue
        page = E / 'spec' / (item['name'] + '.html')
        assert sha(page) == item['sha256']
        anchor = 'sticky-pos' if item['name'] == 'position3' else 'logical-to-physical'
        assert f'id="{anchor}"' in page.read_text()
        out['specs'].append({**{k: item[k] for k in ['name', 'url', 'time_utc', 'sha256']}, 'verified_anchor': anchor})
    assert len(out['specs']) == 2
    sources = {}
    for v, pin in VARIANTS.items():
        p = E / NAMES[1] / f'variant-{v}.cpp'
        assert sha(p) == pin
        sources[v] = p.read_text()
    patches = []
    for folder, pin, variant in zip(NAMES, PINS, ['auto-only', 'writing-only']):
        p = E / folder / 'fix-candidate-v1.patch'
        assert sha(p) == pin
        patch = decode_patch(p)
        assert len(patch) == 2 and CPP in patch
        assert apply(sources['original'], patch[CPP]) == sources[variant]
        assert apply(sources[variant], patch[CPP], True) == sources['original']
        htmlpath = next(k for k in patch if k != CPP)
        html = ''.join(x[1:] for h in patch[htmlpath] for x in h if x.startswith('+'))
        snapshots = list((E / folder).glob('*sources/' + htmlpath.replace('/', '__')))
        assert snapshots and all(s.read_text() == html for s in snapshots if 'baseline-v1-sources' not in str(s) or folder == NAMES[1])
        out['patches'].append({'variant': variant, 'sha256': pin, 'files': list(patch), 'exact_forward_reverse': True})
        patches.append(patch[CPP])
    # H1 changes context shared with H2. Apply isolated edit blocks with unique exact matching.
    def edits(hunks):
        blocks = []
        for hunk in hunks:
            block = []
            for line in hunk + [' ']:
                if line[0] == ' ':
                    if block:
                        blocks.append(block)
                        block = []
                else:
                    block.append(line)
        return blocks
    assert apply(sources['auto-only'], edits(patches[1])) == sources['combined']
    assert apply(sources['writing-only'], edits(patches[0])) == sources['combined']
    out['commuting_exact_edits'] = True
    predictions = {v: corpus(v in ['auto-only', 'combined'], v in ['writing-only', 'combined']) for v in VARIANTS}
    desired = predictions['combined']
    rows = []
    for key, value in desired.items():
        rows.append({'test': key[0], 'name': key[1], 'expected': value,
                     'predicted_variants': {v: p[key] for v, p in predictions.items()}})
    (ROOT / 'ORACLE-ROWS.json').write_text(json.dumps(rows, indent=2) + '\n')
    for folder in NAMES:
        for receipt in sorted((E / folder).glob('*-receipt.json')):
            r = json.loads(receipt.read_text())
            raw = receipt.with_name(receipt.name.replace('-receipt.json', '.jsonl'))
            events = [json.loads(line) for line in raw.read_text().splitlines()]
            statuses = [e for e in events if e.get('action') in ['test_status', 'test_end']]
            assert statuses == r['statuses']
            assert r['pins_before'] == r['pins_after']
            assert r['absent_before'] == r['absent_after']
            assert sum(e.get('action') == 'suite_end' for e in events) == r['suite_end_count'] == 1
            counts = collections.defaultdict(collections.Counter)
            for e in statuses:
                counts[e['test']][e['status']] += 1
            assert dict(counts) == r['counts']
            pin = r['pins_before'][CPP]
            variant = next(v for v, h in VARIANTS.items() if h == pin)
            phase = r['phase']
            observed = {}
            historical_zero = []
            for e in statuses:
                if e['action'] != 'test_status':
                    continue
                test = 'A' if 'auto-inset-reduction' in e['test'] else 'B' if 'containing-block-writing-mode' in e['test'] else None
                if not test:
                    if e['status'] == 'FAIL':
                        assert 'single-axis-basic' in e['test'] and e.get('expected', 'FAIL') == 'FAIL'
                    else:
                        assert e['status'] == 'PASS'
                    continue
                key = (test, e['subtest'])
                assert key not in observed
                expected, predicted = desired[key], predictions[variant][key]
                if folder == NAMES[0] and phase == 'wpt-baseline-v1' and e.get('message') == 'assert_equals: expected -0 but got 0':
                    assert expected == predicted == 0
                    historical_zero.append(e['subtest'])
                else:
                    assert not e.get('known_intermittent')
                    assert e.get('expected', 'PASS') == 'PASS'
                    assert e['status'] == ('PASS' if expected == predicted else 'FAIL'), (phase, key, expected, predicted, e)
                    if expected != predicted:
                        assert e['message'] == f'assert_equals: expected {expected} but got {predicted}', (phase, e)
                observed[key] = e['status']
            for test in {k[0] for k in observed}:
                assert {k for k in observed if k[0] == test} == {k for k in desired if k[0] == test}
            checked_sources = 0
            snapdir = receipt.with_name(receipt.name.replace('-receipt.json', '-sources'))
            if snapdir.exists():
                for path, pin in r['pins_before'].items():
                    snap = snapdir / path.replace('/', '__')
                    assert snap.exists() or '/Contents/MacOS/' in path, ('missing retained input', receipt, path)
                    if snap.exists():
                        assert sha(snap) == pin, snap
                        checked_sources += 1
            out['runs'].append({'folder': folder, 'phase': phase, 'variant': variant,
                                'counts': dict(counts), 'oracle_cases_checked': len(observed),
                                'historical_negative_zero_only': historical_zero,
                                'retained_source_pins_checked': checked_sources,
                                'receipt_raw_exact': True, 'pins_and_absences_unchanged': True})
    matrix = [x for x in out['runs'] if x['phase'].startswith('matrix-')]
    out['matrix_complete'] = {x['variant'] for x in matrix} == set(VARIANTS)
    if out['matrix_complete']:
        d = E / NAMES[1]
        m = json.loads((d / 'INDEPENDENCE-MATRIX-v1.json').read_text())
        assert m['status'] == 'PASS' and m['failure'] is None
        assert m['fixed_inputs_before'] == m['fixed_inputs_after']
        assert m['variants'] == VARIANTS
        assert m['final_source_sha256'] == VARIANTS['combined']
        allpins = []
        for run in m['runs']:
            v = run['variant']
            rpath = d / f'matrix-{v}-v1-receipt.json'
            assert sha(rpath) == run['receipt_sha256']
            assert sha(d / f'matrix-{v}-v1-runner.log') == run['runner_log_sha256']
            assert sha(d / f'matrix-build-{v}-v1.log') == run['build']['log_sha256']
            assert run['build']['exit_code'] == 0
            assert run['build']['source_sha256'] == VARIANTS[v]
            r = json.loads(rpath.read_text())
            assert r['counts'] == run['counts'] and r['exit_code'] == run['wpt_exit']
            allpins.append(r['pins_before'])
        assert len(allpins) == 4
        allowed = {CPP, 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
                   'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'}
        assert all(set(p) == set(allpins[0]) for p in allpins)
        varied = {k for k in allpins[0] if len({p[k] for p in allpins}) > 1}
        assert varied == allowed
        out['matrix_integrity'] = {'builds_exit_zero': 4, 'fixed_project_pins': len(m['fixed_inputs_before']),
                                   'per_run_pins': len(allpins[0]), 'only_varied': sorted(varied),
                                   'scope': m['scope']}
    out['oracle_rows'] = len(rows)
    out['oracle_disagreements'] = {v: dict(collections.Counter(k[0] for k in desired if desired[k] != p[k])) for v, p in predictions.items()}
    out['regression_pairs'] = []
    for folder, suite in itertools.product(NAMES, ['regressions', 'timelines']):
        pair = [json.loads((E / folder / f'{suite}-{phase}-v1-receipt.json').read_text()) for phase in ['baseline', 'candidate']]
        def signature(r):
            return sorted((s['action'], s['test'], s.get('subtest', ''), s['status'],
                           s.get('expected', s['status']), tuple(s.get('known_intermittent', []))) for s in r['statuses'])
        assert signature(pair[0]) == signature(pair[1])
        assert pair[0]['absent_before'] == pair[1]['absent_before']
        a, b = (p['pins_before'] for p in pair)
        assert set(a) == set(b)
        changed = {k for k in a if a[k] != b[k]}
        assert changed == {CPP, 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
                           'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'}
        out['regression_pairs'].append({'folder': folder, 'suite': suite, 'statuses_and_expectations_identical': True,
                                        'pins': len(a), 'changed': sorted(changed)})
    (ROOT / 'AUDIT.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'runs': len(out['runs']), 'oracle_rows': len(rows), 'matrix_complete': out['matrix_complete'], 'oracle_disagreements': out['oracle_disagreements']}))

if __name__ == '__main__':
    audit()
