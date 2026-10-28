import copy
import hashlib


def derive(epoch, observed):
    assert epoch['staged_working'] == {}
    assert epoch['semantic_index']['cached_diff'] == hashlib.sha256(b'').hexdigest()
    assert set(observed) == set(epoch['semantic_index']) | {'raw_index'}
    assert {k: v for k, v in observed.items() if k != 'raw_index'} == epoch['semantic_index']
    result = copy.deepcopy(epoch)
    result['raw_index_observation']['current'] = observed['raw_index']
    return result
