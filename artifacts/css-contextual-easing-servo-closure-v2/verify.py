import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(directory):
    return {p.relative_to(directory).as_posix(): sha(p)
            for p in directory.rglob('*') if p.is_file()}


for role in ('baseline', 'candidate'):
    assert inventory(HERE / role) == read(HERE / f'{role.upper()}-FILES.json'), role
    assert not (HERE / role / 'target').exists()

for package in read(HERE / 'RESOLVED-SOURCES.json'):
    directory = Path(package['manifest_path']).parent
    assert inventory(directory) == package['files'], package['name']

for package in read(HERE / 'DIRECTORY-SOURCE-AUDIT.json')['packages']:
    directory = Path(package['manifest_path']).parent
    checksums = directory / '.cargo-checksum.json'
    assert sha(checksums) == package['checksum_manifest_sha256']
    for name, expected in read(checksums)['files'].items():
        assert sha(directory / name) == expected, (package['name'], name)

provenance = read(HERE / 'TRACKED-PATCH-PROVENANCE.json')
assert sha(ROOT / 'Cargo.toml') == provenance['root_manifest_sha256']
for entry in provenance['files']:
    path = ROOT / entry['path']
    expected = entry['head_sha256']
    if expected is None:
        assert not path.exists() and not path.is_symlink(), entry['path']
    else:
        assert sha(path) == expected, entry['path']

for name, role in read(HERE / 'SOURCE-ROLES.json').items():
    if name.startswith('servo/components/style/'):
        assert sha(HERE / 'baseline' / name) == role['base_sha256']
        assert sha(HERE / 'candidate' / name) == role['candidate_sha256']

baseline = read(HERE / 'BASELINE-FILES.json')
candidate = read(HERE / 'CANDIDATE-FILES.json')
assert baseline.keys() == candidate.keys()
assert sorted(name for name in baseline if baseline[name] != candidate[name]) == read(
    HERE / 'INHERITANCE.json')['seven_source_differences_preserved']
assert (HERE / 'baseline/Cargo.lock').read_bytes() == (HERE / 'candidate/Cargo.lock').read_bytes()
print('Verified exact inputs, seven source differences, tracked patches, and all selected directory-source checksums; verifier performs no compilation')
