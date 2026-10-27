def bind(ROOT, epoch, settings, read, sha, authenticate, load, need):
    state = read(epoch / 'STATE.json')
    receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
    final = read(epoch / 'FINAL.json')
    need(state['status'] == 'terminal' and state['complete'] is False and state['preserved'] is True
         and state['native_changes'] is False and state['failure'] == {
             'type':'RuntimeError','message':'calibration/control/later/unpredicted failure'}, 'preserved rejected predecessor')
    need(receipt['status'] == 'PRESERVED_DIAGNOSTIC_REJECTED' and receipt['exit'] == 1
         and receipt['state_sha256'] == sha(epoch / 'STATE.json')
         and receipt['final_sha256'] == sha(epoch / 'FINAL.json')
         and receipt['unpredicted_first_value'] == 30 and receipt['accepted_bug'] is False
         and receipt['owned_fixture_removed'] is True, 'actual rejected diagnostic receipt')
    need(read(epoch / 'BEFORE.json') == final and len(final['pins']) == 396, 'preserved396 roles')
    prior = read(epoch / 'CONFIG.json')
    installed = ROOT / prior['epoch']
    need(sha(installed / 'FILES.json') == prior['epoch_manifest_sha256']
         and sha(installed / 'ROOT-FINAL-CHECK.json') == prior['root_receipt_sha256'], 'installed predecessor seals')
    authenticate(read(installed / 'FILES.json'), installed)
    gate = load('reviewed_installed_gate', ROOT / 'artifacts/css-svg-length-hidden-provider-browser-v1/epoch_gate.py')
    _, installed_receipt, expected, oldpins, c, tests = gate.bind(
        ROOT, installed, prior, read, sha, authenticate, load, need)
    oldpins[prior['owned_metadata']] = None
    need(final == {'snapshot':expected,'pins':oldpins}
         and receipt['installed_tests'] == installed_receipt['installed_tests']
         and receipt['installed_binary_pins'] == installed_receipt['installed_binary_pins']
         and receipt['source_count'] == 53 and receipt['native_modified_paths'] == 30
         and receipt['staged_paths'] == 925, 'installed and rejected epoch join')
    need(prior['owned_test'] not in oldpins and prior['owned_test'] not in tests, 'old owned input role')
    c['must_be_absent'] = sorted(set(c['must_be_absent']) | {prior['owned_test']})
    pins = dict(oldpins)
    for name, item in read(ROOT / settings['proposal'] / 'SOURCE-PINS.json').items():
        need(not name.startswith('artifacts/') and len(item['installed_sha256']) == len(item['head_sha256']) == 64
             and item['same_as_head'] == (item['installed_sha256'] == item['head_sha256']), 'audit source shape')
        digest = item['installed_sha256']
        need(name not in pins or pins[name] == digest, 'audit source conflicts with installed roles')
        pins[name] = digest
    return state, receipt, expected, pins, c, tests
