import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def replace_bytes(path, data):
    descriptor, name = tempfile.mkstemp(prefix='.zoom-install-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


manifest_pin, = sys.argv[1:]
assert sha(HERE / 'FILES.json') == manifest_pin
for name, pin in read(HERE / 'FILES.json').items():
    assert sha(HERE / name) == pin['sha256']
for name, pin in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / name) == pin
assert not any(os.environ.get(k) for k in
               ['GIT_DIR', 'GIT_INDEX_FILE', 'GIT_WORK_TREE', 'RUSTFLAGS', 'CARGO_TARGET_DIR'])
assert shutil.disk_usage(ROOT).free > 35 * 2**30
spec = importlib.util.spec_from_file_location('normalization_state', RUNTIME / 'state.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
epoch_bytes = (RUNTIME / 'CURRENT-EPOCH.json').read_bytes()
assert hashlib.sha256(epoch_bytes).hexdigest() == '4e57e1bc389c057beb27d13f2f25234c142fc2c96d10057eededbb6808a2ee83'
epoch = json.loads(epoch_bytes)
before = s.a.verify_current(s.h, ROOT, ENV, epoch)
flags = {name: s.h.git(ROOT / name, ENV, 'ls-files', '-v', '-z')
         for name in ['.', 'artifacts/css-spec-lean']}
assert epoch['semantic_index']['head'] == '1c7870c6d36d002b1c785ec2a6251ddc4ca2a040'
assert len(epoch['modified_native_paths']) == 9
assert s.h.git(ROOT, ENV, 'symbolic-ref', 'HEAD').decode().strip() == 'refs/heads/stylo-bloom-verification-2'
observed = ROOT / 'artifacts/css-registered-container-zoom-runtime-admission-only-1/RESULT.json'
assert sha(observed) == 'dfb8920f58104dbc01a6f325c48b17bd905442d315b63404e7b24db0973278b8'
assert read(observed)['complete'] and read(observed)['execution_preserved']
roles = read(HERE / 'UPDATE-ROLES.json')
assert len(roles) == 2 and set(roles) <= set(epoch['modified_native_paths'])
identities = {}
for name, record in roles.items():
    assert sha(ROOT / name) == record['base_sha256'] == sha(ROOT / record['base'])
    assert hashlib.sha256(s.h.git(ROOT, ENV, 'show', 'HEAD:' + name)).hexdigest() == record['head_sha256']
    assert sha(ROOT / record['candidate']) == record['candidate_sha256']
    st = (ROOT / name).lstat()
    assert (ROOT / name).is_file() and not (ROOT / name).is_symlink()
    identities[name] = [st.st_dev, st.st_ino]
run = RUNTIME / 'zoom-normalization-correction-1'
run.mkdir()
save(run / 'PRE.json', before)
save(run / 'INITIAL-EPOCH.json', epoch)
save(run / 'SOURCE-ROLES.json', roles)
controls_before = {name: (RUNTIME / name).read_bytes()
                   for name in ['ROLE.json', 'OWNED.json', 'CURRENT-EPOCH.json']}
assert controls_before['CURRENT-EPOCH.json'] == epoch_bytes
role = json.loads(controls_before['ROLE.json'])
owned = json.loads(controls_before['OWNED.json'])
assert role['role'] == 'candidate' and role['variant'] == 'zoom-normalization-v2' and not role['built']
assert role['last_build'] == 'zoom-normalization-build-1'
save(run / 'PREVIOUS-ROLE.json', role)
save(run / 'PREVIOUS-OWNED.json', owned)
changed = []
current = copy.deepcopy(epoch)
controls_after = {}
try:
    assert s.h.index_state(ROOT, ENV) == before['index']
    assert s.h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == before['nested_index']
    for name, record in roles.items():
        st = (ROOT / name).lstat()
        assert [st.st_dev, st.st_ino] == identities[name] and not (ROOT / name).is_symlink()
        assert sha(ROOT / name) == record['base_sha256']
        changed.append(name)
        (ROOT / name).write_bytes((ROOT / record['candidate']).read_bytes())
        for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
            if name in current[key]:
                current[key][name] = s.h.fingerprint(ROOT, name)
        current['pins'][name] = s.h.fingerprint(ROOT, name)
        current['installed_identities'][name] = identities[name]
        owned[name] = {'path': name, 'identity': identities[name],
                       'owned_sha256': record['candidate_sha256']}
    state = s.h.index_state(ROOT, ENV)
    semantic = s.h.semantic_index(state)
    assert {k: v for k, v in semantic.items() if k != 'working_diff'} == {
        k: v for k, v in epoch['semantic_index'].items() if k != 'working_diff'}
    assert state['raw_index'] == before['index']['raw_index']
    assert s.h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == before['nested_index']
    assert all(s.h.git(ROOT / name, ENV, 'ls-files', '-v', '-z') == body
               for name, body in flags.items())
    current['semantic_index'] = semantic
    current['raw_index_observation']['current'] = state['raw_index']
    current['modified_native_paths'] = sorted(epoch['modified_native_paths'])
    assert sorted(s.h.git(ROOT, ENV, 'diff', '--name-only').decode().splitlines()) == current['modified_native_paths']
    current['counts']['roles'] = len(current['pins'])
    current['counts']['installed_identities'] = len(current['installed_identities'])
    current['counts']['native_modified_paths'] = len(current['modified_native_paths'])
    current['registered_number_transition'] = {
        'role': 'candidate', 'variant': 'zoom-normalization-v3', 'compiled': False,
        'last_phase': run.name, 'accepted': False,
    }
    current['zoom_normalization_transition'] = {
        'proposal': str(HERE.relative_to(ROOT)), 'manifest_sha256': manifest_pin,
        'source_paths': 7, 'corrected_source_paths': 2, 'prior_epoch_sha256': hashlib.sha256(epoch_bytes).hexdigest(),
        'accepted': False, 'container_contract': 'experimental per-source zoom inference',
        'logical_unit_scheduling': 'separate unresolved defect',
    }
    after = s.a.verify_current(s.h, ROOT, ENV, current)
    role.update({'role': 'candidate', 'variant': 'zoom-normalization-v3', 'built': False,
                 'paired_head': epoch['semantic_index']['head'], 'last_install': run.name})
    controls_after = {
        'ROLE.json': (json.dumps(role, indent=2) + '\n').encode(),
        'OWNED.json': (json.dumps(owned, indent=2, sort_keys=True) + '\n').encode(),
        'CURRENT-EPOCH.json': (json.dumps(current, indent=2, sort_keys=True) + '\n').encode(),
    }
    for name, data in controls_after.items():
        assert (RUNTIME / name).read_bytes() == controls_before[name]
        replace_bytes(RUNTIME / name, data)
    assert all((RUNTIME / name).read_bytes() == data for name, data in controls_after.items())
    save(run / 'POST.json', after)
    save(run / 'EPOCH.json', current)
    save(run / 'RESULT.json', {'installed': True, 'compiled': False, 'accepted': False,
                             'new_sources': 0, 'corrected_sources': 2, 'modified_native_paths': 9,
                             'existing_work_preserved': True,
                             'epoch_sha256': sha(RUNTIME / 'CURRENT-EPOCH.json')})
except BaseException:
    for name, data in controls_before.items():
        assert (RUNTIME / name).read_bytes() in [data, controls_after.get(name)]
        replace_bytes(RUNTIME / name, data)
    for name in reversed(changed):
        st = (ROOT / name).lstat()
        assert [st.st_dev, st.st_ino] == identities[name] and not (ROOT / name).is_symlink()
        assert sha(ROOT / name) in [roles[name]['candidate_sha256'], roles[name]['base_sha256']]
        (ROOT / name).write_bytes((ROOT / roles[name]['base']).read_bytes())
    assert s.a.verify_current(s.h, ROOT, ENV, epoch) == before
    assert all(s.h.git(ROOT / name, ENV, 'ls-files', '-v', '-z') == body
               for name, body in flags.items())
    save(run / 'ROLLED-BACK.json', {'restored': changed})
    raise
print((run / 'RESULT.json').read_text(), flush=True)
