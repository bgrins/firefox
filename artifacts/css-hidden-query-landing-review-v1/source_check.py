import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent/'css-hidden-query-landing-runtime-v1'
LANDING = HERE.parent/'css-hidden-query-landing-drafts-v1'
def need(ok, message):
    if not ok:
        raise RuntimeError(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    return json.loads(path.read_bytes())

def apply(text, old):
    lines = text.splitlines(keepends=True)
    source = old.splitlines(keepends=True)
    out, cursor, i = [], 0, 0
    while i < len(lines):
        match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', lines[i])
        need(match is not None, 'unexpected hunk')
        start = int(match[1]) - (int(match[1]) > 0)
        need(start >= cursor, 'overlapping hunk')
        out.extend(source[cursor:start]); cursor = start; i += 1
        old_count, new_count = 0, 0
        while i < len(lines) and not lines[i].startswith('@@'):
            line = lines[i]; need(line[:1] in [' ', '+', '-'], 'unsupported patch line')
            if line[0] in ' -':
                need(cursor < len(source) and source[cursor] == line[1:], 'exact hunk mismatch')
                cursor += 1; old_count += 1
            if line[0] in ' +':
                out.append(line[1:]); new_count += 1
            i += 1
        need(old_count == int(match[2] if match[2] is not None else 1)
             and new_count == int(match[4] if match[4] is not None else 1), 'hunk counts')
    out.extend(source[cursor:])
    return ''.join(out)

need(sha(RUNTIME/'INPUTS.json') == 'e582fdf18c401b30289fbaf26bf461c2f421808020718f263d83d176e55809fb', 'INPUTS')
inputs = load(RUNTIME/'INPUTS.json')
for name, pin in inputs['payload_pins'].items():
    need(sha(RUNTIME/name) == pin, 'input '+name)
need(sha(LANDING/'FILES.json') == 'd07313be9f6bf371cac7579a0ec7a43d8e57184d0f63da1ecf50949d63d2bcbc', 'landing seal')
manifest = load(LANDING/'FILES.json')
manifest = manifest.get('files', manifest)
for name, pin in manifest.items():
    need(sha(LANDING/name) == pin, 'landing payload')
config = load(RUNTIME/'CONFIG.json')
patches = [(LANDING/'column-gecko-wpt.patch', 'layout/base/PresShell.cpp', 'selected/pres-shell-column.cpp'),
           (LANDING/'block-gecko-wpt.patch', 'layout/generic/nsBlockFrame.cpp', 'selected/block-skipped-line.cpp'),
           (HERE.parent/'css-hidden-grid-landing-proposal-v1/standalone-gecko-wpt.patch',
            'layout/generic/nsGridContainerFrame.cpp', 'selected/grid-candidate.cpp')]
results = []
for patch, native, candidate in patches:
    sections = re.split(r'(?m)^--- ', patch.read_text())[1:]
    targets = []
    for section in sections:
        before, after, hunks = section.split('\n', 2)
        need(after.startswith('+++ b/'), 'target header')
        target = after.removeprefix('+++ b/')
        if target == native:
            need(before == 'a/'+native, 'native source header')
            old = (RUNTIME/config['baseline_sources'][native]).read_text()
            expected = (RUNTIME/candidate).read_text()
        else:
            need(before == '/dev/null' and target in config['install'], 'unexpected patch target')
            old = ''
            expected = (RUNTIME/config['install'][target]).read_text()
        need(apply(hunks, old) == expected, 'patch output differs from phase input')
        targets.append(target)
    results.append({'patch': str(patch), 'sha256': sha(patch), 'exact_targets': targets})
original = HERE.parent/'css-hidden-query-boundaries-runtime-v2/tests'
auto = 'hidden-column-auto-scroll.html'
need((LANDING/auto).read_bytes() == (original/auto).read_bytes(), 'auto transfer')
def cases(text):
    return json.loads(re.search(r'const cases = (\[.*?\]);\nconst content', text, re.S)[1])
block = cases((LANDING/'hidden-skipped-block-line-queries.html').read_text())
need(block == [r for r in cases((original/'hidden-skipped-block-line-queries.html').read_text())
               if r['kind'] not in ['float', 'oof']] and len(block) == 14, 'block object transfer')
transfer = load(RUNTIME/'CASE-TRANSFER.json')
need(len(transfer) == 79 and len({(r['landing_test'], r['subtest']) for r in transfer}) == 79, '79case transfer')
need(sum(not r['landing_test'].endswith('/hidden-grid-own-content-queries.html') for r in transfer) == 71, '71 non-grid cases')
result = {'status': 'PASS_SOURCE_TRANSFER', 'inputs': len(inputs['payload_pins']), 'patches': results,
          'block14_objects_exact': True, 'auto4_bytes_exact': True, 'mapped_prior_case_ids': 71,
          'cleaned_landing_files_require_actual_run': True, 'native_landing_acceptance': False}
(HERE/'SOURCE-CHECK.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
