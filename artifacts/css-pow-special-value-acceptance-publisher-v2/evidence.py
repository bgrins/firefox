import importlib.util
import json
import hashlib


def verify(root, inputs):
    assert inputs['final_validation_ready']
    for name,pin in inputs['evidence_pins'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==pin,name
    policy_path = root / inputs['research_checkpoint']['directory'] / 'POLICY.json'
    policy = json.loads(policy_path.read_bytes())
    assert policy['final_validation'] == inputs['final_validation_binding']
    path = policy_path.parent / 'check_final_validation.py'
    spec = importlib.util.spec_from_file_location('pow_acceptance_final', path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    result = checker.verify(root, policy)
    assert result == inputs['expected_final_validation']
    return {'callbacks':147, 'new_page_pass':24, 'targets_pass':18, 'control_end_signatures':131, 'accepted':False}
