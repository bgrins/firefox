import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
SOURCE = 'servo/components/style/custom_properties.rs'
TEST = 'testing/web-platform/tests/css/css-variables/trailing-backslash-newline.html'

def git(*args, env=None, data=None):
    return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=REPO, env=env, input=data)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def adapt(data):
    source = data.decode()
    def replace(old, new, count=1):
        nonlocal source
        if source.count(old) != count:
            raise RuntimeError('Unexpected source shape: ' + old)
        source = source.replace(old, new)
    if 'trailing_whitespace_len' in source:
        replace('    let mut trailing_whitespace_len = 0;',
                '    let mut trailing_whitespace_len = 0;\n    let mut last_token_was_backslash = false;')
        replace('            Token::WhiteSpace(value) => value.len(),',
                '            // A backslash delimiter needs its following newline when reserialized.\n'
                '            Token::WhiteSpace(value) if !last_token_was_backslash => value.len(),')
        replace('        if !matches!(token, Token::WhiteSpace(_)) {',
                "        last_token_was_backslash = matches!(token, Token::Delim('\\\\'));\n"
                '        if !matches!(token, Token::WhiteSpace(_)) {')
    else:
        replace('let (first_token_type, last_token_type) =',
                'let (first_token_type, last_token_type, preserve_trailing_whitespace) =')
        replace('        css.truncate(css.trim_ascii_end().len());',
                '        if !preserve_trailing_whitespace {\n'
                '            css.truncate(css.trim_ascii_end().len());\n'
                '        }')
        replace(') -> Result<(TokenSerializationType, TokenSerializationType), ParseError> {',
                ') -> Result<(TokenSerializationType, TokenSerializationType, bool), ParseError> {', 2)
        replace('    let mut last_token_type = TokenSerializationType::Nothing;',
                '    let mut last_token_type = TokenSerializationType::Nothing;\n'
                '    let mut preserve_trailing_whitespace = false;')
        replace('        last_token_type = serialization_type;',
                '        last_token_type = serialization_type;\n'
                '        if !matches!(token, Token::WhiteSpace(_)) {\n'
                '            // A backslash delimiter needs its following newline when reserialized.\n'
                "            preserve_trailing_whitespace = matches!(token, Token::Delim('\\\\'));\n"
                '        }')
        replace('let (first, last) = parse_declaration_value(',
                'let (first, last, _) = parse_declaration_value(')
        replace('    Ok((first_token_type, last_token_type))',
                '    Ok((first_token_type, last_token_type, preserve_trailing_whitespace))')
    return source.encode()

candidate = json.loads((ROOT / 'CANDIDATE.json').read_text())
before = (ROOT / 'before.rs').read_bytes()
tested = (ROOT / 'candidate.rs').read_bytes()
if sha(before) != json.loads((ROOT / 'BASELINE.json').read_text())['source_sha256'] or sha(tested) != candidate['source_sha256']:
    raise RuntimeError('Retained source changed')
if adapt(before) != tested or (REPO / SOURCE).read_bytes() != tested:
    raise RuntimeError('Adaptation differs from tested candidate')
run = json.loads((ROOT / 'candidate-wpt-v1/RUN.json').read_text())
test_bytes = (REPO / TEST).read_bytes()
if not run['complete'] or run['after'][TEST] != sha(test_bytes):
    raise RuntimeError('Test differs from passing run')
head = git('rev-parse', 'HEAD').decode().strip()
index = git('write-tree')
record = {}
for label, base in [('head', head), ('standalone', '976279105b2e78b8666a959eb3f25c9176cefaf8')]:
    original = git('show', base + ':' + SOURCE)
    changed = adapt(original)
    folder = ROOT / ('package-' + label)
    folder.mkdir(exist_ok=False)
    (folder / 'original.rs').write_bytes(original)
    (folder / 'candidate.rs').write_bytes(changed)
    with tempfile.TemporaryDirectory(prefix='css-backslash-newline-index-', dir='/private/tmp') as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / 'index'))
        git('read-tree', base, env=env)
        for name, data in [(SOURCE, changed), (TEST, test_bytes)]:
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
record['integration_adaptation_equals_tested_candidate'] = True
record['limits'] = 'Source-only independent applicability; no isolated build/browser of either packaged variant. Both packages exclude all three preceding whitespace repairs and preserve their base EOF behavior. Standalone variants return a dedicated preservation flag; the tested integration uses the existing raw-span field. Correspondence requires maximal whitespace tokens.'
(ROOT / 'PACKAGING.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
