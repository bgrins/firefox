import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, shutil, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, data):
    (HERE/name).write_text(json.dumps(data,indent=2)+'\n')
def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def git(*args):
    return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],cwd=ROOT)
def reference(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':sha(path)}
assert not (HERE/'DRAFT-FILES.json').exists() and not (HERE/'STATE.json').exists()
proposal=ROOT/'artifacts/css-svg-length-hidden-embedder-repair-v1'
fixture=ROOT/'artifacts/css-svg-hidden-embedding-regression-v1'
epoch=ROOT/'artifacts/css-svg-length-hidden-provider-fallback-runtime-v1'
for directory in (proposal,fixture,epoch):
    for n,h in read(directory/'FILES.json').items():assert sha(directory/n)==h,n
c=read(ROOT/'artifacts/css-svg-length-readiness-comparison-runtime-v1/CONFIG.json')
gates=read(fixture/'GATES.json')
previous=read(epoch/'FINAL.json');receipt=read(epoch/'ROOT-FINAL-CHECK.json')
installed=receipt['installed_tests']
native=['dom/base/Document.cpp','dom/base/FlushType.h','dom/svg/DOMSVGLength.cpp','dom/svg/SVGLength.cpp','dom/svg/SVGLength.h']
owned='testing/web-platform/tests/svg/types/scripted/SVGLength-hidden-embedding-viewport.html'
test_id='/svg/types/scripted/SVGLength-hidden-embedding-viewport.html'
shutil.copyfile(fixture/'SVGLength-hidden-embedding-viewport.html',HERE/'fixture.html')
c.update(ready_for_execution=False,epoch=str(epoch.relative_to(ROOT)),epoch_manifest_sha256=sha(epoch/'FILES.json'),epoch_receipt=receipt,
    proposal=str(proposal.relative_to(ROOT)),fixture_proposal=str(fixture.relative_to(ROOT)),head=previous['snapshot']['head'],
    candidate_sources={n:str((proposal/'candidate'/n).relative_to(ROOT)) for n in native},
    candidate_pins={n:sha(proposal/'candidate'/n) for n in native},
    sources=sorted(set(c['modified_native_paths'])|set(native)),
    guard_sources=sorted(set(previous['snapshot']['sources'])|set(native)),
    install={owned:'fixture.html'},tests=['testing/web-platform/tests'+n for n in gates['expected_subtests']],
    expected_subtests=gates['expected_subtests'],main_tests=[test_id],landing_tests=[test_id],
    proposal_test_files={owned:'SVGLength-hidden-embedding-viewport.html'},main_expected_count=24,files_expected_count=6,
    landing_failure_prefix='assert_equals: first viewport-dependent value expected ',
    required_hidden_witnesses=[[test_id,n] for n in gates['expected_subtests'][test_id] if n.endswith('hidden-only')],
    pending_acceptance_gates=['Normalized hidden-only baseline witness and all24 landing cases passing','Existing28 controls preserved or improved with exact failure diagnostics','All original sources/index/eight installed tests restored and restoration build succeeds','Independent source/runtime review and installed overlay integration before acceptance'],
    required_seals={'proposal':reference(proposal/'FILES.json'),'fixture':reference(fixture/'FILES.json'),'source_review':None,'runner_review':None})
c['baseline_tests']=c['tests'];c['baseline_expected_subtests']=c['expected_subtests']
c.pop('baseline_allowed_failures',None)
c['source_pins']={n:sha(ROOT/n) for n in c['guard_sources']}
c['head_pins']={n:hashlib.sha256(git('show',c['head']+':'+n)).hexdigest() for n in c['guard_sources']}
assert all(c['source_pins'][n]==h for n,h in previous['snapshot']['sources'].items())
control_records=read(fixture/'CONTROL-PINS.json')
assert all(v['head']==c['head'] for v in control_records.values()), 'control HEAD roles'
controls={n:v['sha256'] for n,v in control_records.items()}
for n,h in controls.items():assert sha(ROOT/n)==h and hashlib.sha256(git('show',c['head']+':'+n)).hexdigest()==h,n
save('TEST-SOURCE-PINS.json',controls)
c['existing_tests']=sorted(set(installed)|set(controls))
c['existing_test_pins']={n:sha(ROOT/n) for n in c['existing_tests']}
c['tracked_existing_tests']=git('ls-files','--',*c['existing_tests']).decode().splitlines()
c['resource_guard_paths']=sorted(previous['pins'])
save('CONFIG.json',c)
wpt=load('wpt',ROOT/c['helpers']/'run_wpt.py');wpt.HERE=HERE;wpt.CONFIG=c
resources={n:h for n,h in previous['pins'].items() if n not in c['guard_sources'] and n not in wpt.BINARIES}
for n in wpt.resource_paths(c['tests'],virtual=True):
    if n in c['guard_sources'] or n in wpt.BINARIES:continue
    h=sha(ROOT/n) if (ROOT/n).is_file() else None
    assert n not in resources or resources[n]==h,n
    resources[n]=h
save('RESOURCES.json',resources)
refs=read(epoch/'REFERENCES.json')
extra=[epoch/'FILES.json',epoch/'ROOT-FINAL-CHECK.json',proposal/'FILES.json',fixture/'FILES.json',
 ROOT/'artifacts/css-svg-length-hidden-provider-fallback-browser-v1/epoch_gate.py',
 ROOT/'artifacts/css-svg-length-readiness-comparison-runtime-v1/run.py',
 ROOT/'artifacts/css-svg-length-readiness-comparison-runtime-v1/tests.py',
 ROOT/'artifacts/css-svg-length-hidden-provider-fallback-results-review-v1/FILES.json']
for path in extra:refs[str(path.relative_to(ROOT))]=sha(path)
save('REFERENCES.json',refs)
assert len(c['sources'])==33 and len(c['guard_sources'])==56 and len(c['candidate_sources'])==5
assert sum(map(len,c['expected_subtests'].values()))==52 and len(c['tests'])==6
print(json.dumps({'disabled':True,'sources':33,'guards':56,'candidate_sources':5,'owned_tests':1,'subtests':52,'resources':len(resources),'existing_tests':len(c['existing_tests'])}))
