from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'css-root-font-startup-trace-instrumentation-v1'
roles = json.loads((HERE / 'SOURCE-ROLES.json').read_text())['roles']
for path, pins in json.loads((OLD / 'SOURCE-ROLES.json').read_text())['roles'].items():
    assert (HERE / 'candidate' / path).read_bytes() == (OLD / 'candidate' / path).read_bytes()
edits = json.loads((HERE / 'EDITS.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for path, pins in roles.items():
    for kind in ['base', 'parent', 'candidate']:
        assert sha(HERE / kind / path) == pins[kind + '_sha256']
    text = (HERE / 'candidate' / path).read_text()
    for edit in reversed(edits):
        if edit['path'] != path:
            continue
        assert text.count(edit['new']) == 1
        text = text.replace(edit['new'], edit['old'])
    assert text == (HERE / 'parent' / path).read_text()
with tempfile.TemporaryDirectory(prefix='css-startup-trace-') as td:
    scratch = Path(td)
    for origin, patch in [('base', 'native.patch'), ('parent', 'PARENT-DELTA.patch')]:
        tree = scratch / origin
        shutil.copytree(HERE / origin, tree)
        for reverse in [False, True]:
            command = ['patch', '-p1', '--batch', '--fuzz=0'] + (['-R'] if reverse else [])
            result = subprocess.run(command, cwd=tree, input=(HERE / patch).read_bytes(), capture_output=True)
            assert result.returncode == 0, result.stdout + result.stderr
            assert b'offset' not in result.stdout and b'fuzz' not in result.stdout
            expected = origin if reverse else 'candidate'
            for path in roles:
                assert (tree / path).read_bytes() == (HERE / expected / path).read_bytes()
    for path in ['dom/animation/EffectCompositor.cpp', 'layout/style/ServoStyleSet.cpp']:
        source = HERE / 'candidate' / path
        if path.endswith('.rs'):
            command = ['rustfmt', '--edition', '2024', '--emit', 'stdout', '--config', 'skip_children=true,match_block_trailing_comma=true', str(source)]
        else:
            command = ['/Users/bgrins/.mozbuild/clang-tools/clang-tidy/bin/clang-format', str(source)]
        result = subprocess.run(command, capture_output=True)
        assert result.returncode == 0, result.stderr.decode()
        assert sha(source) == roles[path]['candidate_sha256']
    scratch_name = str(scratch)
assert not Path(scratch_name).exists()
result = {
    'source_roles': len(roles),
    'exact_logging_replacements_erased': len(edits),
    'zero_fuzz_forward_reverse_checks': 4,
    'formatter_parser_acceptance': {'new_cpp': 2, 'unchanged_eight_roles_not_repeated': True},
    'native_typecheck': False,
    'browser_run': False,
    'scratch_removed': scratch_name,
    'tested': {str(p.relative_to(HERE)): sha(p) for p in [HERE / 'check.py', HERE / 'prepare.py', HERE / 'EDITS.json', HERE / 'SOURCE-ROLES.json', HERE / 'PARENT-DELTA.patch', HERE / 'native.patch']},
}
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
