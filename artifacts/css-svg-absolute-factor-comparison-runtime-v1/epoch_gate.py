def bind(ROOT, epoch, read, sha, authenticate, load):
    def need(ok, why):
        if not ok:
            raise RuntimeError(why)
    state = read(epoch / 'STATE.json')
    receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
    final = read(epoch / 'FINAL.json')
    installation = read(epoch / 'TEST-INSTALLATION.json')
    config = read(epoch / 'CONFIG.json')
    owned_test = read(epoch / 'OWNED-TEST.json')
    need(state == {'status': 'terminal', 'native_changes': False, 'complete': True,
                   'expanded_test_installed': True, 'expanded_acceptance': False,
                   'lint_exit': 0, 'counts': {'PASS': 15, 'FAIL': 0}, 'files_ok': 2},
         'successful final15 installed test epoch')
    need(receipt['status'] == 'TEST_SCOPE_INSTALLED_VERIFIED' and receipt['exit'] == 0
         and receipt['state_sha256'] == sha(epoch / 'STATE.json')
         and receipt['final_sha256'] == sha(epoch / 'FINAL.json')
         and receipt['counts'] == state['counts'] and receipt['files_ok'] == 2
         and receipt['lint_exit'] == 0 and receipt['new_native_build'] is False,
         'final15 root receipt')
    need(final == installation['after'] and final['snapshot'] == installation['before']['snapshot']
         and installation['native_changes'] is False
         and len(final['snapshot']['sources']) == receipt['source_count'] == 52
         and len(final['pins']) == receipt['pin_count'] == 372
         and receipt['native_modified_paths'] == 29 and receipt['staged_paths_preserved'] == 925
         and receipt['native_sources_index_binaries_unchanged'] is True
         and receipt['prior4_test_identities_preserved'] is True
         and receipt['new_font_test_identity_verified'] is True,
         'final15 source and ownership preservation')
    owned = dict(config['installed_tests'])
    name = owned_test['path']
    need(name not in owned and len(owned) == 4, 'prior4 installed ownership')
    owned[name] = {k: owned_test[k] for k in ('identity', 'sha256')}
    need(owned == receipt['installed_tests'], 'five installed identity joins')
    need(all(final['pins'][n] == item['sha256'] for n, item in owned.items())
         and all(final['pins'][n] == h for n, h in final['snapshot']['sources'].items())
         and all(final['pins'][n] == h for n, h in receipt['installed_binary_pins'].items()),
         'complete source/test/binary role joins')
    return final['snapshot'], final['pins'], config, owned
