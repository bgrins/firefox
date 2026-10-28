import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent

def verify_current(h, root, env, epoch):
    policy = json.loads((HERE / 'STAGED-STATE.json').read_text())
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    def read(path):
        return json.loads(path.read_text())
    for name, pin in policy['control_pins'].items():
        assert not (root / name).is_symlink() and sha(root / name) == pin, name
    selection = read(root / policy['selection'])
    selected = set(selection['files'])
    assert len(selected) == policy['selected_files'] == 207
    assert selected == set(selection['source_pins'])
    assert all(name.startswith('artifacts/') for name in selected)
    before = h.index_state(root, env)
    nested = h.index_state(root / 'artifacts/css-spec-lean', env)
    assert before['head'] == epoch['semantic_index']['head'] == policy['head']
    assert before['working_diff'] == epoch['semantic_index']['working_diff']
    assert h.semantic_index(nested) == epoch['nested_semantic_index']
    assert nested == read(root / policy['prior_preservation'])['nested_index']
    assert set(h.git(root, env, 'diff', '--cached', '--name-only').decode().splitlines()) == selected
    patch = h.git(root, env, 'diff', '--cached', '--binary', '--full-index', policy['head'])
    assert patch == (root / policy['staged_patch']).read_bytes()
    for name, pin in selection['source_pins'].items():
        assert h.fingerprint(root, name) == pin
        assert hashlib.sha256(h.git(root, env, 'show', ':' + name)).hexdigest() == pin
        assert h.git(root, env, 'ls-files', '--stage', '--', name).decode().split()[::2] == ['100644','0']
    entries = h.git(root, env, 'ls-files', '--stage', '-z').split(b'\0')
    prior_entries = b''.join(row+b'\0' for row in entries if row and row.split(b'\t',1)[1].decode() not in selected)
    assert hashlib.sha256(prior_entries).hexdigest() == epoch['semantic_index']['entries']
    flags = h.git(root, env, 'ls-files', '-v', '-z')
    prior_flags = b''.join(row+b'\0' for row in flags.split(b'\0') if row and row[2:].decode() not in selected)
    saved_flags = read(root / policy['prior_flags'])
    assert hashlib.sha256(prior_flags).hexdigest() == saved_flags['.']
    nested_flags = h.git(root / 'artifacts/css-spec-lean', env, 'ls-files', '-v', '-z')
    assert hashlib.sha256(nested_flags).hexdigest() == saved_flags['artifacts/css-spec-lean']
    for group in ['pins','staged_working','committed_research_working_payloads']:
        assert {name:h.fingerprint(root,name) for name in epoch[group]} == epoch[group], group
    for name, identity in epoch['installed_identities'].items():
        info = (root / name).lstat()
        assert stat.S_ISREG(info.st_mode) and [info.st_dev,info.st_ino] == identity
    native = set(h.git(root, env, 'diff', '--name-only').decode().splitlines())
    assert native == set(epoch['modified_native_paths']) == set(policy['native_sources'])
    assert len(native) == 7
    assert all(epoch['pins'][name] == pin for name,pin in policy['native_sources'].items())
    untracked = {name for name in h.git(root,env,'ls-files','--others','--exclude-standard','--','layout','dom','servo','mfbt').decode().splitlines() if not name.startswith('artifacts/')}
    assert untracked == set(epoch['untracked_native'])
    after = h.index_state(root,env)
    assert after == before
    assert h.index_state(root/'artifacts/css-spec-lean',env) == nested
    assert h.git(root,env,'ls-files','-v','-z') == flags
    return {'index':after,'nested_index':nested,'staged_patch_sha256':hashlib.sha256(patch).hexdigest(),
            'staged_files':207,'current_raw_stable_during_check':True,
            'working_sources_binaries_research_preserved':True,'index_empty':False}
