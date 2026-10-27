import json


def validate(wpt, tests, previous, reanalysis, epoch, resources, fixture, sha):
    c = wpt.CONFIG
    receipt = json.loads((reanalysis / 'BASELINE-REVALIDATED.json').read_text())
    wpt.need(receipt['status'] == 'BASELINE_REVALIDATED' and receipt['original_complete'] is False
             and receipt['revalidated_complete'] is True and receipt['runtime_failure_preserved'] is True
             and receipt['runtime'] == c['epoch'] and receipt['candidate_observed'] is False
             and receipt['native_acceptance'] is False, 'independent baseline reanalysis gate')
    capture = previous / 'wpt-baseline'
    wpt.need(sha(capture / 'RUN.json') == receipt['run_sha256']
             and sha(capture / 'raw.json') == receipt['raw_sha256']
             and sha(previous / 'DRAFT-FILES.json') == receipt['draft_sha256']
             and sha(reanalysis / 'tests.py') == receipt['corrected_parser_sha256']
             and sha(reanalysis / 'BASELINE-BUILD.json') == receipt['build_phase_sha256'], 'baseline reanalysis inputs')
    run = json.loads((capture / 'RUN.json').read_text())
    phase = json.loads((reanalysis / 'BASELINE-BUILD.json').read_text())
    wpt.need(phase == epoch['phases']['baseline'] and phase['build_exit'] == 0
             and phase['source_before_build'] == phase['source_after_build']
             and phase['source_after_build']['sources'] == {**c['head_pins'], **c['baseline_pins']}, 'captured baseline source/build role')
    old = json.loads((previous / 'BEFORE.json').read_text())
    wpt.need(all(phase['source_after_build'][k] == old[k]
             for k in ('head', 'index_diff_sha256', 'index_entries_sha256')), 'baseline HEAD/index join')
    owned = next(iter(c['install']))
    expected_pins = {**resources, **c['head_pins'], **c['baseline_pins'],
                     owned: fixture, **phase['binary_pins']}
    wpt.need(run['before'] == run['after'] == expected_pins
             and len(expected_pins) == 307 and receipt['baseline_binary_pins'] == phase['binary_pins'], 'baseline complete resource/source/binary map')
    raw = capture / 'raw.json'
    wpt.need(raw.is_file() and not raw.is_symlink() and raw.stat().st_size <= 128 * 1024 * 1024, 'baseline raw ownership/size')
    events = [json.loads(line) for line in raw.read_text().splitlines()]
    for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
        wpt.need(run[key] == [e for e in events if e.get('action') == action], 'baseline raw/result correspondence')
    names = c['expected_subtests']
    wpt.need(len(run['rows']) == len({(r['test'], r['subtest']) for r in run['rows']}) == 104
             and len(run['starts']) == len(run['ends']) == len(names) == 9
             and {r['test'] for r in run['starts']} == {r['test'] for r in run['ends']} == set(names)
             and all(r['status'] == 'OK' for r in run['ends']), 'baseline exact identities/harnesses')
    for test, expected in names.items():
        actual = [r['subtest'] for r in run['rows'] if r['test'] == test]
        wpt.need(len(actual) == len(expected) == len(set(expected)) and set(actual) == set(expected), 'baseline exact unique subtests')
    wpt.need(sum(e.get('action') == 'suite_start' for e in events) == 1
             and sum(e.get('action') == 'suite_end' for e in events) == 1
             and tests.infrastructure_faults(events) == run['infrastructure_faults'] == [], 'baseline infrastructure')
    wpt.need(run['exit'] == 1 and run['complete'] is False
             and json.loads((capture / 'CLEANUP.json').read_text()) == {'owned_group_absent': True, 'errors': []}, 'original baseline completion and cleanup')
    tests.require_phase(wpt, 'baseline', run)
    main = next(iter(names))
    wpt.need([r for r in run['rows'] if r['test'] != main and r['status'] == 'FAIL'] == receipt['control_failures']
             and {status: sum(r['status'] == status for r in run['rows']) for status in ('PASS', 'FAIL')} == {'PASS': 94, 'FAIL': 10}, 'retained baseline outcome identity')
    return run
