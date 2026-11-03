import hashlib
import json


def require_intermediate(snapshot, consumed_inputs):
    assert set(snapshot) == {
        'index', 'nested_index', 'current_raw_stable_during_check',
        'working_sources_binaries_preserved', 'archival_research_not_rechecked',
        'verification_scope', 'consumed_inputs_sha256',
    }
    assert snapshot['current_raw_stable_during_check'] is True
    assert snapshot['working_sources_binaries_preserved'] is True
    assert snapshot['archival_research_not_rechecked'] is True
    assert snapshot['verification_scope'] == 'intermediate-consumed-inputs-v1'
    assert consumed_inputs
    assert snapshot['consumed_inputs_sha256'] == hashlib.sha256(json.dumps(
        consumed_inputs, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def require_full(snapshot):
    assert set(snapshot) == {
        'index', 'nested_index', 'current_raw_stable_during_check',
        'working_sources_binaries_research_preserved',
    }
    assert snapshot['current_raw_stable_during_check'] is True
    assert snapshot['working_sources_binaries_research_preserved'] is True
