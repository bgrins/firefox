from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

here = Path(__file__).resolve().parent
root = here.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
roles = read(here / 'SOURCE-ROLES.json')
for name, pin in read(here / 'REFERENCES.json').items():
    assert sha(root / name) == pin
for name, record in read(here / 'SOURCES.json').items():
    assert sha(here / 'base' / name) == record['captured_sha256']
for name, record in roles.items():
    assert sha(here / 'candidate' / name) == record['candidate_sha256']
    if record['base_sha256']:
        assert sha(here / 'base' / name) == record['base_sha256']
subprocess.run(['rustfmt', '--check', '--edition', '2024', '--config-path',
    str(root / 'servo/rustfmt.toml'), *[str(here / 'candidate' / n) for n in roles]], check=True)
with tempfile.TemporaryDirectory(prefix='js-initial-independence-') as directory:
    scratch = Path(directory)
    for name, record in roles.items():
        (scratch / name).parent.mkdir(parents=True, exist_ok=True)
        if record['base_sha256']:
            shutil.copyfile(here / 'base' / name, scratch / name)
    for flags, side in [([], 'candidate'), (['-R'], 'base'), ([], 'candidate')]:
        result = subprocess.run(['patch','--fuzz=0','-p1',*flags,'-i',str(here / 'native.patch')],
            cwd=scratch,check=True,capture_output=True,text=True)
        assert 'offset' not in result.stdout and 'fuzz' not in result.stdout
        expected = {n for n,v in roles.items() if side == 'candidate' or v['base_sha256']}
        assert {str(f.relative_to(scratch)) for f in scratch.rglob('*') if f.is_file()} == expected
        for name in expected:
            assert (scratch / name).read_bytes() == (here / side / name).read_bytes()
print(json.dumps({'native_paths':len(roles),'transport':'forward/reverse/reapply exact',
    'rustfmt':'passed','temporary_scratch':'removed','compiled':False,'browser_tested':False,
    'live_source_or_index_mutations':False}))
