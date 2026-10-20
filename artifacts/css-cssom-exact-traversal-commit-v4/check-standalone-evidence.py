import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ENV = {**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}
HEAD = '99a9ca84f08370c1797720db8688bcb3747f6985'

def require(ok, message):
    if not ok:
        raise SystemExit(message)

def read(path):
    def unique(items):
        result = {}
        for name, value in items:
            require(name not in result, 'Duplicate key: ' + name)
            result[name] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)

def sha(path):
    require(path.is_file() and not path.is_symlink(), 'Not a regular input: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, env=ENV)

def capsule(entry):
    root = ROOT / entry['path']
    require(sha(root / 'FILES.json') == entry['FILES_sha256'], 'Manifest pin')
    manifest = read(root / 'FILES.json')
    expected = set(manifest) | {'FILES.json'}
    if entry.get('FREEZE_sha256'):
        require(sha(root / 'FREEZE.json') == entry['FREEZE_sha256'], 'Freeze pin')
        expected.add('FREEZE.json')
    directories = {'.'}
    for name, pin in manifest.items():
        path = Path(name)
        require(not path.is_absolute() and '..' not in path.parts and path.as_posix() == name, 'Unsafe member')
        require(sha(root / name) == pin, 'Capsule payload: ' + name)
        directories.update(str(p) for p in path.parents)
    actual = set()
    for path in root.rglob('*'):
        require(not path.is_symlink(), 'Capsule symlink')
        name = path.relative_to(root).as_posix()
        if path.is_file():
            actual.add(name)
        else:
            require(path.is_dir() and name in directories, 'Unexpected directory: ' + name)
    require(actual == expected, 'Closed roster: ' + str(root))
    require(len(manifest) == entry['payloads'], 'Payload count')
    return {str((root / n).relative_to(ROOT)): sha(root / n) for n in sorted(actual)}

def check():
    item = read(HERE / 'standalone-evidence-draft.json')
    audit = read(HERE / 'STANDALONE-EVIDENCE-AUDIT.json')
    require(sha(HERE / 'standalone-evidence-draft.json') == audit['recipe_sha256'], 'Recipe pin')
    require(item['expected_head'] == 'FINALIZE_AFTER_FIVE_PRECEDING_RESEARCH_COMMITS', 'Draft HEAD')
    require(item['files'] == sorted(item['source_pins']) and len(item['files']) == len(set(item['files'])), 'Roster')
    for name, pin in item['source_pins'].items():
        require(name.startswith('artifacts/') and '..' not in Path(name).parts, 'Artifact-only roster')
        require(not name.startswith('artifacts/css-cssom-exact-traversal-standalone-v4/'), 'Unsealed runtime excluded')
        require(sha(ROOT / name) == pin, 'New recipe input: ' + name)
    prior = {}
    for entry in item['dependencies']['preceding_recipes']:
        require(sha(ROOT / entry['path']) == entry['sha256'], 'Prior recipe pin')
        recipe = read(ROOT / entry['path'])
        require(sorted(recipe['files']) == sorted(recipe['source_pins']) and len(recipe['files']) == len(set(recipe['files'])), 'Prior roster')
        for name, pin in recipe['source_pins'].items():
            require(sha(ROOT / name) == pin, 'Prior payload: ' + name)
            require(name not in prior or prior[name] == pin, 'Prior conflict')
            prior[name] = pin
    require(not set(prior) & set(item['source_pins']), 'Duplicate prior evidence')
    expected = {}
    for entry in item['sealed_capsules']:
        expected.update(capsule(entry))
    expected.update(audit['root_receipts'])
    require(expected == item['source_pins'], 'Exact capsule and receipt roster')
    combined = {**prior, **item['source_pins']}
    history = item['dependencies']['committed_inputs']
    for entry in history:
        name, pin = entry['path'], entry['sha256']
        require(hashlib.sha256(git('show', HEAD + ':' + name)).hexdigest() == pin, 'Historical committed input')
        require(sha(ROOT / name) == pin, 'Retained committed input')
        combined[name] = pin
    capture = ROOT / 'artifacts/css-cssom-exact-traversal-standalone-postprocess-v4/runtime-capture'
    inputs = read(capture / 'INPUTS.json')['pins']
    counts = {'preceding_recipe': 0, 'remapped_capture': 0, 'committed_history': 0, 'native_test_capture': 0}
    sources = {'layout/generic/nsIFrame.cpp', 'layout/generic/nsIFrame.h', 'layout/base/nsLayoutUtils.cpp', 'layout/base/nsLayoutUtils.h', 'dom/base/DOMRect.cpp'}
    prefix = 'artifacts/css-cssom-exact-traversal-standalone-v4/'
    for name, pin in inputs.items():
        if name.startswith(prefix):
            path = capture / name[len(prefix):]
            kind = 'remapped_capture'
        elif name.startswith('artifacts/'):
            require(combined.get(name) == pin, 'Uncovered artifact dependency: ' + name)
            path = ROOT / name
            kind = 'preceding_recipe' if name in prior else 'committed_history'
        else:
            path = capture / ('original' if name in sources else 'standalone/inputs') / name
            kind = 'native_test_capture'
        require(sha(path) == pin, '400-input binding: ' + name)
        if kind in ('remapped_capture', 'native_test_capture'):
            require(combined.get(str(path.relative_to(ROOT))) == pin, 'Capture not in recipe')
        counts[kind] += 1
    require(counts == audit['standalone_input_coverage'] and sum(counts.values()) == 400, 'Dependency counts')
    acceptance = read(ROOT / 'artifacts/css-cssom-exact-traversal-acceptance-v4/ACCEPTANCE.json')
    for name, pin in acceptance['evidence_pins'].items():
        require(combined.get(name) == pin, 'Acceptance dependency: ' + name)
    helper = item['dependencies']['commit_helper']
    require(sha(ROOT / helper['path']) == helper['sha256'], 'Helper pin')
    stage = read(HERE / 'SIGNING-RESUME-PREFLIGHT.json')
    require(sha(HERE / 'SIGNING-RESUME-PREFLIGHT.json') == audit['signing_preflight_sha256'], 'Historical preflight pin')
    first = read(ROOT / item['dependencies']['preceding_recipes'][0]['path'])
    require(stage['staged_blob_pins'] == first['source_pins'], 'Historical staged first recipe')
    require(stage['head'] == HEAD and stage['previous_receipt']['before'] == stage['previous_receipt']['after'] == HEAD, 'Historical failed attempt')
    require(stage['previous_receipt']['exit_code'] == 128 and stage['staged_count'] == 229, 'Historical failure state')
    print(json.dumps({'status': 'PASS_PRECEDING_EVIDENCE_DRAFT', 'files': len(item['files']), 'prior_files': len(prior), 'captured_input_coverage': counts, 'historical_head': HEAD, 'production_files': 0, 'signer_executed': False}, sort_keys=True))

if __name__ == '__main__':
    require(not sys.argv[1:], 'No arguments')
    check()
