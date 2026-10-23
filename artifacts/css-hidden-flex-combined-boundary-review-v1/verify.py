import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
import argparse
import collections
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--runtime', type=Path, required=True)
a = p.parse_args()
here = Path(__file__).resolve().parent
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
require = lambda ok, message: None if ok else sys.exit(message)
require(h(a.runtime/'FILES.json') == '86e59d39179a46b36f0b3c935b03cbd3b106dd1546d96286ea8ef0b0f31f4d07', 'Runtime manifest pin mismatch')
manifest = read(a.runtime/'FILES.json')
actual = set()
for path in a.runtime.rglob('*'):
    require(not path.is_symlink(), 'Unexpected runtime symlink')
    if path.is_dir():
        continue
    require(path.is_file(), 'Unexpected runtime file type')
    actual.add(path.relative_to(a.runtime).as_posix())
require(actual == set(manifest)|{'FILES.json','FREEZE.json'}, 'Runtime closed roster mismatch')
for path,sha in manifest.items():
    require(h(a.runtime/path) == sha, 'Runtime payload mismatch: '+path)
inputs = read(here/'INPUTS.json')
require(h(a.runtime/'DRAFT-FILES.json') == inputs['combined_draft_sha256'], 'Draft pin mismatch')
draft = read(a.runtime/'DRAFT-FILES.json')
for path,sha in draft.items():
    require(h(a.runtime/path) == sha, 'Draft payload changed: '+path)
config = read(a.runtime/'CONFIG.json')
roles = {
    'baseline': ('a4ebad4b40076d3aea3ef9d48f9d84357d93ad3784c29b93bb6e9dbb9603ae98', 'a2fcecf806b786267b181131c7f204eb40575c75eb4313caa0d794e5efee0824'),
    'principal-only': ('83c646378ba60da82d6501bb94089532992a9ecf1bdc20258c7ea28ee48ff3f5', 'a2fcecf806b786267b181131c7f204eb40575c75eb4313caa0d794e5efee0824'),
    'oof-only': ('a4ebad4b40076d3aea3ef9d48f9d84357d93ad3784c29b93bb6e9dbb9603ae98', '926858026128b2934df41c6ec3953b76fb84d2ed66796523b553fc8dcf2373c7'),
    'both': ('83c646378ba60da82d6501bb94089532992a9ecf1bdc20258c7ea28ee48ff3f5', '926858026128b2934df41c6ec3953b76fb84d2ed66796523b553fc8dcf2373c7'),
}
maps = {}
for phase, source_roles in roles.items():
    auth = read(here/(phase.upper()+'-AUTH.json'))
    path = a.runtime/phase
    require(h(path/'RUN.json') == auth['RUN_sha256'] and h(path/'raw.json') == auth['raw_sha256'], 'Runtime pin mismatch')
    run = read(path/'RUN.json')
    raw = [json.loads(line) for line in (path/'raw.json').read_text().splitlines()]
    require(run['complete'] and run['before'] == run['after'], 'Incomplete or unstable runtime')
    require(run['rows'] == [e for e in raw if e['action']=='test_status'], 'Raw row mismatch')
    require(run['ends'] == [e for e in raw if e['action']=='test_end'], 'Raw end mismatch')
    require(len(run['rows']) == 686 and len(run['ends']) == 22 and sum(e['action']=='suite_end' for e in raw)==1, 'Incomplete event roster')
    for test,names in config['expected_subtests'].items():
        require([r['subtest'] for r in run['rows'] if r['test']==test] == names, 'Ordered roster mismatch')
    for file,sha in zip(['layout/generic/nsFlexContainerFrame.cpp','layout/generic/AbsoluteContainingBlock.cpp'], source_roles):
        require(run['before'][file] == sha, 'Wrong selected source role')
    for name,sha in inputs['fixture_sha256'].items():
        require(h(a.runtime/'tests'/name) == sha == run['before']['testing/web-platform/tests/css/css-contain/content-visibility/'+name], 'Wrong boundary fixture')
    classified = read(here/(phase.upper()+'.json'))
    require(classified['run_sha256'] == h(path/'RUN.json'), 'Wrong classification source')
    index = {(r['test'],r['subtest']):r for r in run['rows']}
    for row in classified['rows']:
        actual = index[row['test'],row['name']]
        require(row['status'] == actual['status'] and row['message'] == (actual.get('message') or ''), 'Classification outcome mismatch')
    maps[phase] = index
matrix = read(here/'FOUR-PHASE-MATRIX.json')
for row in matrix['rows']:
    require(row['statuses'] == {phase:rows[row['test'],row['name']]['status'] for phase,rows in maps.items()}, 'Matrix mismatch')
patterns = collections.Counter(tuple(maps[p][key]['status'] for p in roles) for key in maps['baseline'])
require(patterns == {('PASS','PASS','PASS','PASS'):645,('FAIL','PASS','FAIL','PASS'):34,('FAIL','FAIL','PASS','PASS'):7}, 'Unexpected phase differences')
rejected = read(here/'COMBINED-TIMING-REJECTED.json')
require(h(a.runtime/'timing-both/RESULT.json') == rejected['receipt_sha256'], 'Rejected timing changed')
require(bool(read(a.runtime/'timing-both/RESULT.json')['cleanupErrors']), 'Missing retained cleanup failure')
state = read(a.runtime/'STATE.json')
require(state['status']=='terminal' and state['restored'] and state['restore_build_exit']==0 and not state['recovery_errors'], 'Incomplete restoration')
require(state['traces']=={} and state['failure']['message']=='timing browser termination/reap incomplete', 'Abort history mismatch')
require(read(a.runtime/'BEFORE.json') == read(a.runtime/'FINAL.json') == read(a.runtime/'INPUTS.json')['before'], 'Historical state not restored')
print('PASS: 400 sealed runtime inputs, four raw WPT phases, exact source roles, 28 boundary assertions, phase matrix, rejected combined timing and historical restoration')
