def bind(ROOT, epoch, read, sha, authenticate, load):
    state = read(epoch / 'STATE.json')
    receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
    final = read(epoch / 'FINAL.json')
    settings = read(epoch / 'CONFIG.json')
    assert state['status'] == 'terminal' and state['complete'] and state['preserved']
    assert not state['native_changes'] and 'failure' not in state and 'preservation_failure' not in state
    assert state['counts'] == receipt['counts'] == {'PASS': 2, 'FAIL': 8}
    assert state['calibrated'] == receipt['calibrated'] == 10
    assert receipt['status'] == 'REPRODUCED_AND_PRESERVED' and receipt['exit'] == 0
    assert receipt['state_sha256'] == sha(epoch / 'STATE.json')
    assert receipt['final_sha256'] == sha(epoch / 'FINAL.json')
    assert final == read(epoch / 'BEFORE.json')
    installed = ROOT / settings['epoch']
    assert sha(installed / 'FILES.json') == settings['epoch_manifest_sha256']
    authenticate(read(installed / 'FILES.json'), installed)
    assert sha(installed / 'ROOT-FINAL-CHECK.json') == settings['root_receipt_sha256']
    adapter = load('installed_viewport_gate', epoch / 'epoch_gate.py')
    def need(condition, message):
        if not condition:
            raise RuntimeError(message)
    _, old_receipt, expected, pins, c, identities = adapter.bind(
        ROOT, installed, settings, read, sha, authenticate, load, need)
    assert final['snapshot'] == expected
    assert final['pins'] == {**pins, settings['owned_metadata']: None}
    assert receipt['installed_tests'] == identities and len(identities) == 7
    assert receipt['installed_binary_pins'] == old_receipt['installed_binary_pins']
    assert receipt['source_count'] == len(expected['sources']) == 53
    assert receipt['pin_count'] == len(final['pins']) == 387
    assert receipt['native_modified_paths'] == len(c['modified_native_paths']) == 30
    assert receipt['staged_paths'] == 925
    run = read(epoch / 'wpt-viewport/RUN.json')
    assert run['complete'] and run['before'] == run['after'] and run['exit'] == 1
    assert run['before'] == {**final['pins'], settings['owned_test']: sha(epoch / 'fixture.html')}
    assert read(epoch / 'wpt-viewport/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    c['must_be_absent'] = sorted(set(c['must_be_absent']) | {settings['owned_test']})
    return expected, final['pins'], c, identities
