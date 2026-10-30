import hashlib
import json
import stat


def verify_intermediate(h, root, env, epoch, consumed_inputs, record_index_mismatch=None):
    assert consumed_inputs and isinstance(consumed_inputs, dict)
    before = h.index_state(root, env)
    assert before['raw_index'] == epoch['raw_index_observation']['current']
    assert h.semantic_index(before) == epoch['semantic_index']
    nested_before = h.index_state(root / 'artifacts/css-spec-lean', env)
    assert h.semantic_index(nested_before) == epoch['nested_semantic_index']
    for name in ('pins', 'staged_working'):
        assert {p: h.fingerprint(root, p) for p in epoch[name]} == epoch[name], name
    assert {p: h.fingerprint(root, p) for p in consumed_inputs} == consumed_inputs, 'consumed_inputs'
    for path, identity in epoch['installed_identities'].items():
        info = (root / path).lstat()
        assert stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == identity
    assert not h.git(root, env, 'diff', '--cached', '--name-only')
    native = {p for p in h.git(root, env, 'diff', '--name-only').decode().splitlines()
              if not p.startswith('artifacts/')}
    assert native == set(epoch['modified_native_paths'])
    untracked = {p for p in h.git(root, env, 'ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines()
                 if not p.startswith('artifacts/')}
    assert untracked == set(epoch['untracked_native'])
    after = h.index_state(root, env)
    if after != before and record_index_mismatch is not None:
        record_index_mismatch({'repository': 'root', 'before': before, 'after': after,
                               'changed_fields': sorted(k for k in before.keys() | after.keys()
                                                        if before.get(k) != after.get(k))})
    assert after == before
    nested_after = h.index_state(root / 'artifacts/css-spec-lean', env)
    if nested_after != nested_before and record_index_mismatch is not None:
        record_index_mismatch({'repository': 'nested', 'before': nested_before, 'after': nested_after,
                               'changed_fields': sorted(k for k in nested_before.keys() | nested_after.keys()
                                                        if nested_before.get(k) != nested_after.get(k))})
    assert nested_after == nested_before
    return {'index': after, 'nested_index': nested_before,
            'current_raw_stable_during_check': True,
            'working_sources_binaries_preserved': True,
            'archival_research_not_rechecked': True,
            'verification_scope': 'intermediate-consumed-inputs-v1',
            'consumed_inputs_sha256': hashlib.sha256(json.dumps(
                consumed_inputs, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}
