import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = read(HERE / 'SOURCE.json')
assert sha(HERE / 'original.rs') == source['preimage_sha256']
assert sha(HERE / 'candidate.rs') == source['postimage_sha256']
assert sha(HERE / 'native.patch') == source['patch_sha256']
assert (HERE / 'native.patch').read_text().count('diff --git ') == 1
assert ' 100644\n' in (HERE / 'native.patch').read_text()
for kind in ['native', 'research']:
    item = read(HERE / (kind + '.draft.json'))
    assert item['expected_head'] is None and item['execution_epoch'] is None and not item['execution_enabled']
    assert set(item['files']) == set(item['source_pins']) == set(item['source_modes'])
native = read(HERE / 'native.draft.json')
assert native['files'] == ['servo/components/servo_arc/lib.rs']
assert native['source_pins'] == {source['path']: source['postimage_sha256']}
selected = read(HERE / 'RESEARCH-PINS.json')
assert len(selected) == 131 and not set(selected) & set(read(HERE / 'ALREADY-COMMITTED.json'))
for name, pin in selected.items():
    assert sha(ROOT / name) == pin
    mode = '100755' if (ROOT / name).stat().st_mode & 0o111 else '100644'
    assert mode == read(HERE / 'RESEARCH-MODES.json')[name]
for name, pin in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / name) == pin
for name, pin in read(HERE / 'EVIDENCE-MANIFESTS.json').items():
    manifest = ROOT / name
    for relative, expected in read(manifest).items():
        assert sha(manifest.parent / relative) == expected
unit = read(ROOT / 'artifacts/css-keyframe-compact-borrow-unit-runtime-v3/CRATE-SOURCE.json')
assert unit[source['path']] == source['postimage_sha256']
assert (HERE / 'candidate.rs').read_bytes() == (ROOT / 'artifacts/css-keyframe-compact-source-borrow-proposal-v2/candidate' / source['path']).read_bytes()
assert (HERE / 'original.rs').read_bytes() == (ROOT / 'artifacts/css-keyframe-compact-source-borrow-proposal-v2/original' / source['path']).read_bytes()
with tempfile.TemporaryDirectory(prefix='compact-borrow-commit-') as directory:
    scratch = Path(directory)
    target = scratch / source['path']
    target.parent.mkdir(parents=True)
    shutil.copyfile(HERE / 'original.rs', target)
    target.chmod(0o644)
    subprocess.run(['git', 'apply', '--check', str(HERE / 'native.patch')], cwd=scratch, check=True, capture_output=True)
    subprocess.run(['git', 'apply', str(HERE / 'native.patch')], cwd=scratch, check=True, capture_output=True)
    assert sha(target) == source['postimage_sha256'] and target.stat().st_mode & 0o777 == 0o644
    subprocess.run(['git', 'apply', '-R', str(HERE / 'native.patch')], cwd=scratch, check=True, capture_output=True)
    assert sha(target) == source['preimage_sha256'] and target.stat().st_mode & 0o777 == 0o644
print(json.dumps({'status': 'COMPACT_BORROW_COMMIT_PROPOSAL_STATIC_PASS', 'native_paths': 1,
                  'selected_research_paths': 131, 'excluded_committed_paths': 5,
                  'exact_unit_source': True, 'forward_reverse_and_mode': True,
                  'execution_enabled': False, 'live_native_or_index_writes': False}, indent=2))
