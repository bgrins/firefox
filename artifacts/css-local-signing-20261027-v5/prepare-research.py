import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
group = sys.argv[1]
groups = {
    'provider-research': (('css-keyframe-provider-', 'css-keyframe-winning-provider-', 'css-keyframe-animated-cycle-'), 'No bug - Record current-provider resolver validation and cascade research. r?#firefox-style-system-reviewers'),
    'quote-research': (('css-quote-append-', 'css-quote-scope-append-', 'css-nonanimation-next-'), 'No bug - Record contained-quote invalidation model and browser evidence. r?#firefox-style-system-reviewers'),
    'research-checkpoint': (('css-integer-stored-range-', 'css-integer-history-', 'css-steps-origin-library-', 'css-post-provider-'), 'No bug - Checkpoint CSS verification results and current fix ledger. r?#firefox-style-system-reviewers'),
}
prefixes, message = groups[group]
directories = [p for p in (ROOT / 'artifacts').iterdir() if p.is_dir() and p.name.startswith(prefixes)]
if group == 'research-checkpoint':
    directories.extend([HERE, ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v4'])
paths = sorted(str(p.relative_to(ROOT)) for d in directories for p in d.rglob('*')
               if p.is_file() and not any(n in p.parts for n in ('.git', '.lake', '__pycache__', '.DS_Store')))
omit = {'artifacts/css-local-signing-20261027-v5/CURRENT-EPOCH.json'}
paths = sorted(p for p in set(paths) - omit if not (p.startswith('artifacts/css-local-signing-20261027-v5/') and p.endswith('-staged.patch')))
git = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
tracked = set(subprocess.check_output(git + ['ls-files', '-z', '--', *paths], cwd=ROOT, env=env).decode().split('\0'))
files = sorted(set(paths) - tracked)
if group == 'research-checkpoint':
    files.extend(['artifacts/stylo-bloom-tools/CURRENT-COMMITS.json', 'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md', 'artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md', 'artifacts/css-fix-readout-20261023/GROUPS.json', 'artifacts/css-fix-readout-20261023/README.md'])
assert files and len(files) == len(set(files))
assert all((ROOT / p).is_file() and not (ROOT / p).is_symlink() for p in files)
pins = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files}
item = dict(id=group, files=sorted(files), source_pins=pins, source_modes={p: '100755' if (ROOT / p).stat().st_mode & 0o111 else '100644' for p in files}, message=message)
with (HERE / (group + '-input.json')).open('x') as stream:
    json.dump(item, stream, indent=2, sort_keys=True)
    stream.write('\n')
print(group, len(files), 'files', sum((ROOT / p).stat().st_size for p in files), 'bytes')
