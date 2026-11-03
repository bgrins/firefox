import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
OLD = HERE.with_name('css-root-font-cancellation-trace-instrumentation-v1')
NAME = 'layout/style/GeckoBindings.cpp'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
roles = json.loads((HERE / 'SOURCE-ROLES.json').read_bytes())
for name, record in roles.items():
    for role in ('base', 'parent', 'candidate'):
        assert sha(HERE / role / name) == record[role + '_sha256']
        if name != NAME:
            assert (HERE / role / name).read_bytes() == (OLD / role / name).read_bytes()
for path, pin in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
    assert sha(HERE.parents[1] / path) == pin
source = (HERE / 'candidate' / NAME).read_text()
log = (HERE / 'NORMALIZATION-LOG.txt').read_text()
assert source.count(log) == 1
assert source.count('RFTC normalize') == 1
erased = source.replace(log, '', 1).replace('\n#include <cstdio>\n', '', 1)
assert erased == (HERE / 'base' / NAME).read_text()
anchor = '      AnimationUtils::GetElementPseudoPair(aElement);\n'
assert source.index(log) == source.index(anchor, source.index('void Gecko_UpdateAnimations(')) + len(anchor)
formatter = Path('/Users/bgrins/.mozbuild/clang-tools/clang-tidy/bin/clang-format')
formatted = subprocess.run([str(formatter), '--style=Mozilla', str(HERE / 'candidate' / NAME)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
assert formatted.returncode == 0, formatted.stderr
scratch = Path(tempfile.mkdtemp(prefix='css-cancel-normalize-', dir='/private/tmp'))
roundtrips = []
try:
    for role, patch in [('base', 'native.patch'), ('parent', 'INSTRUMENTATION.patch'), ('predecessor', 'PARENT-DELTA.patch')]:
        target = scratch / role
        shutil.copytree(HERE / ('base' if role == 'predecessor' else role), target)
        if role == 'predecessor':
            for name in roles:
                if name != NAME:
                    (target / name).write_bytes((OLD / 'candidate' / name).read_bytes())
        original = {name: (target / name).read_bytes() for name in roles}
        for reverse in (False, True):
            command = ['patch', '-p1', '--batch', '-i', str(HERE / patch)]
            if reverse:
                command.append('-R')
            result = subprocess.run(command, cwd=target, capture_output=True)
            assert result.returncode == 0, result.stdout + result.stderr
            for name in roles:
                expected = original[name] if reverse else (HERE / 'candidate' / name).read_bytes()
                assert (target / name).read_bytes() == expected, name
        roundtrips.append(patch)
finally:
    shutil.rmtree(scratch)
print(json.dumps({'exact_five_role_hashes': True, 'four_predecessor_roles_unchanged': True,
                  'exact_changed_file_logging_erasure': True, 'formatter_parse_exit': formatted.returncode,
                  'roundtrips': roundtrips, 'scratch': str(scratch), 'scratch_removed': not scratch.exists(),
                  'native_typecheck': False, 'browser': False,
                  'tested_inputs': {name: sha(HERE / name) for name in ['check.py', 'SOURCE-ROLES.json', 'NORMALIZATION-LOG.txt', 'native.patch', 'INSTRUMENTATION.patch', 'PARENT-DELTA.patch']}}))
