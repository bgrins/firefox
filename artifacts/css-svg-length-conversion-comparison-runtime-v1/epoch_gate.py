def bind(ROOT, epoch, read, sha, authenticate, load):
    def need(ok, why):
        if not ok:
            raise RuntimeError(why)
    state, receipt = read(epoch / 'STATE.json'), read(epoch / 'ROOT-FINAL-CHECK.json')
    final, pins = read(epoch / 'FINAL.json'), read(epoch / 'FINAL-PINS.json')
    installation, config = read(epoch / 'INSTALLATION.json'), read(epoch / 'CONFIG.json')
    need(state['status'] == 'terminal' and state['installed'] is True and 'failure' not in state
         and state['build_exit'] == state['lint_exit'] == 0 and state['recovery_errors'] == []
         and state['subtests'] == {'PASS': 8, 'FAIL': 0} and state['files_ok'] == 1, 'successful installed113')
    need(receipt['status'] == 'INSTALLED_VERIFIED' and receipt['exit'] == 0
         and receipt['state_sha256'] == sha(epoch / 'STATE.json') and receipt['final_sha256'] == sha(epoch / 'FINAL.json')
         and receipt['installed_binary_pins'] == state['installed_binary_pins'] == installation['binary_pins'], 'installed root/source/binary join')
    need(final == installation['after'] and len(final['sources']) == receipt['source_count'] == 50
         and len(pins) == receipt['pin_count'] == 356 and receipt['staged_paths_preserved'] == 925
         and receipt['native_modified_paths'] == 27 and receipt['installed112_test_identities_preserved'] is True
         and receipt['new113_test_identity_verified'] is True, 'installed roster/ownership')
    need(pins == {**read(epoch / 'RESOURCES.json'), **final['sources'], **state['installed_binary_pins'],
                  installation['owned_test']: installation['owned_test_sha256']}, 'complete installed roles')
    need(all(final['sources'][n] == h for n, h in installation['installed_source_pins'].items()), 'installed113 source')
    owned = dict(config['installed_tests'])
    for directory in ('css-cssom-client-install-runtime-v1', 'css-cssom-offset-scroll-install-runtime-v1'):
        prior = ROOT / 'artifacts' / directory
        authenticate(read(prior / 'FILES.json'), prior)
        record = read(prior / 'INSTALLATION.json')
        need(owned[record['owned_test']] == {'identity': record['owned_test_identity'],
                                           'sha256': record['owned_test_sha256']}, 'old112 identity join')
    need(installation['owned_test'] not in owned and len(owned) == 2, 'distinct113 ownership')
    owned[installation['owned_test']] = {'identity': installation['owned_test_identity'],
                                       'sha256': installation['owned_test_sha256']}
    need(all(pins[n] == item['sha256'] for n, item in owned.items()), 'three installed WPT role joins')
    config['modified_native_paths'] = sorted(set(config['modified_native_paths']) | set(installation['installed_source_pins']))
    return final, pins, config, owned
