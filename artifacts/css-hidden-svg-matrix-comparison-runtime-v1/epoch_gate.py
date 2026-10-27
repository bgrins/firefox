def bind(ROOT, epoch, read, sha, authenticate, load):
    expected, state_before = read(epoch / 'FINAL.json'), read(epoch / 'STATE.json')
    receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
    assert state_before['status'] == 'terminal' and state_before['restored'] is True
    assert state_before['trace_complete'] is True and state_before['baseline_complete'] is True
    assert state_before['trace_build_exit'] == state_before['restore_build_exit'] == 0
    assert state_before['recovery_errors'] == [] and 'failure' not in state_before
    assert receipt['status'] == 'TRACE_AND_RESTORATION_VERIFIED' and receipt['exit'] == 0
    assert receipt['state_sha256'] == sha(epoch / 'STATE.json') and receipt['final_sha256'] == sha(epoch / 'FINAL.json')
    assert receipt['source_count'] == 49 and receipt['pin_count'] == 337
    assert receipt['staged_paths_preserved'] == 925 and receipt['native_modified_paths_preserved'] == 26
    assert receipt['installed112_source_and_test_ownership_preserved'] is True
    assert receipt['both_process_groups_cleaned'] is True and receipt['both_profiles_removed'] is True
    binaries = state_before['restored_binary_pins']
    assert binaries == receipt['restored_binary_pins'] == {
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox': 'a783e8f1cce2b4f3ca63e9a5dc1af4396e6af929669ac835e2171d96e76a5ee9',
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL': 'bce39299d0fe371e42177cc27fbebf75fb36ee7150f0f3fa0628403dace852ed'}
    assert expected == read(epoch / 'BEFORE.json')
    gate = load('svg_prior_installed_gate', epoch / 'epoch_gate.py')
    def need(ok, message):
        if not ok:
            raise RuntimeError(message)
    installed, installed_pins, _, config, installed_tests = gate.bind(
        ROOT, read(epoch / 'CONFIG.json'), read(epoch / 'EPOCH.json'), read, sha, authenticate, need)
    display = 'layout/painting/nsDisplayList.cpp'
    assert expected == {**installed, 'sources': {**installed['sources'],
                           display: '2af39c2e2b92d20891db704e6e60a7a6e56ef05158b3597b601074807862dea0'}}
    assert len(expected['sources']) == 49 and len(config['modified_native_paths']) == 26
    before_pins = read(epoch / 'BEFORE-PINS.json')
    assert before_pins == {**installed_pins, display: expected['sources'][display]}
    pins = read(epoch / 'FINAL-PINS.json')
    assert pins == {**before_pins, **binaries} and len(pins) == 337
    assert all(pins[n] == h for n, h in expected['sources'].items())
    config['guard_sources'] = sorted(expected['sources'])
    config['existing_tests'] = sorted(installed_tests)
    config['existing_test_pins'] = {n: item['sha256'] for n, item in installed_tests.items()}
    config['tracked_existing_tests'] = []
    config['install'] = {}
    return expected, pins, config, installed_tests
