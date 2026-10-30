import hashlib
import json
import os
from pathlib import Path
import stat
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def receipt(path, pin):
    path = path.resolve()
    relative = str(path.relative_to(ROOT))
    assert relative.startswith('artifacts/')
    body = path.read_bytes()
    assert sha(body) == pin
    return relative, body, json.loads(body)


def extract(research_path, research_pin, branch, minmax_path, minmax_pin):
    assert branch.startswith('refs/heads/') and len(branch) > len('refs/heads/')
    research_name, research_body, research = receipt(research_path, research_pin)
    minmax_name, minmax_body, minmax = receipt(minmax_path, minmax_pin)
    assert research['committed'] is True and research['signature_verified'] is True
    assert research['native_working_diff_preserved'] is True and research['accepted_fix_increment'] == 0
    assert minmax['signature_verified'] is True and minmax['accepted'] is False and minmax['app_rebuilt'] is False
    assert minmax['accepted_fix_increment'] == 0 and minmax['parent'] == research['head']
    for name, pin in read(HERE / 'INPUTS.json').items():
        assert sha((ROOT / name).read_bytes()) == pin
    policy = read(HERE / 'POLICY.json')
    assert set(minmax['files']) == set(policy['minmax_files'])
    controls = {name: (RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
    epoch = json.loads(controls['CURRENT-EPOCH.json'])
    owned = json.loads(controls['OWNED.json'])
    assert sha(controls['CURRENT-EPOCH.json']) == minmax['epoch_sha256']
    assert epoch['semantic_index']['head'] == minmax['commit'] and epoch['staged_working'] == {}
    assert epoch['modified_native_paths'] == ['servo/components/style/custom_properties.rs']
    assert epoch['minmax_relative_infinity_transition']['native_commit'] == minmax['commit']
    assert not os.path.lexists(RUNTIME / 'SOURCE-TRANSITION.lock')
    assert not os.path.lexists(ROOT / policy['runtime_output'])
    previous = read(ROOT / 'artifacts/css-contextual-duration-masked-nine-original-v1/POLICY.json')
    expected = {name: record['sha256'] for name, record in previous['accepted_current_payloads'].items()}
    assert len(expected) == 29
    expected.update(policy['minmax_files'])
    assert len(expected) == 31
    claims = {}
    for name, pin in expected.items():
        path = ROOT / name
        info = path.lstat()
        assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1
        identity = [info.st_dev, info.st_ino]
        assert sha(path.read_bytes()) == pin and epoch['pins'][name] == pin
        assert epoch['installed_identities'][name] == identity
        claims[name] = {'sha256': pin, 'identity': identity}
    assert sha((ROOT / 'servo/components/style/custom_properties.rs').read_bytes()) == policy['held_provider_sha256']
    for name in set(policy['files']) - {policy['source_path']}:
        assert not os.path.lexists(ROOT / name) and epoch['pins'].get(name) is None
        assert name not in epoch['installed_identities'] and name not in owned
    deletion = policy['deleted_metadata']
    assert sha((ROOT / deletion['path']).read_bytes()) == deletion['sha256']
    assert epoch['pins'].get(deletion['path'], deletion['sha256']) == deletion['sha256']
    absent = sorted(name for name, pin in epoch['pins'].items() if pin is None and name.startswith('testing/web-platform/meta/'))
    for name in absent:
        assert not os.path.lexists(ROOT / name)
        assert name not in epoch['installed_identities'] and name not in owned
    mutable = {'pins', 'installed_identities', 'semantic_index', 'raw_index_observation', 'modified_native_paths', 'counts', 'committed_research_working_payloads', 'log_clear_special_values_transition'}
    historical = {name: value for name, value in epoch.items() if name not in mutable}
    assert 'log_clear_special_values_transition' not in epoch
    assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
    assert (ROOT / research_name).read_bytes() == research_body and (ROOT / minmax_name).read_bytes() == minmax_body
    return {'head': minmax['commit'], 'branch': branch, 'research_receipt': research_name,
            'research_receipt_sha256': research_pin, 'minmax_commit_receipt': minmax_name,
            'minmax_commit_receipt_sha256': minmax_pin, 'controls': {name: sha(body) for name, body in controls.items()},
            'preserved_claims': claims, 'historical_markers': historical, 'absent_metadata': absent}
