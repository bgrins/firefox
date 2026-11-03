import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONT = ROOT / 'artifacts/css-keyframe-font-unit-dependency-fix-v1'
ROUTE = ROOT / 'artifacts/css-root-font-cancellation-normal-handoff-fix-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


roles = json.loads((HERE / 'SOURCE-ROLES.json').read_text())
for name, role in roles['roles'].items():
    for stage in ['base', 'parent', 'candidate']:
        assert digest(HERE / stage / name) == role[stage + '_sha256']
    actual = subprocess.check_output(['git', 'show', roles['revision'] + ':' + name], cwd=ROOT)
    assert hashlib.sha256(actual).hexdigest() == role['base_sha256']
    source = FONT / 'candidate' / name
    expected_parent = source if source.exists() else HERE / 'base' / name
    assert (HERE / 'parent' / name).read_bytes() == expected_parent.read_bytes()
    parsed = subprocess.run(['rustfmt', '--edition', '2024', '--emit', 'stdout',
                             str(HERE / 'candidate' / name)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert parsed.returncode == 0, parsed.stderr.decode()

refs = json.loads((HERE / 'REFERENCES.json').read_text())
for ref in refs:
    assert digest(ROOT / ref['path']) == ref['sha256']


def apply(tree, patch, reverse=False):
    command = ['patch', '--batch', '--fuzz=0', '-p1'] + (['-R'] if reverse else [])
    result = subprocess.run(command, cwd=tree, input=patch.read_bytes(),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert result.returncode == 0, result.stdout.decode()


def matches(tree, stage):
    for name in roles['roles']:
        assert (tree / name).read_bytes() == (HERE / stage / name).read_bytes()


with tempfile.TemporaryDirectory(prefix='selective-handoff-source-') as temp:
    work = Path(temp)
    for origin, patch in [('base', 'native.patch'), ('parent', 'PARENT-DELTA.patch')]:
        tree = work / origin
        shutil.copytree(HERE / origin, tree)
        apply(tree, HERE / patch)
        matches(tree, 'candidate')
        apply(tree, HERE / patch, reverse=True)
        matches(tree, origin)
    tree = work / 'composition'
    shutil.copytree(HERE / 'base', tree)
    apply(tree, FONT / 'native.patch')
    matches(tree, 'parent')
    apply(tree, ROUTE / 'native.patch')
    apply(tree, HERE / 'COMPOSITION-HANDOFF-DELTA.patch')
    matches(tree, 'candidate')
    apply(tree, HERE / 'COMPOSITION-HANDOFF-DELTA.patch', reverse=True)
    apply(tree, ROUTE / 'native.patch', reverse=True)
    apply(tree, FONT / 'native.patch', reverse=True)
    matches(tree, 'base')
    removed = str(work)
assert not Path(removed).exists()
assert not list(HERE.rglob('*.orig'))
assert not list(HERE.rglob('*.rej'))

tested = ['check.py', 'native.patch', 'PARENT-DELTA.patch',
          'COMPOSITION-HANDOFF-DELTA.patch', 'SOURCE-ROLES.json', 'REFERENCES.json']
print(json.dumps({'source_files': 4, 'references': len(refs),
                  'forward_reverse_roundtrips': ['base', 'font-parent', 'explicit-three-stage-composition'],
                  'rustfmt_parse_only': True, 'native_typecheck': False, 'browser_run': False,
                  'scratch': removed, 'scratch_removed': True,
                  'tested_inputs': {name: digest(HERE / name) for name in tested}}, indent=2))
