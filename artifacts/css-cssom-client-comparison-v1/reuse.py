import json

def read(p):
    return json.loads(p.read_text())

def validate(wpt, load, sha, authenticate, current_baseline_resources):
    c, root = wpt.CONFIG, wpt.ROOT
    old = root / c['retained_baseline']
    reanalysis = root / c['reanalysis']
    authenticate(read(old / 'FILES.json'), old)
    authenticate(read(reanalysis / 'FILES.json'), reanalysis)
    old_config, old_resources = read(old / 'CONFIG.json'), read(old / 'RESOURCES.json')
    old_config['epoch'] = c['retained_baseline']
    old_owned, old_fixture = next(iter(old_config['install'].items()))
    gate = load('original104_gate', wpt.HERE / 'baseline_gate.py')
    old_tests = load('original104_tests', reanalysis / 'tests.py')
    try:
        wpt.CONFIG = old_config
        old104 = gate.validate(wpt, old_tests, old, reanalysis, read(old / 'STATE.json'),
                              old_resources, sha(old / old_fixture), sha)
    finally:
        wpt.CONFIG = c
    prior = root / c['retained_combined']
    authenticate(read(prior / 'FILES.json'), prior)
    pc, state = read(prior / 'CONFIG.json'), read(prior / 'STATE.json')
    wpt.need(state['status'] == 'terminal' and state['restored'] is True
             and state['restore_build_exit'] == 0 and not state['recovery_errors']
             and 'failure' not in state and state['paired_preservation_passed'] is True,
             'combined comparison terminal restoration')
    wpt.need(read(prior / 'BEFORE.json') == read(prior / 'FINAL.json'), 'combined original/final snapshot')
    receipt = read(prior / 'ROOT-FINAL-CHECK.json')
    wpt.need(receipt['state_sha256'] == sha(prior / 'STATE.json')
             and receipt['final_sha256'] == sha(prior / 'FINAL.json'), 'combined root receipt')
    phase = state['phases']['baseline']
    role = {**pc['head_pins'], **pc['baseline_pins']}
    wpt.need(phase['build_exit'] == 0 and phase['source_before_build'] == phase['source_after_build']
             and phase['source_after_build']['sources'] == role, 'fresh61 build/source role')
    wpt.need(all(phase['source_after_build'][k] == read(prior / 'BEFORE.json')[k]
             for k in ['head','index_diff_sha256','index_entries_sha256']), 'fresh61 historic HEAD/index')
    new_role = {**c['head_pins'], **c['baseline_pins']}
    wpt.need({n:h for n,h in new_role.items() if n != 'dom/base/Element.h'} == role
             and old_config['head_pins'] == pc['head_pins'] and old_config['baseline_pins'] == pc['baseline_pins'],
             'all archived native roles equal; added header checked as resource')
    prior_resources = read(prior / 'RESOURCES.json')
    prior_owned, prior_fixture = next(iter(pc['install'].items()))
    fresh_pins = {**prior_resources, **role, prior_owned:sha(prior / prior_fixture), **phase['binary_pins']}
    old_role_resources = {**old_resources, **old_config['head_pins'], **old_config['baseline_pins']}
    wpt.need(all(current_baseline_resources.get(n) == h for n,h in old_role_resources.items()
                 if n not in [old_owned, prior_owned]), 'old104 source/header/resource transfer')
    wpt.need(all(current_baseline_resources.get(n) == h for n,h in fresh_pins.items()
                 if n not in phase['binary_pins']), 'fresh61 source/header/resource transfer')
    wpt.need(fresh_pins['dom/base/Element.h'] == old_role_resources['dom/base/Element.h']
             == new_role['dom/base/Element.h'], 'explicit archived Element.h provenance')
    capture = prior / 'wpt-baseline'
    run = read(capture / 'RUN.json')
    raw = capture / 'raw.json'
    wpt.need(raw.is_file() and not raw.is_symlink() and raw.stat().st_size <= 128*1024*1024, 'fresh61 raw size')
    events = [json.loads(line) for line in raw.read_text().splitlines()]
    for key, action in [('rows','test_status'),('starts','test_start'),('ends','test_end')]:
        wpt.need(run[key] == [e for e in events if e.get('action') == action], 'fresh61 raw/RUN identity')
    names = pc['baseline_expected_subtests']
    wpt.need(len(run['rows']) == len({(e['test'],e['subtest']) for e in run['rows']}) == 61
             and len(run['starts']) == len(run['ends']) == len(names) == 5
             and {e['test'] for e in run['starts']} == {e['test'] for e in run['ends']} == set(names)
             and all(e['status'] == 'OK' for e in run['ends']), 'fresh61 exact files and rows')
    for test, expected in names.items():
        actual = [e['subtest'] for e in run['rows'] if e['test'] == test]
        wpt.need(len(actual) == len(expected) == len(set(expected)) and set(actual) == set(expected), 'fresh61 unique names')
    pt = load('fresh61_tests', prior / 'tests.py')
    wpt.need(sum(e.get('action') == 'suite_start' for e in events) == 1
             and sum(e.get('action') == 'suite_end' for e in events) == 1
             and pt.infrastructure_faults(events) == run['infrastructure_faults'] == []
             and run['complete'] is True and run['exit'] == 1
             and run['before'] == run['after'] == fresh_pins, 'fresh61 lifecycle/source/resources')
    wpt.need(read(capture / 'CLEANUP.json') == {'owned_group_absent':True,'errors':[]}, 'fresh61 cleanup')
    try:
        wpt.CONFIG = pc
        pt.require_phase(wpt, 'baseline', run)
    finally:
        wpt.CONFIG = c
    controls = [e for e in old104['rows'] if e['test'] in pc['expected_subtests']]
    wpt.need(len(controls) == 80, 'original80 selection')
    rows = run['rows'] + controls
    combined = read(prior / 'COMBINED-BASELINE.json')
    wpt.need(combined['rows'] == rows and combined['retained_runtime'] == c['retained_baseline']
             and combined['retained_reanalysis'] == c['reanalysis'], 'full141 composition provenance')
    wpt.need(len(rows) == len({(e['test'],e['subtest']) for e in rows}) == 141
             and set(pc['expected_subtests']) <= set(c['expected_subtests'])
             and all(c['expected_subtests'][n] == v for n,v in pc['expected_subtests'].items()), 'unchanged141 identity roster')
    wpt.need({s:sum(e['status']==s for e in rows) for s in ['PASS','FAIL']} == {'PASS':129,'FAIL':12}, 'retained141 outcomes')
    return {'rows':rows,'runtime':c['retained_combined'],'combined_sha256':sha(prior/'COMBINED-BASELINE.json'),
            'original104_runtime':c['retained_baseline'],'reanalysis':c['reanalysis'],
            'source_header_resource_transfer':True}
