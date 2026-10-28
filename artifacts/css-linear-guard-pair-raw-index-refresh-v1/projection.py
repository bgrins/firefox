import copy


def derive(canonical, pre, post, raw, sources):
    assert canonical['staged_working'] == {}
    assert raw['semantic_index_unchanged'] is True and raw['runtime_epoch_updated'] is False
    assert raw['before'] == canonical['raw_index_observation']['current']
    assert set(sources) == {'servo/components/style/values/specified/easing.rs'}
    expected = copy.deepcopy(canonical)
    for name, record in sources.items():
        assert canonical['pins'].get(name, record['base_sha256']) == record['base_sha256']
        expected['pins'][name] = record['base_sha256']
        identity = pre['installed_identities'][name]
        assert isinstance(identity, list) and len(identity) == 2
        assert all(isinstance(n, int) and not isinstance(n, bool) and n > 0 for n in identity)
        assert canonical['installed_identities'].get(name, identity) == identity
        expected['installed_identities'][name] = identity
    expected['counts']['roles'] = len(expected['pins'])
    expected['counts']['installed_identities'] = len(expected['installed_identities'])
    expected['counts']['staged_payloads'] = len(expected['staged_working'])
    assert pre == expected
    expected['raw_index_observation']['current'] = raw['after']
    assert post == expected
    updated = copy.deepcopy(canonical)
    updated['raw_index_observation']['current'] = raw['after']
    return updated
