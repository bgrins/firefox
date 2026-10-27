from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
assert not (HERE/'FILES.json').exists(), 'sealed producer is immutable; replay in an owned copy'
REV='90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def write(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def authenticate(path,digest):
    assert sha(path/'FILES.json')==digest
    for name,value in read(path/'FILES.json').items():assert sha(path/name)==value

baseline=ROOT/'artifacts/css-finite-mod-rem-runtime-v1'
authenticate(baseline,'90dce7991da1c70f56832eb68fe85002926ae08531c569ec48df2fbf1ff03791')
proposal=ROOT/'artifacts/css-finite-mod-rem-repair-v1'
authenticate(proposal,'11cd45831364d8062b71f815b2344c98f60a2c2abf488f6f3f257e8e14ecd936')
completion=read(baseline/'ROOT-COMPLETION.json')
assert completion['status']=='COMPLETE_DIAGNOSTIC_ROOT_ADOPTED' and completion['session']==44048 and completion['actual_exit']==0 and completion['raw_classification_errors']==0
receipt=read(baseline/'ROOT-FINAL-CHECK.json')
assert receipt['status']=='FINITE_MOD_REM_BASELINE_PRESERVATION_PASS' and receipt['capture_error'] is None and receipt['final_pins_sha256']==sha(baseline/'FINAL-PINS.json')
assert not read(baseline/'SUMMARY.json')['errors']
final=read(baseline/'FINAL.json');pins=dict(final['pins'])
assert len(pins)==620 and final['pins']==read(baseline/'FINAL-PINS.json')
assert len(final['snapshot']['sources'])==72 and len(final['installed_tests'])==24
assert read(baseline/'SUMMARY.json')['counts']=={'PASS':8,'FAIL':16}
prior=ROOT/'artifacts/css-name-repeat-context-comparison-runtime-v1'
config=read(prior/'CONFIG.json')
old_names=['round-mod-rem-computed.html','signed-zero.html','calc-infinity-nan-computed.html',
           'calc-relative-length-nonfinite-intermediates.html','round-runtime-nan-priority.html','round-finite-negative-zero.html']
new_names=['round-mod-rem-invalid.html','round-mod-rem-serialize.html','mod-rem-infinite-divisor.html']
base='testing/web-platform/tests/css/css-values/'
roster={}
for name in old_names:
    url='/css/css-values/'+name
    roster[url]=config['expected_subtests'][url]
    assert base+name in pins
objects={}

def historical(name,optional=False):
    result=subprocess.run(['git','show',REV+':'+name],cwd=ROOT,capture_output=True)
    if result.returncode:
        assert optional and result.returncode==128
        digest=None
    else:
        path=HERE/'source'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(result.stdout)
        digest=sha(path)
    objects[name]=dict(revision=REV,exit=result.returncode,sha256=digest)
    assert name not in pins or pins[name]==digest,('historical conflict',name)
    pins[name]=digest
    return result.stdout.decode() if digest else None

parsing=historical('testing/web-platform/tests/css/support/parsing-testcommon.js')
serialization=historical('testing/web-platform/tests/css/support/serialize-testcommon.js')
with tempfile.TemporaryDirectory(prefix='modrem-roster-') as tmp:
    for name in new_names:
        body=historical(base+name)
        scripts=re.findall(r'<script>([\s\S]*?)</script>',body)
        assert len(scripts)==1
        helpers=parsing if name.endswith('invalid.html') else serialization if name.endswith('serialize.html') else ''
        js=Path(tmp)/'roster.js'
        js.write_text('const names=[];global.test=(f,n)=>names.push(n);global.document={querySelector:()=>({})};\n'+helpers+'\n'+scripts[0]+'\nconsole.log(JSON.stringify(names));')
        r=subprocess.run(['node',str(js)],check=True,capture_output=True,text=True)
        names=json.loads(r.stdout);assert len(names)==len(set(names)) and names
        roster['/css/css-values/'+name]=names
        historical('testing/web-platform/meta/css/css-values/'+name+'.ini',optional=True)
landing=base+'mod-rem-exact-finite-remainder.html'
landing_url='/css/css-values/mod-rem-exact-finite-remainder.html'
roster[landing_url]=read(ROOT/'artifacts/css-finite-mod-rem-quotient-audit-v1/ROSTER.json')
assert landing not in pins
pins[landing]=None
pins['testing/web-platform/meta/css/css-values/mod-rem-exact-finite-remainder.html.ini']=None
native='servo/components/style/values/generics/calc.rs'
original=proposal/'installed/original'/native;candidate=proposal/'installed/candidate'/native
assert sha(original)==final['snapshot']['sources'][native]
source_maps={k:dict(final['snapshot']['sources']) for k in ['baseline','candidate','restored']}
source_maps['candidate'][native]=sha(candidate)
assert {k for k in source_maps['baseline'] if source_maps['baseline'][k]!=source_maps['candidate'][k]}=={native}
write('SOURCE-MAPS.json',source_maps)
write('ROSTER.json',dict(tests=['testing/web-platform/tests'+url for url in roster],expected_subtests=roster,reftests=[],expected_total=sum(map(len,roster.values())),files_expected_count=len(roster)))
write('HISTORICAL-OBJECTS.json',objects)
write('RESOURCES.json',pins)
write('ADDITIONAL-ROLES.json',{k:v for k,v in pins.items() if k not in final['pins']})
write('BASELINE-EPOCH.json',dict(runtime=str(baseline.relative_to(ROOT)),manifest_sha256=sha(baseline/'FILES.json'),final_sha256=sha(baseline/'FINAL.json'),final_pins_sha256=sha(baseline/'FINAL-PINS.json'),root_receipt_sha256=sha(baseline/'ROOT-FINAL-CHECK.json'),peer_review={'path':'artifacts/css-finite-mod-rem-terminal-review-v1','manifest_sha256':'505a4022ad9b5a1ff1fb777a95c3ff9041562f14871821d3a92abdcd0f0eb84a'},
    snapshot=final['snapshot'],installed_tests=final['installed_tests'],source_roles=72,prior_roles=620,planned_full_roles=len(pins),actual_runtime_session=44048,actual_runtime_exit=0))
run=read(baseline/'wpt-diagnostic/RUN.json')
assert run['complete'] and not run['infrastructure_faults'] and len(run['rows'])==24
assert run['before']==run['after']==read(baseline/'PRE-CAPTURE.json')['pins']
assert [r['subtest'] for r in run['rows']]==roster[landing_url]
rows=[]
for row in run['rows']:
    moved=dict(row);moved['test']=landing_url;rows.append(moved)
write('OBSERVED-LANDING-BASELINE.json',dict(original_test=run['rows'][0]['test'],comparison_test=landing_url,body_sha256=sha(proposal/'installed/candidate'/landing),rows=rows,identity_transfer='Same byte-identical body and24 names; only destination filename changes. Actual full comparison baseline still required.'))
reference=[r for r in read(prior/'wpt-candidate/RUN.json')['rows'] if r['test'] in roster and r['test']!=landing_url]
assert len(reference)==sum(len(roster['/css/css-values/'+n]) for n in old_names)
write('HISTORICAL-CONTROL-OUTCOMES.json',dict(authoritative_for_next_run=False,source=str(prior.relative_to(ROOT))+'/wpt-candidate/RUN.json',rows=reference))
write('CANDIDATE.json',dict(native_paths={native:dict(original=str(original.relative_to(ROOT)),original_sha256=sha(original),candidate=str(candidate.relative_to(ROOT)),candidate_sha256=sha(candidate))},fixture={landing:dict(source=str((proposal/'installed/candidate'/landing).relative_to(ROOT)),sha256=sha(proposal/'installed/candidate'/landing))},patch=str((proposal/'installed.patch').relative_to(ROOT)),patch_sha256=sha(proposal/'installed.patch'),head90_alternative_execution=False))
write('POLICY.json',dict(ready_for_execution=False,phase_order=['baseline','candidate','restored'],normalization_to_head90=False,full_baseline_outcomes=None,actual_comparison_runtime=None,
    mandatory_candidate_pass={landing_url:roster[landing_url]},require_observed_repair=True,expected_repair_count=16, observed_repair_identities=[dict(test=r['test'],subtest=r['subtest']) for r in rows if r['status']=='FAIL'], require_fresh_landing_baseline_exact_observed=True,
    baseline_calibrations='Exact reviewed24 classifier, fatal admission/input/finite/repeat/zero-history/guard errors; no failure count forced.',
    existing_outcomes='Fresh full700 baseline is authority. All24 landing baseline rows must match the observed24; candidate must pass24 and repair the exact16 observed failures. Any non-target change, including extra FAIL-to-PASS improvement or retained FAIL diagnostic/metadata change, rejects and restores pending separate root review. No executable waiver.',
    restoration='Restore original installed body, rebuild, rerun exact full roster and require original baseline outcome equality including retained failure diagnostics; verify all role/source/index/identity/preservation joins before acceptance.',
    fixture_ownership='Only new landing file is temporarily owned; all installed24 identities and historical tests readonly; old diagnostic absences retained.',
    precision_qualification='Binary32 exact-support investigation with CSS implementation-defined precision limits; no oracle/tolerance weakening.'))
write('CHECK.json',dict(status='DISABLED_COMPARISON_DATA_PREPARED',cases=sum(map(len,roster.values())),files=len(roster),observed_main_pass=8,observed_main_fail=16,full_control_baseline_pending=True,source_guards=72,installed_identities=24,prior_roles=620,planned_roles=len(pins),new_roles=len(pins)-620,temporary_fixture_count=1,live_reads=False))
print(json.dumps(read(HERE/'CHECK.json')))

actual_config=read(baseline/'CONFIG.json')
readonly=[n for n in read(HERE/'ROSTER.json')['tests'] if n!=landing]
old_tracked=set(actual_config['tracked_existing_tests'])
new_tracked={n for n in objects if n.startswith('testing/web-platform/tests/')}
tracked=sorted(n for n in readonly if n in old_tracked|new_tracked)
installed={n:final['installed_tests'][n] for n in readonly if n in final['installed_tests']}
assert set(tracked)|set(installed)==set(readonly) and not set(tracked)&set(installed)
write('OWNERSHIP.json',dict(owned_fixture=landing,readonly_tests=readonly,readonly_pins={n:pins[n] for n in readonly},tracked_readonly=tracked,installed_readonly=installed,full_installed_identities=final['installed_tests'],no_installed_test_replacement=True))
