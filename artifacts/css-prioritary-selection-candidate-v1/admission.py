PENDING = ('head','controls','prepared_application_metadata','prepared_flag_hashes',
           'prepared_flag_capture','execution_handoff','restoration_binding',
           'baseline_binding','baseline_capsule')


def validate(root, policy):
    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
    assert policy['activation_pending'] == ['Actual original74 terminal/capture/restoration and fresh current-state binding']
    assert all(policy[name] is None for name in PENDING)
