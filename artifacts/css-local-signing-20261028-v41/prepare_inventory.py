import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (HERE / 'INITIAL-EPOCH.json').exists(), 'Selections are frozen once signing starts'
inputs = read(HERE / 'INPUTS.json')
assert inputs['execution_enabled'] is False
packages = read(HERE / 'PACKAGES.json')
extras = read(HERE / 'EXTRA-PINS.json')
seen = set()
counts = {}
for group in ('research', 'validation'):
    selection = read(HERE / (group + '-selection.json'))
    pins = {}
    for package in packages[group]:
        directory = ROOT / package['path']
        assert sha(directory / 'FILES.json') == package['manifest_sha256']
        manifest = read(directory / 'FILES.json')
        manifest = manifest.get('files', manifest)
        for name, item in manifest.items():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            path = directory / name
            pin = item if isinstance(item, str) else item['sha256']
            assert path.is_file() and not path.is_symlink() and sha(path) == pin
            pins[str(path.relative_to(ROOT))] = pin
        pins[str((directory / 'FILES.json').relative_to(ROOT))] = package['manifest_sha256']
    for name, pin in extras[group].items():
        assert name.startswith('artifacts/') and '..' not in Path(name).parts
        assert not (ROOT / name).is_symlink() and sha(ROOT / name) == pin
        assert name not in pins or pins[name] == pin
        pins[name] = pin
    assert not seen.intersection(pins)
    seen.update(pins)
    selection.update(files=sorted(pins), source_pins=pins)
    (HERE / (group + '-selection.json')).write_text(json.dumps(selection, indent=2, sort_keys=True) + '\n')
    counts[group] = {'packages':len(packages[group]), 'files':len(pins), 'bytes':sum((ROOT/name).stat().st_size for name in pins)}
(HERE / 'INVENTORY.json').write_text(json.dumps(counts, indent=2) + '\n')
print(json.dumps(counts, sort_keys=True))
