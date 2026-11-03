import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
OLD = HERE.with_name('css-root-font-cancellation-trace-instrumentation-v2')
NAME = 'servo/components/style/matching.rs'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
roles = json.loads((HERE / 'SOURCE-ROLES.json').read_bytes())
for name, record in roles.items():
    for role in ('base', 'parent', 'candidate'):
        assert sha(HERE / role / name) == record[role + '_sha256']
        if name != NAME or role != 'candidate':
            assert (HERE / role / name).read_bytes() == (OLD / role / name).read_bytes()
for name, pin in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
    assert sha(HERE.parents[1] / name) == pin
before = (OLD / 'candidate' / NAME).read_text()
after = (HERE / 'candidate' / NAME).read_text()
old_import = 'use crate::dom::TElement;\n#[cfg(feature = "servo")]\nuse crate::dom::TNode;'
new_import = 'use crate::dom::{TElement, TNode};'
old_line = next(line for line in before.splitlines() if 'RFTC animation-task' in line)
new_line = old_line.replace('tasks={:?}', 'tasks={:#x}').replace('traversal_flags, tasks,', 'traversal_flags, tasks.bits(),')
assert after == before.replace(old_import, new_import, 1).replace(old_line, new_line, 1)
erasure_source = (HERE.with_name('css-root-font-cancellation-trace-instrumentation-v1') / 'check.py').read_text()
function = next(n for n in ast.parse(erasure_source).body if isinstance(n, ast.FunctionDef) and n.name == 'erase')
scope = {'re': re}
exec(compile(ast.Module(body=[function], type_ignores=[]), '<unchanged predecessor erasure function>', 'exec'), scope)
assert scope['erase'](after.replace(new_import, old_import, 1)) == '\n'.join(line for line in (HERE / 'parent' / NAME).read_text().splitlines() if line.strip())
type_sources = json.loads((HERE / 'TYPE-SOURCE.json').read_bytes())
for name, record in type_sources.items():
    body = subprocess.check_output(['git', 'show', record['commit'] + ':' + name], cwd=HERE.parents[1])
    assert hashlib.sha256(body).hexdigest() == record['sha256']
    assert all(excerpt in body.decode() for excerpt in record['excerpts'])
cpp = type_sources['layout/style/ServoTypes.h']['excerpts'][0]
rust = type_sources['servo/components/style/context.rs']['excerpts'][0]
assert 'EffectProperties = 1 << 2' in cpp
assert 'const EFFECT_PROPERTIES = structs::UpdateAnimationsTasks_EffectProperties;' in rust
assert 'tasks.bits(),' in type_sources['servo/components/style/gecko/wrapper.rs']['excerpts'][0]
fmt = subprocess.run(['rustfmt', '--edition', '2024', '--emit', 'stdout', str(HERE / 'candidate' / NAME)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
assert fmt.returncode == 0, fmt.stderr
scratch = Path(tempfile.mkdtemp(prefix='css-cancel-trace-types-', dir='/private/tmp'))
roundtrips = []
try:
    for role, patch in [('base', 'native.patch'), ('parent', 'INSTRUMENTATION.patch'), ('predecessor', 'PARENT-DELTA.patch')]:
        directory = scratch / role
        shutil.copytree(OLD / 'candidate' if role == 'predecessor' else HERE / role, directory)
        original = {name: (directory / name).read_bytes() for name in roles}
        for reverse in (False, True):
            cmd = ['patch', '-p1', '--batch', '-i', str(HERE / patch)]
            if reverse:
                cmd.append('-R')
            result = subprocess.run(cmd, cwd=directory, capture_output=True)
            assert result.returncode == 0, result.stdout + result.stderr
            for name in roles:
                assert (directory / name).read_bytes() == (original[name] if reverse else (HERE / 'candidate' / name).read_bytes())
        roundtrips.append(patch)
finally:
    shutil.rmtree(scratch)
print(json.dumps({'exact_two_edits': True, 'four_other_candidate_roles_unchanged': True,
                  'all_base_and_parent_bytes_unchanged': True, 'changed_file_logging_erasure': True,
                  'rust_mask_passed_to_cpp_unchanged': True, 'effect_properties_mask': 4,
                  'parser_exit': fmt.returncode, 'roundtrips': roundtrips,
                  'scratch': str(scratch), 'scratch_removed': not scratch.exists(),
                  'native_typecheck': False, 'native_build_or_browser': False,
                  'tested_inputs': {name: sha(HERE / name) for name in ['check.py', 'SOURCE-ROLES.json', 'TYPE-SOURCE.json', 'PARENT-DELTA.patch', 'native.patch', 'INSTRUMENTATION.patch']}}))
