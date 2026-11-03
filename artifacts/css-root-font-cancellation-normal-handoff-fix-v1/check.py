import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


roles = json.loads((HERE / 'SOURCE-ROLES.json').read_text())
for name, role in roles['roles'].items():
    assert digest(HERE / 'base' / name) == role['base_sha256']
    assert digest(HERE / 'candidate' / name) == role['candidate_sha256']
    actual = subprocess.check_output(['git', 'show', roles['revision'] + ':' + name], cwd=ROOT)
    assert hashlib.sha256(actual).hexdigest() == role['base_sha256']
    parsed = subprocess.run(['rustfmt', '--edition', '2024', '--emit', 'stdout',
                             str(HERE / 'candidate' / name)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert parsed.returncode == 0, parsed.stderr.decode()

refs = json.loads((HERE / 'REFERENCES.json').read_text())
for ref in refs:
    assert digest(ROOT / ref['path']) == ref['sha256']
inputs = json.loads((HERE / 'INPUTS.json').read_text())
for record in inputs['resources'].values():
    assert digest(ROOT / record['path']) == record['sha256']
    assert (ROOT / record['path']).read_bytes() == (ROOT / record['origin']['path']).read_bytes()
assert sum(map(len, inputs['expected_subtests'].values())) == 8

source_map = json.loads((HERE / 'SOURCE-MAP.json').read_text())
for name, record in source_map['sources'].items():
    actual = subprocess.check_output(['git', 'show', roles['revision'] + ':' + name], cwd=ROOT)
    assert hashlib.sha256(actual).hexdigest() == record['sha256']
    lines = actual.decode().splitlines()
    for excerpt in record['excerpts']:
        assert '\n'.join(lines[excerpt['start'] - 1:excerpt['end']]) == excerpt['text']

with tempfile.TemporaryDirectory(prefix='normal-handoff-source-') as temp:
    work = Path(temp)
    shutil.copytree(HERE / 'base', work / 'tree')
    for reverse in [False, True]:
        args = ['patch', '--batch', '--fuzz=0', '-p1']
        if reverse:
            args.append('-R')
        patched = subprocess.run(args, cwd=work / 'tree', input=(HERE / 'native.patch').read_bytes(),
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert patched.returncode == 0, patched.stdout.decode()
        expected = 'base' if reverse else 'candidate'
        for name in roles['roles']:
            assert (work / 'tree' / name).read_bytes() == (HERE / expected / name).read_bytes()
    removed = str(work)
assert not Path(removed).exists()

tested = ['check.py', 'native.patch', 'SOURCE-ROLES.json', 'SOURCE-MAP.json',
          'INPUTS.json', 'REFERENCES.json', 'CALLERS.txt']
print(json.dumps({'source_files': len(roles['roles']), 'references': len(refs),
                  'source_excerpts_authenticated': True, 'exact_wpt_callbacks': 8,
                  'roundtrip': True, 'rustfmt_parse_only': True,
                  'native_typecheck': False, 'browser_run': False,
                  'scratch': removed, 'scratch_removed': True,
                  'tested_inputs': {name: digest(HERE / name) for name in tested}}, indent=2))
