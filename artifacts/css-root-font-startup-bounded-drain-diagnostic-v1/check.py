from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'css-root-font-startup-queue-trace-instrumentation-v1'
ROLE = 'layout/style/ServoStyleSet.cpp'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
roles = json.loads((HERE / 'SOURCE-ROLES.json').read_text())['roles']
for path, pins in roles.items():
    for kind in ['base', 'parent', 'candidate']:
        assert sha(HERE / kind / path) == pins[kind + '_sha256']
    assert (HERE / 'parent' / path).read_bytes() == (PARENT / 'candidate' / path).read_bytes()
    if path != ROLE:
        assert (HERE / 'candidate' / path).read_bytes() == (HERE / 'parent' / path).read_bytes()
candidate = (HERE / 'candidate' / ROLE).read_text()
parent = (HERE / 'parent' / ROLE).read_text()
addition = (HERE / 'ADDITION.cpp').read_text()
assert candidate.count(addition) == 1
assert candidate.replace(addition, '') == parent
assert candidate[candidate.index('void ServoStyleSet::StyleNewSubtree('):] == parent[parent.index('void ServoStyleSet::StyleNewSubtree('):]
assert addition.count('PreTraverse(aFlags)') == 1
assert addition.index('PreTraverse(aFlags)') < addition.index('GetServoRestyleRoot()') < addition.index('AutoPrepareTraversal guard(this)')
assert 'additionalAnimationPasses < kMaxAdditionalAnimationPasses' in addition
assert 'kMaxAdditionalAnimationPasses = 16' in addition
body = '''      AutoPrepareTraversal guard(this);
      postTraversalRequired |=
          Servo_TraverseSubtree(root, mRawData.get(), &snapshots, aFlags) ||
          root->HasAnyOfFlags(Element::kAllServoDescendantBits |
                              NODE_NEEDS_FRAME);
'''
assert body in parent and body in addition
with tempfile.TemporaryDirectory(prefix='css-bounded-drain-') as td:
    scratch = Path(td)
    for origin, filename in [('base', 'native.patch'), ('parent', 'PARENT-DELTA.patch')]:
        tree = scratch / origin
        shutil.copytree(HERE / origin, tree)
        for reverse in [False, True]:
            result = subprocess.run(['patch', '-p1', '--batch', '--fuzz=0'] + (['-R'] if reverse else []), cwd=tree, input=(HERE / filename).read_bytes(), capture_output=True)
            assert result.returncode == 0, result.stdout + result.stderr
            assert b'offset' not in result.stdout and b'fuzz' not in result.stdout
            for path in roles:
                assert (tree / path).read_bytes() == (HERE / (origin if reverse else 'candidate') / path).read_bytes()
    result = subprocess.run(['/Users/bgrins/.mozbuild/clang-tools/clang-tidy/bin/clang-format', str(HERE / 'candidate' / ROLE)], capture_output=True)
    assert result.returncode == 0, result.stderr
assert not Path(td).exists()
result = {'source_roles': 10, 'unchanged_parent_candidates': 9, 'one_exact_insertion_erased': True, 'existing_passes_and_StyleNewSubtree_unchanged': True, 'added_traversal_body_matches_existing_second_pass': True, 'zero_fuzz_forward_reverse_checks': 4, 'changed_cpp_formatter_parser': True, 'native_typecheck': False, 'browser_run': False, 'scratch_removed': td, 'tested': {n: sha(HERE / n) for n in ['prepare.py', 'check.py', 'ADDITION.cpp', 'SOURCE-ROLES.json', 'native.patch', 'PARENT-DELTA.patch']}}
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
