import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE.parent
TARGETS = {
    'cancellation': {
        'existing-child rem keyframes after root em cancellation with none',
        'root-pseudo rem keyframes after root em cancellation with none',
    },
    'depth': {
        f'existing-child rem keyframes through {depth} fixed ancestors after root em cancellation with none'
        for depth in (1, 4)
    },
}


def load(relative, page, count):
    path = ARTIFACTS / relative
    raw = path.read_bytes()
    events = [json.loads(line) for line in raw.splitlines() if line.strip()]
    assert not any(e.get('action') == 'crash' for e in events)
    selected = [e for e in events if e.get('test') == page]
    rows = [e for e in selected if e.get('action') == 'test_status']
    starts = [e for e in selected if e.get('action') == 'test_start']
    endings = [e for e in selected if e.get('action') == 'test_end']
    assert len(starts) == len(endings) == 1
    assert endings[0]['status'] == 'OK'
    assert len(rows) == count and len({e['subtest'] for e in rows}) == count
    keys = ('test', 'subtest', 'status', 'expected', 'known_intermittent', 'message')
    signatures = {e['subtest']: {k: e[k] for k in keys if k in e} for e in rows}
    end = {k: endings[0][k] for k in keys if k in endings[0]}
    return signatures, end, hashlib.sha256(raw).hexdigest()


result = {'scope': 'saved cancellation8 and depth4 callbacks', 'lanes': []}
for lane in json.loads((HERE / 'INPUTS.json').read_text()):
    original, old_end, old_sha = load(lane['original'], lane['page'], lane['count'])
    candidate, new_end, new_sha = load(lane['candidate'], lane['page'], lane['count'])
    assert original.keys() == candidate.keys() and old_end == new_end
    targets = TARGETS[lane['label']]
    assert {n for n, v in original.items() if v['status'] == 'FAIL'} == targets
    changed = []
    preserved = []
    for name, before in original.items():
        after = candidate[name]
        assert after['status'] == 'PASS'
        if name in targets:
            assert before.get('expected') == 'PASS'
            assert 'expected 46 +/- 0.06 but got 64' in before['message']
            changed.append({'before': before, 'after': after})
        else:
            assert before == after
            preserved.append(before)
    result['lanes'].append({**lane, 'original_sha256': old_sha,
                            'candidate_sha256': new_sha,
                            'changed': changed, 'preserved': preserved,
                            'preserved_ending': old_end})
assert sum(len(x['changed']) for x in result['lanes']) == 4
assert sum(len(x['preserved']) for x in result['lanes']) == 8
result['comparison_passed'] = True
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print('4 target FAIL-to-PASS changes; 8 unchanged PASS signatures; 2 unchanged OK endings')
