import json
import hashlib

def read(p):
    return json.loads(p.read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def installed_epoch(epoch):
    expected, state_before = read(epoch / 'FINAL.json'), read(epoch / 'STATE.json')
    receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
    before, installation = read(epoch / 'BEFORE.json'), read(epoch / 'INSTALLATION.json')
    config = read(epoch / 'CONFIG.json')
    native = 'dom/base/Element.cpp'
    candidate = '5770fd0f1134284626ed42152e4b1c1d054cf509ae99e2ebcaf08d5ae00c0913'
    owned = 'testing/web-platform/tests/css/cssom-view/offset-scroll-integer-precision.html'
    fixture_hash = '18c47e1acbf0a546a975fe5dc92c297a38a71e228a7b6ec576a58bc71c06078b'
    assert state_before['status'] == 'terminal' and state_before['installed'] is True and state_before['restored'] is False
    assert state_before['build_exit'] == state_before['lint_exit'] == 0 and state_before['recovery_errors'] == []
    assert 'failure' not in state_before and state_before['subtests'] == {'PASS': 32, 'FAIL': 0} and state_before['files_ok'] == 1
    assert receipt['status'] == 'INSTALLED_VERIFIED' and receipt['fix'] == 112 and receipt['exit'] == 0
    assert receipt['build_exit'] == receipt['lint_exit'] == 0 and receipt['existing_stage_paths'] == 925
    assert receipt['source_count'] == 47 and receipt['pin_count'] == 318
    assert all(receipt[n] is True for n in ['head_index_preserved', 'other_native_sources_preserved', 'owned_wpt_present', 'cleanup_verified'])
    assert receipt['state_sha256'] == sha(epoch / 'STATE.json') and receipt['final_sha256'] == sha(epoch / 'FINAL.json')
    assert receipt['installed_binary_pins'] == state_before['installed_binary_pins'] == installation['binary_pins']
    assert receipt['acceptance_sha256'] == state_before['acceptance_sha256'] == installation['acceptance_sha256'] == 'bf2e4f24e4ddc542346499f108e9510646db050aeec2893e3dbf506870b8d11c'
    assert installation['before'] == before and installation['after'] == expected
    assert len(expected['sources']) == len(before['sources']) == 47
    assert expected['sources'] == {**before['sources'], native: candidate}
    assert installation['installed_source_pins'] == {native: candidate}
    assert installation['original_source_pins'] == {native: before['sources'][native]}
    assert expected['head'] == config['head'] == '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
    assert all(expected[k] == before[k] for k in ['head', 'index_diff_sha256', 'index_entries_sha256'])
    assert config['source_pins'] == before['sources']
    assert len(config['modified_native_paths']) == 24 and native not in config['modified_native_paths']
    assert installation['owned_test'] == owned and installation['owned_test_sha256'] == fixture_hash
    assert config['install'] == {owned: 'fixture.html'} and sha(epoch / 'fixture.html') == fixture_hash
    pins = read(epoch / 'FINAL-PINS.json')
    assert len(pins) == 318 and pins == {**read(epoch / 'RESOURCES.json'), **expected['sources'],
                                       owned: fixture_hash, **state_before['installed_binary_pins']}
    config['guard_sources'] = sorted(expected['sources'])
    config['modified_native_paths'] = sorted([*config['modified_native_paths'], native])
    return expected, pins, config, installation

