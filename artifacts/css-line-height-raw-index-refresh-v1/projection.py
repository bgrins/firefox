import copy


def derive(canonical, pre, post, raw):
    assert canonical['staged_working'] == {}
    assert raw['semantic_index_unchanged'] is True and raw['runtime_epoch_updated'] is False
    assert raw['before'] == canonical['raw_index_observation']['current']
    assert pre['raw_index_observation']['current'] == raw['before']
    expected = copy.deepcopy(pre)
    expected['raw_index_observation']['current'] = raw['after']
    assert post == expected
    result = copy.deepcopy(canonical)
    result['raw_index_observation']['current'] = raw['after']
    return result
