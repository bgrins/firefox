import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def authenticate(folder, pin):
    assert sha(folder / 'FILES.json') == pin
    for name, record in read(folder / 'FILES.json').items():
        path = folder / name
        assert not path.is_symlink() and path.is_file()
        assert sha(path) == (record if isinstance(record, str) else record['sha256'])


def generation(index, value, leaf=False):
    assert value in ((0, 1) if leaf else (16, 32))
    encoded = bool(value) if leaf else value == 32
    return encoded != bool(index % 2)


def project(depth, snapshot):
    rows = [{'index': 0, 'property': 'root font', 'value': snapshot['rootFont'],
             'generation': generation(0, snapshot['rootFont'])}]
    for index, node in enumerate(snapshot['nodes'], 1):
        prop = 'lineHeight' if index % 2 else 'font'
        rows.append({'index': index, 'property': prop, 'value': node[prop],
                     'generation': generation(index, node[prop]),
                     'css_duration_ms': node['duration'], 'effect_duration_ms': node['timing']['duration']})
    rows.append({'index': depth + 1, 'property': 'opacity', 'value': snapshot['opacity'],
                 'generation': generation(depth + 1, snapshot['opacity'], True),
                 'css_duration_ms': snapshot['leafDuration'], 'effect_duration_ms': snapshot['leaf']['duration']})
    bits = [row['generation'] for row in rows]
    mismatches = [row for row in rows[1:] if row['css_duration_ms'] != row['effect_duration_ms']]
    return {'nodes': rows, 'generation_bits': bits, 'all_new': all(bits),
            'output_matches_prefix_through_stage_1': bits == [True, True] + [False] * depth,
            'first_css_effect_duration_mismatch': mismatches[0] if mismatches else None}


def main():
    refs = read(HERE / 'REFERENCES.json')
    for name, pin in refs.items():
        assert sha(ROOT / name) == pin
    runtime = ROOT / 'artifacts/css-contextual-duration-finite-depth-original-runtime-1'
    authenticate(runtime, refs[str((runtime / 'FILES.json').relative_to(ROOT))])
    model = ROOT / 'artifacts/css-contextual-duration-finite-depth-oracle-model-v1'
    authenticate(model, refs[str((model / 'FILES.json').relative_to(ROOT))])
    assessment = read(runtime / 'original-wpt/ASSESSMENT.json')
    result = {'actual_statuses': [row['status'] for row in assessment['rows']],
              'actual_endings': [row['status'] for row in assessment['ends']],
              'projection_only': True, 'native_round_count_inferred': False,
              'queue_or_flight_state_inferred': False, 'depths': {}}
    binding = read(runtime / 'PROGRESS-BINDING.json')
    collection = read(runtime / 'PROGRESS-RECORDS.json')
    assert collection['complete'] and not collection['errors'] and not collection['missing']
    for depth in (1, 2, 4, 8):
        filename = f'depth-{depth}.json'
        path = runtime / 'progress-records' / filename
        assert sha(path) == collection['records'][filename]['sha256']
        record = read(path)
        assert record['kind'] == f'depth-{depth}' and record['run_id'] == binding['run_id']
        modes = {}
        for mode, item in record['observations'].items():
            assert item['mode'] == mode and item['depth'] == depth
            modes[mode] = {phase: project(depth, item[phase]) for phase in
                           ('literalInitial', 'initial', 'beforeMembership', 'afterMembership')}
            modes[mode]['leaf_samples'] = [dict(sample, generation=generation(depth + 1, sample['opacity'], True))
                                           for sample in item['samples']]
            modes[mode]['membership'] = item['membership']
            modes[mode]['detail_snapshots_equal'] = item['beforeMembership'] == item['afterMembership']
        result['depths'][str(depth)] = modes
    assert len(sys.argv) == 2
    with Path(sys.argv[1]).open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({depth: value['contextual']['beforeMembership'] for depth, value in result['depths'].items()}))


if __name__ == '__main__':
    main()
