import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def run(root, here, output, policy, env, verify, owned, cancelled):
    spec = importlib.util.spec_from_file_location('clean_original_wpt', here / 'wpt.py')
    wpt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wpt)
    initial = verify()
    wpt.save(output / 'PHASES-PRE.json', initial)
    rows, endings, results = [], [], {}
    build = read(output / 'original-build/RESULT.json')
    for lane in policy['lane_order']:
        phase = output / ('original-wpt-' + lane)
        results[lane] = wpt.run(root, here, phase, 'original', policy, env, verify, owned, cancelled, lane=lane)
        assessment = read(phase / 'ASSESSMENT.json')
        settings = policy['wpt_lanes'][lane]
        assert assessment['complete'] and len(assessment['rows']) == settings['expected_subtest_count']
        assert len(assessment['ends']) == settings['expected_page_count']
        assert all(row['status'] in ('PASS', 'FAIL') for row in assessment['rows'])
        rows.extend(assessment['rows'])
        endings.extend(assessment['ends'])
        assert not owned and read(phase / 'PRE.json') == read(phase / 'POST.json') == initial
        metadata = read(phase / 'APPLICATION-METADATA.json')
        assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
        assert metadata['revision'] == metadata['build_revision'] == policy['head']
        assert metadata['source_role'] == 'original'
        assert build['binaries'] == read(phase / 'BINARY-PINS.json')
        assert verify() == initial
    assert len(rows) == 77 and len(endings) == 12
    assert len({(row['test'], row['subtest']) for row in rows}) == 77
    assert len({row['test'] for row in endings}) == 12
    assert results['ordinary']['zoom_observation_sha256'] is not None
    assert build['native_sources'] == {name: row['candidate_sha256'] for name, row in read(here / 'SOURCE-ROLES.json').items()}
    wpt.save(output / 'OUTCOMES.json', {
        'callbacks_passed': sum(row['status'] == 'PASS' for row in rows),
        'callbacks_failed': sum(row['status'] == 'FAIL' for row in rows),
        'rows': rows, 'endings': endings, 'lanes': results,
        'zoom_target_correctness': None, 'provider_source_role': 'clean-original', 'native_acceptance': False,
    })
    wpt.save(output / 'PHASES-POST.json', initial)
    return results
