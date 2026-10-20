import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise SystemExit(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    def unique(items):
        result = {}
        for name, value in items:
            require(name not in result, 'Duplicate JSON key')
            result[name] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)

require(len(sys.argv) == 3 and sys.argv[1] == '--files-sha256', 'verify.py --files-sha256 PIN')
require(sha(ROOT / 'FILES.json') == sys.argv[2], 'External manifest pin')
files = load(ROOT / 'FILES.json')
directories = {'.'}
for name, pin in files.items():
    path = Path(name)
    require(not path.is_absolute() and '..' not in path.parts and path.as_posix() == name, 'Unsafe path')
    require(sha(ROOT / name) == pin, 'Payload: ' + name)
    directories.update(str(p) for p in path.parents)
actual = set()
for path in ROOT.rglob('*'):
    require(not path.is_symlink(), 'Symlink')
    name = path.relative_to(ROOT).as_posix()
    if path.is_file():
        actual.add(name)
    else:
        require(path.is_dir() and name in directories, 'Unexpected directory')
require(actual == set(files) | {'FILES.json', 'FREEZE.json'}, 'Closed roster')
freeze = load(ROOT / 'FREEZE.json')
require(freeze['files_sha256'] == sys.argv[2] and freeze['payloads'] == len(files), 'Freeze')
require(freeze['report_sha256'] == sha(ROOT / 'REPORT.md'), 'Report pin')
require(freeze['verifier_sha256'] == sha(Path(__file__)), 'Verifier pin')
for name, pin in load(ROOT / 'RUNTIME-INPUT-PINS.json')['pins'].items():
    require(sha(ROOT / 'runtime-inputs' / name) == pin, 'Runtime input')
for kind, expected_bad in [('release', 0), ('project', 32)]:
    path = ROOT / 'runtime-inputs' / kind / 'RESULT.json'
    receipt = load(path)
    require(receipt['stable'] is True, 'Source/binary stability')
    require(len(receipt['observations']) == 1, 'One completed observation')
    rows = receipt['observations'][0]['rows']
    require(len(rows) == 32, 'Row count')
    bad = []
    for row in rows:
        require(len(row['stages']) == 5, 'Stage count')
        expected = [[24, 32]] if row['api'] == 'rects' else [24, 32]
        for stage in row['stages']:
            if any(stage[n] != expected for n in ['first', 'second', 'third']):
                bad.append({**{n: row[n] for n in ['columns', 'flex', 'initiallyHidden', 'api']}, 'phase': stage['phase'], **{n: stage[n] for n in ['first', 'second', 'third']}})
    recount = load(ROOT / (kind + '-recount.json'))
    require(recount['source_sha256'] == sha(path) and recount['rows'] == 32 and recount['stages'] == 160, 'Recount provenance')
    require(bad == recount['bad'] and len(bad) == recount['bad_stages'] == expected_bad, 'Exact bad stages')
    require(all(row['flex'] and row['phase'] in ('append', 'append-again') for row in bad), 'Observed failure family')
old = (ROOT / 'HEAD-flex.cpp').read_text()
new = (ROOT / 'candidate-HEAD-flex.cpp').read_text()
marker = "  // CachedFlexItemData is stored in item's writing mode, so we pass\n  // aChildReflowInput into ReflowOutput's constructor.\n  ReflowOutput childReflowOutput(aChildReflowInput);"
insertion = '  if (aItem.Frame()->IsHiddenByContentVisibilityOfInFlowParentForLayout()) {\n    aItem.Frame()->AddStateBits(NS_FRAME_IS_DIRTY);\n  }\n\n'
require(old.count(marker) == 1 and new == old.replace(marker, insertion + marker), 'Only provisional source delta')
patch = ''.join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True), fromfile='a/layout/generic/nsFlexContainerFrame.cpp', tofile='b/layout/generic/nsFlexContainerFrame.cpp'))
require(patch == (ROOT / 'candidate-provisional.patch').read_text(), 'Exact patch')
for name, pins in load(ROOT / 'SOURCE-ROLES.json')['files'].items():
    require(sha(ROOT / 'source-HEAD' / name) == pins['HEAD_sha256'], 'Frozen HEAD source')
print(json.dumps({'status': 'PASS_SOURCE_HYPOTHESIS_CHECKPOINT', 'payloads': len(files), 'release_bad_stages': 0, 'project_bad_stages': 32, 'candidate_runtime_tested': False, 'native_accepted': False}, sort_keys=True))
