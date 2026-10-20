import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCES = ['servo/components/style/properties/mod.rs',
           'servo/components/style/properties/cascade.rs',
           'servo/components/style/properties_and_values/value.rs']
TEST = 'testing/web-platform/tests/css/css-properties-values-api/animation-invalid-inherit-publication.html'


def git(*args, env=None, data=None):
    return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args],
                                   cwd=ROOT, env=env, input=data)


def sha(data):
    return hashlib.sha256(data).hexdigest()


inputs = json.loads((HERE / 'INPUTS.json').read_text())
for name, expected in inputs.items():
    assert sha((HERE / name).read_bytes()) == expected
head = git('rev-parse', 'HEAD').decode().strip()
initial_index = git('write-tree').decode().strip()
result = {}
for label, base in [('head', head), ('standalone', '976279105b2e78b8666a959eb3f25c9176cefaf8')]:
    with tempfile.TemporaryDirectory(prefix='invalid-publication-package-', dir='/private/tmp') as temp:
        env = {**os.environ, 'GIT_INDEX_FILE': str(Path(temp) / 'index')}
        git('read-tree', base, env=env)
        git('apply', '--cached', '--check', str(HERE / 'native.patch'), env=env)
        git('apply', '--cached', str(HERE / 'native.patch'), env=env)
        pins = {}
        for name in SOURCES:
            source = git('show', ':' + name, env=env)
            output = HERE / label / Path(name).relative_to('servo/components/style')
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(source)
            pins[name] = sha(source)
        blob = git('hash-object', '-w', '--stdin', data=(HERE / 'landing.html').read_bytes()).decode().strip()
        git('update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + TEST, env=env)
        pins[TEST] = inputs['landing.html']
        tree = git('write-tree', env=env).decode().strip()
        paths = git('diff', '--name-only', base, tree).decode().splitlines()
        assert sorted(paths) == sorted(SOURCES + [TEST])
        patch = git('diff', '--binary', '--full-index', base, tree, '--', *SOURCES, TEST)
        output = HERE / (label + '-native-wpt.patch')
        output.write_bytes(patch)
        git('apply', '--cached', '--reverse', '--check', str(output), env=env)
        git('apply', '--cached', '--reverse', str(output), env=env)
        assert git('write-tree', env=env) == git('rev-parse', base + '^{tree}')
        result[label] = {'base': base, 'patch': str(output.relative_to(ROOT)), 'patch_sha256': sha(patch),
                         'candidate_tree': tree, 'paths': paths, 'pins': pins, 'exact_apply_reverse': True}
assert git('rev-parse', 'HEAD').decode().strip() == head
assert git('write-tree').decode().strip() == initial_index
result['limits'] = 'Source packaging only. Shared-tree browser evidence contains earlier repairs; neither isolated HEAD nor upstream runtime was run. Pending fix81 is not included in these patches.'
result['real_head_and_index_preserved'] = True
(HERE / 'PACKAGING.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
