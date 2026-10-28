import stat


def require_transition(epoch, policy):
    transition = epoch['registered_number_transition']
    assert epoch['semantic_index']['head'] == policy['frozen_head']
    assert transition['role'] == 'candidate'
    assert transition['variant'] == 'prototype-overlay'
    assert transition['compiled'] is True
    assert transition['accepted'] is False


def verify_sources(epoch, policy, sources, fingerprint):
    assert len(sources) == policy['expected_source_pins']
    for name, pin in sources.items():
        assert fingerprint(name) == pin and epoch['pins'].get(name) == pin, name
    for name, pin in policy['unchanged_native_sources'].items():
        assert fingerprint(name) == pin, name
        for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
            assert name not in epoch[key] or epoch[key][name] == pin, name


def identities(root, names):
    result = {}
    for name in names:
        info = (root / name).lstat()
        assert stat.S_ISREG(info.st_mode), name
        result[name] = [info.st_dev, info.st_ino]
    return result
