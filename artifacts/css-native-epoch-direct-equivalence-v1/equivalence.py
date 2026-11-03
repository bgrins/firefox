import copy
import hashlib
import json
import re
from pathlib import Path


INPUTS = {
    'native_receipt': ('artifacts/css-prioritary-declaration-capacity-publication-capacity-runtime-1/COMMIT-RESULT.json', '085fcdc6576fea84ef9e43fbc0d0c7f1111d9e7899d8d42f6040442e49d91d16'),
    'original_epoch': ('artifacts/css-font-size-form-crash-diagnostic-raw-index-refresh-runtime-3/PRE-CURRENT-EPOCH.json', '8fecf2c4ed6c92238a32e6f096a1d726b57aecb85c0dde6bb5433c015f51d65e'),
    'original_capture': ('artifacts/css-research-checkpoint-20261102-v115-current.json', '5371c41d114e4bab26f863422b8ae5b464db646bf3f2be06358f0072d2d4a40b'),
    'original_terminal': ('artifacts/css-research-checkpoint-20261102-v115-capture-terminal.json', '1aef4530a2a05e5ce1493be95f872d32265970e209191b08ccb31eb589ee6333'),
    'current_epoch': ('artifacts/css-root-font-cancellation-archive-raw-index-refresh-runtime-1/EPOCH.json', 'e3b00d568e1f317eba71a02cc5bd848c8d5a7f1119a02990e51d2a3452e1d9fc'),
    'current_capture': ('artifacts/css-root-font-cancellation-trace-current-v1.json', 'da0e0cf75f30be0ee6d8953cea5537a2e529c6f5f4c68ea2bc38f15d55aab6c9'),
    'current_terminal': ('artifacts/css-root-font-cancellation-trace-current-root-terminal-v1.json', '19c3186bbedd755bcdcb4e6446baa8b0adc9d432b91c98be4e7327c98cf1f608'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def equal(left, right, message):
    require(canonical(left) == canonical(right), message)


def decode(body):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('nonfinite JSON: ' + value)

    value = json.loads(body, object_pairs_hook=pairs, parse_constant=invalid)
    canonical(value)
    return value


def authenticate(bodies):
    require(set(bodies) == set(INPUTS), 'input set')
    documents = {}
    for name, (_, pin) in INPUTS.items():
        require(hashlib.sha256(bodies[name]).hexdigest() == pin, 'input hash: ' + name)
        documents[name] = decode(bodies[name])
    return documents


def _compare(documents):
    receipt = documents['native_receipt']
    original = documents['original_epoch']
    current = documents['current_epoch']
    old_capture = documents['original_capture']
    new_capture = documents['current_capture']
    old_snapshot, new_snapshot = old_capture['audit'], new_capture['snapshot']
    require(receipt['signature_verified'] is True, 'saved native signature claim')
    equal(receipt['epoch_sha256'], INPUTS['original_epoch'][1], 'receipt epoch')
    equal(old_capture['prior_receipt_sha256'], INPUTS['native_receipt'][1], 'original receipt')
    equal(new_capture['checkpoint'], receipt, 'unchanged native receipt')
    equal(new_capture['checkpoint_receipt'], dict(zip(('path', 'sha256'), INPUTS['native_receipt'])), 'current receipt pin')
    equal(new_capture['authority_kind'], 'signed-native-publication', 'native authority label')
    equal(new_capture['refresh_epoch_sha256'], INPUTS['current_epoch'][1], 'current refresh epoch')
    equal(documents['original_terminal'], {
        'session': 84891, 'launch': '35cd73', 'terminal': 'a35e44', 'exit': 0,
        'capture_sha256': INPUTS['original_capture'][1],
    }, 'original capture terminal')
    terminal = documents['current_terminal']
    equal({key: terminal[key] for key in ('launch_chunk', 'session_id', 'terminal_chunk', 'exit_code', 'capture_path', 'capture_sha256')}, {
        'launch_chunk': '4e2c78', 'session_id': 51957, 'terminal_chunk': 'd89371', 'exit_code': 0,
        'capture_path': INPUTS['current_capture'][0], 'capture_sha256': INPUTS['current_capture'][1],
    }, 'current capture terminal')
    require(terminal['full_current_state_verified'] is True, 'terminal state claim')
    raw_values = []
    for label, epoch, capture, snapshot in (
        ('original', original, old_capture, old_snapshot),
        ('current', current, new_capture, new_snapshot),
    ):
        equal(capture['controls']['CURRENT-EPOCH.json'], INPUTS[label + '_epoch'][1], label + ' epoch control')
        require(capture['full_current_state_verified'] is True and capture['source_transition_lock_absent'] is True, label + ' capture claims')
        equal(epoch['semantic_index']['head'], receipt['commit'], label + ' native HEAD')
        raw = epoch['raw_index_observation']['current']
        require(type(raw) is str and re.fullmatch('[0-9a-f]{64}', raw) is not None, label + ' raw digest')
        equal(snapshot['index']['raw_index'], raw, label + ' snapshot raw join')
        equal({k: v for k, v in snapshot['index'].items() if k != 'raw_index'}, epoch['semantic_index'], label + ' semantic index')
        equal({k: v for k, v in snapshot['nested_index'].items() if k != 'raw_index'}, epoch['nested_semantic_index'], label + ' nested index')
        require(snapshot['current_raw_stable_during_check'] is True and snapshot['working_sources_binaries_research_preserved'] is True, label + ' snapshot claims')
        raw_values.append(raw)
    epoch_normalized = copy.deepcopy(current)
    epoch_normalized['raw_index_observation']['current'] = raw_values[0]
    equal(original, epoch_normalized, 'whole epoch equivalence')
    snapshot_normalized = copy.deepcopy(new_snapshot)
    snapshot_normalized['index']['raw_index'] = raw_values[0]
    equal(old_snapshot, snapshot_normalized, 'whole snapshot equivalence')
    controls_normalized = dict(new_capture['controls'])
    controls_normalized['CURRENT-EPOCH.json'] = INPUTS['original_epoch'][1]
    equal(old_capture['controls'], controls_normalized, 'other controls unchanged')
    return {
        'kind': 'saved-native-epoch-equivalence-evidence',
        'native_receipt_sha256': INPUTS['native_receipt'][1], 'native_head': receipt['commit'],
        'original_epoch_sha256': INPUTS['original_epoch'][1], 'current_epoch_sha256': INPUTS['current_epoch'][1],
        'raw_before': raw_values[0], 'raw_after': raw_values[1],
        'permitted_epoch_path': '/raw_index_observation/current',
        'permitted_snapshot_path': '/index/raw_index',
        'whole_epoch_equal_after_normalization': True, 'whole_snapshot_equal_after_normalization': True,
        'live_checks_performed': False, 'historical_outcomes_verified': False,
        'diagnostic_execution_authorized': False, 'publication_acceptance': False,
    }


def verify_saved(root):
    bodies = {name: (Path(root) / path).read_bytes() for name, (path, _) in INPUTS.items()}
    return _compare(authenticate(bodies))
