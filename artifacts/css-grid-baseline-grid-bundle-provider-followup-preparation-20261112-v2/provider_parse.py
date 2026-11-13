import argparse
import collections
import json
import re
from pathlib import Path

STAGES = {'measure-enter', 'cache-hit', 'post-finish', 'capture-begin',
          'capture-end', 'natural-before', 'natural-after', 'grid-before',
          'grid-after', 'column-entry', 'column-iterator', 'checkbox-clean',
          'text-clean', 'single-initialized', 'export-before', 'export-after'}
PROVIDERS = {'column-entry', 'column-iterator', 'checkbox-clean', 'text-clean',
             'single-initialized'}
IDS = {f'{prefix}-{k}-{s}' for prefix in ['gse', 'gsi'] for k in ['text', 'checkbox', 'empty-columns', 'spanning-columns']
       for s in ['visible', 'hidden-grid', 'fragmented']}
PHASES = {'seed', 'reveal', 'reveal-empty'} | {
    f'edit{i}{suffix}' for i in range(4) for suffix in ['', '-empty', '-filled']}
FIELDS = ('seq stage id phase request capture frame owner parent type dirty '
          'children subtree inreflow empty prev next hidden contain '
          'v0 v1 v2 v3 v4 v5').split()
NUMBERS = set(FIELDS) - {'stage', 'id', 'phase', 'request', 'frame', 'owner', 'parent'}


def parse(text):
    assert 'TRUNCATED' not in text, 'truncated stream'
    rows = []
    for line in text.splitlines():
        assert len(line.encode('utf-8')) <= 1024, 'oversized provider record'
        assert len(rows) < 32768, 'provider record cap'
        assert line.startswith('GRIDSNAPSHOT '), 'not a raw extracted trace record'
        pairs = [p.split('=', 1) for p in line[len('GRIDSNAPSHOT '):].split()]
        assert all(len(p) == 2 for p in pairs) and [p[0] for p in pairs] == FIELDS
        row = dict(pairs)
        for k in NUMBERS:
            assert re.fullmatch(r'-?\d+', row[k]), k
            row[k] = int(row[k])
        assert row['seq'] == len(rows) + 1, 'missing, duplicate or mixed process sequence'
        assert row['stage'] in STAGES and row['id'] in IDS
        assert row['phase'] in PHASES
        assert row['request'] in {'outside', 'content', 'baseline', 'unspecified'}
        for k in ['frame', 'owner', 'parent']:
            assert re.fullmatch(r'0x[0-9a-f]+|\(nil\)', row[k]), k
        for k in ['dirty', 'children', 'subtree', 'inreflow', 'empty', 'prev', 'next', 'hidden', 'contain']:
            assert row[k] in [0, 1], k
        rows.append(row)
    assert rows, 'no records'
    captures, violations, outside = {}, [], []
    exports, export_pairs, export_associated = {}, [], []
    for r in rows:
        c, stage = r['capture'], r['stage']
        if stage.startswith('export-'):
            assert not c, 'export occurred inside Capture unexpectedly'
            assert r['frame'] == r['owner'], 'outside export owner mismatch'
            key = (r['frame'], r['id'], r['phase'], r['v0'], r['v1'])
            if stage == 'export-before':
                assert key not in exports
                exports[key] = r
            else:
                assert key in exports, 'missing export begin'
                before = exports.pop(key)
                assert all(before[k] == r[k] for k in ['request', 'v2', 'v3'])
                export_pairs.append({'before': before, 'after': r})
        if c:
            if stage == 'capture-begin':
                assert c not in captures, 'duplicate capture'
                assert r['v2'] in range(7), 'invalid demand'
                captures[c] = {'entry': r, 'closed': False, 'query': None, 'queries': []}
            assert c in captures and not captures[c]['closed'], 'missing begin or event after end'
            cap = captures[c]
            assert all(r[k] == cap['entry'][k] for k in ['id', 'phase', 'request', 'owner'])
            if stage in {'capture-begin', 'capture-end', 'natural-before', 'natural-after', 'grid-before', 'grid-after'}:
                assert r['frame'] == r['owner'], 'capture/query frame differs from owner'
            if stage in PROVIDERS:
                assert cap['query'] == ('natural', r['v0']), 'provider outside matching natural query'
            if stage == 'natural-after':
                assert r['v1'] in (0, 1), 'natural presence is not boolean'
                assert r['v1'] or r['v2'] == 0, 'absent natural answer has nonzero value'
                cap['natural_present'] = r['v1']
            if stage == 'grid-before':
                assert r['v1'] in [0, 1], 'grid axis invalid'
            if stage == 'grid-after':
                assert cap['query'] == ('grid', r['v0'], r['v2']), 'grid return axis mismatch'
            if stage.endswith('-before'):
                assert cap['query'] is None
                cap['query'] = (stage.split('-')[0], r['v0'])
                if stage == 'grid-before':
                    cap['query'] += (r['v1'],)
            if stage.endswith('-after'):
                expected_pair = (stage.split('-')[0], r['v0'])
                if stage == 'grid-after':
                    expected_pair += (r['v2'],)
                assert cap['query'] == expected_pair, 'query pair mismatch'
                cap['queries'].append(cap['query'])
                cap['query'] = None
            if stage == 'capture-end':
                entry = cap['entry']
                d = entry['v2']
                assert all(entry[k] in [0, 1] for k in ['v3', 'v4', 'v5'])
                assert entry['v4'] == 1 - entry['subtree'], 'clean flag disagrees with subtree'
                assert d < 3 or entry['v5'] == 1
                bundled = d >= 3 and entry['v3'] == 1 and entry['v4'] == 1
                expected = {0: [], 1: [('natural', 0)], 2: [('natural', 1)],
                            3: [('grid', 0, 1)], 4: [('grid', 1, 1)],
                            5: [('grid', 0, 0)], 6: [('grid', 1, 0)]}[d]
                if bundled:
                    expected = [('grid', 0, 1), ('grid', 1, 1), ('grid', 0, 0), ('grid', 1, 0)]
                assert r['v0'] == int(bundled) and r['v1'] in [0, 1] and r['v2'] == d
                if d in (1, 2):
                    assert cap.get('natural_present') == r['v1'], 'natural/capture presence mismatch'
                assert d != 0 or r['v1'] == 0
                assert d < 3 or r['v1'] == 1
                assert cap['query'] is None
                assert cap['queries'] == expected, 'query sequence does not match guarded capture'
                cap['bundle'] = bundled
                cap['present'] = r['v1']
                cap['closed'] = True
        elif stage in {'capture-begin', 'capture-end', 'natural-before', 'natural-after', 'grid-before', 'grid-after'}:
            raise AssertionError('capture marker without id')
        bad = (stage in {'checkbox-clean', 'text-clean', 'single-initialized'} and r['v1'] == 0) or (
            stage == 'column-iterator' and (r['v1'] == 0 or r['v2'] == 0))
        if bad:
            (violations if c else outside).append(r)
            if not c:
                matching = [x for key, x in exports.items() if key[:4] == (r['frame'], r['id'], r['phase'], r['v0'])]
                assert len(matching) <= 1
                export_associated.append({'predicate': r, 'export_before': matching[0] if matching else None})
    assert all(c['closed'] for c in captures.values()), 'unfinished capture'
    assert not exports, 'unfinished export pair'
    coverage = {}
    for i in sorted(IDS):
        entry = [c['entry'] for c in captures.values() if c['entry']['id'] == i]
        coverage[i] = {
            'records': sum(r['id'] == i for r in rows), 'captures': len(entry),
            'requests': dict(collections.Counter(c['request'] for c in entry)),
            'phases': dict(collections.Counter(c['phase'] for c in entry)),
            'provider_stages': dict(collections.Counter(r['stage'] for r in rows
                if r['id'] == i and r['capture'] and r['stage'] in PROVIDERS))}
    return {'status': 'PARSED complete single-process stream; coverage is observational',
            'records': len(rows), 'captures': len(captures),
            'stages': dict(collections.Counter(r['stage'] for r in rows)),
            'coverage': coverage, 'capture_predicate_violations': violations,
            'outside_capture_predicate_violations': outside,
            'outside_violation_export_association': export_associated,
            'export_pairs': export_pairs,
            'missing_capture_cases': [i for i in sorted(IDS) if not coverage[i]['captures']],
            'captures_detail': {str(k): v for k, v in captures.items()}}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('trace', type=Path)
    p.add_argument('out', type=Path)
    a = p.parse_args()
    a.out.write_text(json.dumps(parse(a.trace.read_text()), indent=2) + '\n')
