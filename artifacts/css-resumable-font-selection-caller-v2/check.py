import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
roles = json.loads((HERE / 'SOURCE-ROLES.json').read_text())
refs = json.loads((HERE / 'REFERENCES.json').read_text())
for path, digest in refs.items():
    assert sha(ROOT / path) == digest, path
for name, role in roles.items():
    for record in role.values():
        assert sha(ROOT / record['path']) == record['sha256'], record
    prior = (ROOT / role['v1']['path']).read_bytes()
    expected = prior
    if name.endswith('/cascade.rs'):
        assert prior.count(b'type DeclarationIndex = u16;') == 1
        expected = prior.replace(b'type DeclarationIndex = u16;', b'type DeclarationIndex = u32;')
    assert (ROOT / role['candidate']['path']).read_bytes() == expected
for key, patch in [('base', 'native.patch'), ('v1', 'CAPACITY-REBASE.patch')]:
    expected = ''.join(''.join(difflib.unified_diff(
        (ROOT / role[key]['path']).read_text().splitlines(True),
        (ROOT / role['candidate']['path']).read_text().splitlines(True),
        fromfile='a/' + name, tofile='b/' + name,
    )) for name, role in roles.items())
    assert (HERE / patch).read_text() == expected
    with tempfile.TemporaryDirectory(prefix='retained-caller-u32-', dir='/private/tmp') as directory:
        scratch = Path(directory)
        for name, role in roles.items():
            target = scratch / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / role[key]['path'], target)
        for reverse in [False, True]:
            command = ['patch', '--fuzz=0', '-p1', '-i', str(HERE / patch)]
            if reverse:
                command.append('-R')
            result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
            assert result.returncode == 0, (command, result.stdout, result.stderr)
            for name, role in roles.items():
                assert sha(scratch / name) == role[key if reverse else 'candidate']['sha256']
    assert not scratch.exists()
print(json.dumps({'roles': 3, 'references': len(refs), 'alias_only_rebase': True,
                  'provider_and_mod_unchanged': True, 'exact_patches': 2,
                  'zero_fuzz_forward_reverse': True, 'scratch_absent': True,
                  'native_typecheck': False, 'extracted_tests_rerun': False}))
