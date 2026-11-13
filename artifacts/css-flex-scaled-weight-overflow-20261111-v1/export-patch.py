import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
SOURCE = 'layout/generic/nsFlexContainerFrame.cpp'
TEST = 'testing/web-platform/tests/css/css-flexbox/flex-shrink-large-finite-scaled-weights.html'
head = subprocess.check_output(GIT + ['rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert head == '5fcf976eeb79ddc057e9c73d7b73a422058b1903'
before = (HERE / 'before.cpp').read_text()
after = (ROOT / SOURCE).read_text()
assert after == before.replace('float GetWeight(bool aIsUsingFlexGrow)',
                              'double GetWeight(bool aIsUsingFlexGrow)').replace(
                                  'return mFlexShrink * mFlexBaseSize;',
                                  'return double(mFlexShrink) * mFlexBaseSize;')
test = (ROOT / TEST).read_text()
chunks = ['diff --git a/' + SOURCE + ' b/' + SOURCE + '\n']
chunks.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                 fromfile='a/' + SOURCE, tofile='b/' + SOURCE))
chunks += ['diff --git a/' + TEST + ' b/' + TEST + '\n', 'new file mode 100644\n']
chunks.extend(difflib.unified_diff([], test.splitlines(True), fromfile='/dev/null', tofile='b/' + TEST))
patch = HERE / 'standalone.patch'
with patch.open('x') as stream:
    stream.write(''.join(chunks))
head_source = subprocess.check_output(GIT + ['show', head + ':' + SOURCE], cwd=ROOT, text=True)
commands = []
with tempfile.TemporaryDirectory(prefix='css-flex-weight-patch-', dir='/private/tmp') as directory:
    parent = Path(directory)
    for label, initial in [('head', head_source), ('combined', before)]:
        work = parent / label
        source = work / SOURCE
        source.parent.mkdir(parents=True)
        source.write_text(initial)
        for reverse in [False, True]:
            for check in [True, False]:
                argv = GIT + ['apply'] + (['--reverse'] if reverse else []) + (['--check'] if check else []) + [str(patch)]
                result = subprocess.run(argv, cwd=work, capture_output=True, text=True)
                commands.append({'argv': argv, 'cwd': str(work), 'exit': result.returncode,
                                 'stdout': result.stdout, 'stderr': result.stderr})
                (HERE / 'PATCH-COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
                assert result.returncode == 0, commands[-1]
            if not reverse:
                expected = initial.replace('float GetWeight(bool aIsUsingFlexGrow)',
                                           'double GetWeight(bool aIsUsingFlexGrow)').replace(
                                               'return mFlexShrink * mFlexBaseSize;',
                                               'return double(mFlexShrink) * mFlexBaseSize;')
                assert source.read_text() == expected
                assert (work / TEST).read_text() == test
            else:
                assert source.read_text() == initial and not (work / TEST).exists()
result = {'head': head, 'paths': [SOURCE, TEST], 'commands': len(commands),
          'head_and_combined_apply_reverse': True, 'scratch_removed': not Path(directory).exists(),
          'patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(),
          'scope': 'Two-path patch transport; runtime checks use the combined local branch.'}
(HERE / 'PATCH-RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
