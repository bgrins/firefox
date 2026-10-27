def bind(ROOT, previous, read, sha, authenticate, load):
    def need(ok, why):
        if not ok:
            raise RuntimeError(why)
    c = read(previous / 'CONFIG.json')
    state = read(previous / 'STATE.json')
    receipt = read(previous / 'ROOT-FINAL-CHECK.json')
    need(state['status'] == 'terminal' and state['complete'] and state['preserved']
         and not state['native_changes'] and state['counts'] == {'PASS':4,'FAIL':4}, 'calibrated preserved epoch')
    need(receipt['status'] == 'PRESERVED_CALIBRATED_DIAGNOSTIC' and receipt['exit'] == 0
         and receipt['state_sha256'] == sha(previous / 'STATE.json')
         and receipt['final_sha256'] == sha(previous / 'FINAL.json')
         and receipt['pin_count'] == 399 and receipt['source_count'] == 53
         and receipt['native_modified_paths'] == 30 and receipt['staged_paths'] == 925
         and receipt['owned_fixture_removed'] and not receipt['accepted_bug'], 'root diagnostic receipt')
    gate = load('prior_hidden_gate', ROOT / 'artifacts/css-svg-length-hidden-provider-fallback-browser-v1/epoch_gate.py')
    _, old_receipt, expected, pins, installed_config, installed_tests = gate.bind(
        ROOT, ROOT / c['epoch'], c, read, sha, authenticate, load, need)
    pins[c['owned_metadata']] = None
    need(read(previous / 'BEFORE.json') == read(previous / 'FINAL.json')
         == {'snapshot':expected,'pins':pins}, 'full preserved role join')
    need(receipt['installed_tests'] == installed_tests
         and receipt['installed_binary_pins'] == old_receipt['installed_binary_pins'], 'installed identities and build')
    return expected, pins, installed_config, installed_tests
