import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

for role in ('baseline', 'candidate'):
    for name, expected in read(HERE / f'{role.upper()}-FILES.json').items():
        assert sha(HERE / role / name) == expected, (role, name)
    assert not (HERE / role / 'target').exists()

for package in read(HERE / 'RESOLVED-SOURCES.json'):
    directory = Path(package['manifest_path']).parent
    for name, expected in package['files'].items():
        assert sha(directory / name) == expected, (package['name'], name)

for name, role in read(HERE / 'SOURCE-ROLES.json').items():
    if name.startswith('servo/components/style/'):
        assert sha(HERE / 'baseline' / name) == role['base_sha256']
        assert sha(HERE / 'candidate' / name) == role['candidate_sha256']

assert (HERE / 'baseline/Cargo.lock').read_bytes() == (HERE / 'candidate/Cargo.lock').read_bytes()
print('Verified exact baseline/candidate inputs and resolved dependencies; no compile performed')
