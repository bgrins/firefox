import copy
import hashlib


def derive(epoch, observed, entries, staging):
    assert epoch['staged_working'] == {}
    assert observed['head'] == epoch['semantic_index']['head']
    assert observed['working_diff'] == epoch['semantic_index']['working_diff']
    selected = set(staging['staged_files'])
    assert len(selected) == 165 and selected == set(staging['staged_working'])
    assert all(n.startswith('artifacts/') and not n.startswith('artifacts/css-spec-lean/') for n in selected)
    records = [row for row in entries.split(b'\0') if row]
    added = [row for row in records if row.split(b'\t', 1)[1].decode() in selected]
    assert len(added) == 165
    assert all(row.split(b'\t', 1)[0].startswith(b'100644 ') and row.split(b'\t', 1)[0].endswith(b' 0') for row in added)
    prior = b''.join(row + b'\0' for row in records if row not in added)
    assert hashlib.sha256(prior).hexdigest() == epoch['semantic_index']['entries']
    assert hashlib.sha256(entries).hexdigest() == observed['entries']
    result = copy.deepcopy(epoch)
    result['semantic_index'] = {k: v for k, v in observed.items() if k != 'raw_index'}
    result['raw_index_observation']['current'] = observed['raw_index']
    result['staged_working'] = copy.deepcopy(staging['staged_working'])
    return result
