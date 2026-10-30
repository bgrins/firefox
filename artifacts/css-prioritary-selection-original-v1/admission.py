PENDING = ('head', 'controls', 'prepared_application_metadata', 'prepared_flag_hashes',
           'prepared_flag_capture', 'execution_handoff', 'restoration_binding')


def validate(root, policy):
    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
    assert policy['activation_pending'] == ['Fresh current-state/restoration/flags/application handoff and reviewed admission binding']
    assert all(policy[name] is None for name in PENDING)
    assert policy['baseline_binding'] is None and policy['baseline_capsule'] is None
    assert policy['original_admission_policy_sha256'] is None
