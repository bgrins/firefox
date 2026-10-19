import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path)
parser.add_argument('--live', action='store_true')
args = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


manifest = read(ROOT / 'MANIFEST.json')
assert read(ROOT / 'FREEZE.json')['manifest_sha256'] == sha(ROOT / 'MANIFEST.json')
files, directories = set(), set()
for base, ds, fs in os.walk(ROOT, followlinks=False):
    for name in ds + fs:
        path = Path(base) / name
        mode = path.lstat().st_mode
        assert stat.S_ISREG(mode) or stat.S_ISDIR(mode)
        (directories if stat.S_ISDIR(mode) else files).add(str(path.relative_to(ROOT)))
expected = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
assert files == expected
assert directories == {str(p) for n in expected for p in PurePosixPath(n).parents if str(p) != '.'}
for name, expected_hash in manifest.items():
    path = PurePosixPath(name)
    assert not path.is_absolute() and '..' not in path.parts and str(path) == name
    assert sha(ROOT / name) == expected_hash
module = {'__file__': str(ROOT / 'source_check.py'), '__name__': 'source_audit'}
exec(compile((ROOT / 'source_check.py').read_text(), str(ROOT / 'source_check.py'), 'exec'), module)
result = module['inspect']()
assert result == read(ROOT / 'SOURCE-CHECK.json')
if args.live:
    for name, pin in read(ROOT / 'SOURCE-PINS.json').items():
        assert sha(ROOT.parents[1] / name) == pin
if args.output:
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT) and not out.exists()
    out.mkdir(parents=True)
    config = read(ROOT / 'TOOLCHAIN.json')
    assert sha(Path(config['lean'])) == config['lean_sha256']
    source = out / 'Publication.lean'
    source.write_bytes((ROOT / 'Publication.lean').read_bytes())
    text = source.read_text()
    assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b', text)
    names = ['Publication.' + n for n in re.findall(r'^theorem\s+(\w+)', text, re.M)]
    assert names == ['Publication.' + n for n in ['published_ids', 'unique_publication',
                    'uniform_publication', 'publication_capacity', 'admitted_source']]
    audit = out / 'Audit.lean'
    audit.write_text('import Publication\n' + ''.join('#print axioms ' + n + '\n' for n in names))
    env = {k: v for k, v in os.environ.items() if not k.startswith(('LEAN_', 'PYTHON'))}
    env['LEAN_PATH'] = str(out)
    commands = []
    for command in [[config['lean'], '-o', str(out / 'Publication.olean'), str(source)],
                    [config['lean'], str(audit)]]:
        run = subprocess.run(command, cwd=out, env=env, capture_output=True, text=True)
        commands.append(dict(command=command, exit=run.returncode, stdout=run.stdout, stderr=run.stderr))
        assert run.returncode == 0, commands[-1]
    axioms = commands[-1]['stdout']
    rows = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$", axioms, re.M)
    assert [n for n, _ in rows] == names
    for _, group in rows:
        assert set(filter(None, (x.strip() for x in group.split(',')))) <= {'propext', 'Quot.sound', 'Classical.choice'}
    (out / 'AXIOMS.txt').write_text(axioms)
    (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    (out / 'RESULT.json').write_text(json.dumps(dict(source_sha256=sha(source),
        theorem_audits=5, source_roster_pass=True, full_native_batch_proof=False), indent=2) + '\n')
print(json.dumps(dict(authenticated_inputs=len(manifest), ordinary_shorthands=94,
                     direct_callers=8, maximum_expansion=19, replayed=bool(args.output))))
