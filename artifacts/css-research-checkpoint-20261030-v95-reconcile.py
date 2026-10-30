import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / 'artifacts/css-research-checkpoint-20261030-v95'
OUT = ROOT / 'artifacts/css-research-checkpoint-20261030-v95-reconciliation'
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
spec = importlib.util.spec_from_file_location('checkpoint', HERE / 'commit.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert not (HERE / 'result.json').exists()
head = m.git('rev-parse', 'HEAD').decode().strip()
assert head == 'a1e0ffba3651cf27853c33d22bb7b1b5368f658f'
assert m.git('rev-parse', 'HEAD^').decode().strip() == m.HEAD
m.git('-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', head)
selected = json.loads((HERE / 'SELECTION.json').read_bytes())
for name in ['commit.py', 'README.md', 'RUN-DELTA.patch', 'BINDINGS.json', 'CHECK.json', 'FILES.json', 'SELECTION.json', 'check.py', 'capture_current.py']:
    p = HERE / name
    selected[str(p.relative_to(ROOT))] = {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
assert len(selected) == 146
changed = set(m.git('diff-tree', '--no-commit-id', '--name-only', '-r', head).decode().splitlines())
assert changed == set(selected)
m.verify_blobs([(head + ':' + p, r) for p, r in sorted(selected.items())])
assert not m.git('diff', '--name-only').strip() and not m.git('diff', '--cached', '--name-only').strip()
before_untracked = m.git('ls-files', '--others', '--exclude-standard', '-z')
assert len(before_untracked.rstrip(b'\0').split(b'\0')) == 563
state = m.load('state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
owned = m.load('owned', 'artifacts/css-registered-number-source-transition-v4/transition.py')
controls = {name: (m.RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
old = json.loads(controls['CURRENT-EPOCH.json'])
assert sha(controls['CURRENT-EPOCH.json']) == 'a7795a7ad75e3a2ebe8313ddd68336f7f16779e31d41709bc3d9f98a9623860b'
assert all(old['committed_research_working_payloads'][p] == r['sha256'] for p, r in selected.items())
actual = state.h.index_state(ROOT, m.ENV)
assert state.h.semantic_index(actual) == old['semantic_index']
assert actual['head'] == head
updated = copy.deepcopy(old)
updated['raw_index_observation']['current'] = actual['raw_index']
lock = m.RUNTIME / 'SOURCE-TRANSITION.lock'
assert lock.is_dir() and not lock.is_symlink() and not list(lock.iterdir())
lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
(OUT / 'PRE-CURRENT-EPOCH.json').write_bytes(controls['CURRENT-EPOCH.json'])
(OUT / 'EPOCH.json').write_bytes(owned.encoded(updated))
audit = state.a.verify_current(state.h, ROOT, m.ENV, updated)
assert all((m.RUNTIME / n).read_bytes() == b for n, b in controls.items())
claim = owned.claim(ROOT, str((m.RUNTIME / 'CURRENT-EPOCH.json').relative_to(ROOT)), sha(controls['CURRENT-EPOCH.json']))
owned.write_owned(ROOT, claim, owned.encoded(updated))
assert state.a.verify_current(state.h, ROOT, m.ENV, updated) == audit
assert m.git('ls-files', '--others', '--exclude-standard', '-z') == before_untracked
assert all((m.RUNTIME / n).read_bytes() == controls[n] for n in ('OWNED.json', 'ROLE.json'))
assert (lock.stat().st_dev, lock.stat().st_ino) == lock_identity
lock.rmdir()
receipt = {'committed': True, 'head': head, 'parent': m.HEAD, 'signature_verified': True,
           'selected_paths': len(selected), 'epoch_sha256': sha(owned.encoded(updated)),
           'accepted_fix_increment': 0, 'native_working_diff_preserved': True,
           'original_signing_driver_exit': 1, 'original_failure': 'post-write raw index observation mismatch',
           'reconciled_only': 'raw_index_observation.current', 'semantic_index_unchanged': True,
           'committed_blobs_verified': True, 'full_current_state_verified': True,
           'source_transition_lock_absent': True, 'untracked_inventory_preserved': True}
(OUT / 'AUDIT.json').write_text(json.dumps(audit, indent=2) + '\n')
(OUT / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
(HERE / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
