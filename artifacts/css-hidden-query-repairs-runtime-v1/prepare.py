import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def need(ok, why):
    if not ok:
        raise RuntimeError(why)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--draft-sha', required=True)
parser.add_argument('--expected-head', required=True)
args = parser.parse_args()
need(not (HERE/'INPUTS.json').exists() and not (HERE/'prepared').exists() and not (HERE/'BEFORE.json').exists(), 'already prepared or run')
need(sha(HERE/'DRAFT-FILES.json') == args.draft_sha, 'draft manifest pin')
draft = json.loads((HERE/'DRAFT-FILES.json').read_text())
for n,h in draft.items():
    need(not Path(n).is_absolute() and '..' not in Path(n).parts, 'unsafe draft path')
    need(stat.S_ISREG((HERE/n).lstat().st_mode) and sha(HERE/n) == h, 'draft payload '+n)
spec = importlib.util.spec_from_file_location('compact_wpt',HERE/'run_wpt.py')
wpt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpt)
c = wpt.CONFIG
prior=ROOT/c['prior_runtime']
prior_state=json.loads((prior/'STATE.json').read_text())
need(prior_state.get('status')=='terminal' and prior_state.get('restored') is True and prior_state.get('restore_build_exit')==0 and prior_state.get('recovery_errors')==[], 'prior experiment not successfully restored')
need((prior/'BEFORE.json').read_bytes()==(prior/'FINAL.json').read_bytes(), 'prior restoration snapshot mismatch')
need(len(c['tests'])==7 and sum(map(len,c['expected_subtests'].values()))==66, 'compact roster mismatch')
before = wpt.snapshot()
need(before['head'] == args.expected_head, 'HEAD differs from requested post-commit HEAD')
need(len(wpt.git('diff','--cached','--name-only').splitlines()) == c['expected_staged_paths'] == 0, 'index not empty')
need(len(c['sources']) == 23 and len(set(c['sources'])) == 23 and len(c['guard_sources']) == 28, 'source roster')
need(all(before['sources'][n] is not None for n in c['guard_sources']), 'missing guarded source')
need(all(not (ROOT/n).exists() and not (ROOT/n).is_symlink() for n in c['must_be_absent']), 'current or proposed temporary test still exists')
need(len(c['install'])==2 and len(c['tracked_tests'])==5
     and set(c['install']).isdisjoint(c['tracked_tests'])
     and set(c['tests'])==set(c['install'])|set(c['tracked_tests']), 'test ownership partition')
for path,selected in c['baseline_sources'].items():
    need(wpt.git('show','HEAD:'+path) == (HERE/selected).read_bytes(), 'HEAD body differs from reviewed baseline: '+path)
for path in set(c['guard_sources'])-set(c['sources']):
    need(wpt.git('show','HEAD:'+path)==(ROOT/path).read_bytes(), 'non-written guard differs from HEAD: '+path)
for path,payload in c['tracked_test_payloads'].items():
    need(wpt.git('ls-files','--error-unmatch','--',path).decode().strip()==path, 'landing test not tracked: '+path)
    need(wpt.git('show','HEAD:'+path)==(ROOT/path).read_bytes()==(HERE/payload).read_bytes(), 'tracked landing test differs: '+path)
resources = wpt.resource_paths(c['tests'],virtual=True)
resource_pins = wpt.pins(resources,virtual=True)
need(all(resource_pins[n] is not None for n in c['tests']+c['support_paths']), 'missing test/support')
prepared=HERE/'prepared'
prepared.mkdir()
for path in c['sources']:
    for role,data in [('original',(ROOT/path).read_bytes()),('head',wpt.git('show','HEAD:'+path))]:
        dest=prepared/role/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
need(wpt.snapshot() == before, 'source/HEAD/index changed during preparation')
payloads = dict(draft)
for f in prepared.rglob('*'):
    if f.is_file():
        payloads[str(f.relative_to(HERE))]=sha(f)
inputs={'before':before,'source_pins':before['sources'],'resource_pins':resource_pins,
        'temporary_test_state':{n:None for n in c['install']},'expected_staged_paths':0,
        'draft_sha256':args.draft_sha,'payload_pins':payloads,
        'prior_terminal_pins':{str((prior/name).relative_to(ROOT)):sha(prior/name) for name in ['STATE.json','BEFORE.json','FINAL.json']}}
(HERE/'INPUTS.json').write_text(json.dumps(inputs,indent=2)+'\n')
print(json.dumps({'status':'PREPARED_NOT_RUN','head':before['head'],'INPUTS_sha256':sha(HERE/'INPUTS.json'),
                  'sources_to_restore':23,'source_guards':28,'tests':len(c['tests']),
                  'subtests':sum(map(len,c['expected_subtests'].values()))},indent=2))
