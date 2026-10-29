import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (HERE / 'INITIAL-EPOCH.json').exists()
assert read(HERE / 'INPUTS.json')['execution_enabled'] is False
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
head = subprocess.check_output(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=ROOT, env=env).decode().strip()
packages = read(HERE / 'PACKAGES.json')
seen = set()
counts = {}
archived = {}
for group, extras_name in [('research', 'EXTRA-PINS.json'), ('validation', 'VALIDATION-EXTRA-PINS.json')]:
    pins = {}
    def add(name, pin):
        assert name.startswith('artifacts/') and '..' not in Path(name).parts
        path = ROOT / name
        assert path.is_file() and not path.is_symlink() and sha(path) == pin
        assert name not in pins or pins[name] == pin
        pins[name] = pin
    selected_packages = [p for p in packages if p['group'] == group]
    for package in selected_packages:
        directory = ROOT / package['directory']
        assert sha(directory / 'FILES.json') == package['sha256']
        manifest = read(directory / 'FILES.json')
        manifest = manifest.get('files', manifest)
        for name, item in manifest.items():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            add(str((directory / name).relative_to(ROOT)), item if isinstance(item, str) else item['sha256'])
        add(str((directory / 'FILES.json').relative_to(ROOT)), package['sha256'])
    for name, pin in read(HERE / extras_name).items():
        add(name, pin)
    omitted = {}
    for name, pin in list(pins.items()):
        old = subprocess.run(['git', '--no-optional-locks', 'show', head + ':' + name], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if old.returncode == 0 and hashlib.sha256(old.stdout).hexdigest() == pin:
            omitted[name] = pins.pop(name)
    assert not seen.intersection(pins)
    seen.update(pins)
    message = ('No bug - Record sibling-count rule-cache research and paired validation. r?#firefox-style-system-reviewers' if group == 'research' else 'No bug - Record installed sibling-count rule-cache validation. r?#firefox-style-system-reviewers')
    selection = {'id':group, 'files':sorted(pins), 'source_pins':pins, 'message':message}
    (HERE / (group + '-selection-DRAFT.json')).write_text(json.dumps(selection, indent=2, sort_keys=True) + '\n')
    counts[group] = {'packages':len(selected_packages), 'files':len(pins), 'bytes':sum((ROOT/name).stat().st_size for name in pins), 'already_committed_identical':len(omitted)}
    archived.update(omitted)
(HERE / 'SELECTION-CHECK.json').write_text(json.dumps({'head':head, 'groups':counts, 'already_committed_identical':archived, 'frozen':False}, indent=2, sort_keys=True) + '\n')
print(json.dumps(counts, sort_keys=True))
