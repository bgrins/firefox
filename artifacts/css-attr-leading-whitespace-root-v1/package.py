import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
SOURCE = 'servo/components/style/custom_properties.rs'
TEST = 'testing/web-platform/tests/css/css-values/attr-substitution-leading-whitespace.html'

def git(*args, env=None, data=None):
    return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args],
                                   cwd=REPO, env=env, input=data)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def adapt(source):
    start = source.index('    pub fn parse(\n        input: &mut Parser,\n        namespaces:')
    end = source.index('    /// Returns whether this value is tainted', start)
    body = source[start:end]
    old = '        let mut references = References::default();'
    new = '''        let state = input.state();
        if !matches!(
            input.next_including_whitespace_and_comments(),
            Ok(Token::WhiteSpace(_))
        ) {
            input.reset(&state);
        }
        let mut references = References::default();'''
    trim = '''        let mut css = input
            .slice_from(start_position)
            .trim_ascii_start()
            .to_owned();'''
    if body.count(old) != 1 or body.count(trim) != 1:
        raise RuntimeError('Unexpected source shape')
    body = body.replace(old, new).replace(trim, '        let mut css = input.slice_from(start_position).to_owned();')
    return (source[:start] + body + source[end:]).encode()

candidate = json.loads((ROOT / 'CANDIDATE.json').read_text())
if sha((REPO / SOURCE).read_bytes()) != candidate['candidate_sha256']:
    raise RuntimeError('Candidate changed')
if sha((REPO / TEST).read_bytes()) != candidate['wpt']['sha256']:
    raise RuntimeError('Test changed')
head = git('rev-parse', 'HEAD').decode().strip()
index = git('write-tree')
record = {}
for label, base in [('head', head), ('standalone', '976279105b2e78b8666a959eb3f25c9176cefaf8')]:
    original = git('show', base + ':' + SOURCE)
    changed = adapt(original.decode())
    if label == 'head' and changed != (REPO / SOURCE).read_bytes():
        raise RuntimeError('HEAD adaptation differs from tested candidate')
    folder = ROOT / ('package-' + label)
    folder.mkdir(exist_ok=False)
    (folder / 'original.rs').write_bytes(original)
    (folder / 'candidate.rs').write_bytes(changed)
    with tempfile.TemporaryDirectory(prefix='css-attr-origin-index-', dir='/private/tmp') as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / 'index'))
        git('read-tree', base, env=env)
        for name, data in [(SOURCE, changed), (TEST, (REPO / TEST).read_bytes())]:
            blob = git('hash-object', '-w', '--stdin', data=data).decode().strip()
            git('update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + name, env=env)
        tree = git('write-tree', env=env).decode().strip()
        paths = git('diff', '--name-only', base, tree).decode().splitlines()
        if sorted(paths) != sorted([SOURCE, TEST]):
            raise RuntimeError('Unexpected patch roster')
        patch = git('diff', '--binary', '--full-index', base, tree, '--', SOURCE, TEST)
        output = ROOT / (label + '-native-wpt.patch')
        output.write_bytes(patch)
        git('apply', '--cached', '--reverse', '--check', str(output), env=env)
        git('apply', '--cached', '--reverse', str(output), env=env)
        if git('write-tree', env=env) != git('rev-parse', base + '^{tree}'):
            raise RuntimeError('Reverse did not restore base')
        git('apply', '--cached', '--check', str(output), env=env)
        git('apply', '--cached', str(output), env=env)
        if git('write-tree', env=env).decode().strip() != tree:
            raise RuntimeError('Forward did not restore candidate')
        record[label] = {'base': base, 'candidate_tree': tree, 'paths': paths,
                         'patch': str(output.relative_to(REPO)), 'sha256': sha(patch),
                         'source_sha256': sha(changed), 'exact_apply_reverse': True}
if git('rev-parse', 'HEAD').decode().strip() != head or git('write-tree') != index:
    raise RuntimeError('Real HEAD or index changed')
record['real_head_and_index_preserved'] = True
record['limits'] = 'Source-only standalone applicability; no isolated upstream build/browser. The upstream adaptation preserves its own existing EOF-repair code.'
(ROOT / 'PACKAGING.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
