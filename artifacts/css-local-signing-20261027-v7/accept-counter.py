import hashlib, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
RUN=ROOT/'artifacts/css-counter-scope-append-comparison-execution-v1'
read=lambda p:json.loads(p.read_text())
def ref(p): return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
publication=read(HERE/'RESEARCH-PUBLICATION.json');assert publication['preservation_verified'] and publication['index_empty']
execution=read(HERE/'PUBLICATION-EXECUTION.json');assert execution['exit']==0
review=ROOT/'artifacts/css-counter-scope-append-phase-review-v2/terminal/CHECK.json'
r=read(review);assert r['status']=='COUNTER_OCOC_ARCHIVE_AND_PROCESS_REVIEW_PASS' and not r['outer_exit_observed']
spec=importlib.util.spec_from_file_location('policy',RUN/'policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
config=read(RUN/'ACTUAL-CONFIG.json');historical=read(ROOT/'artifacts/css-counter-scope-append-probe-runtime-v1/wpt-observation/RUN.json')
captures={};counts=[]
for phase in config['phases']:
 run=read(RUN/('wpt-'+phase)/'RUN.json');assert run['complete'] and not run['infrastructure_faults']
 captures[phase]=policy.check(run,config,phase,captures,historical)
 rows=[x for x in run['rows'] if x['test']==policy.COUNTER]
 counts.append([sum(x['status']==status for x in rows) for status in ['PASS','FAIL']])
 if phase!='original-initial':
  build=read(RUN/(phase+'-build')/'build-RESULT.json')
  assert build['exit']==0 and build['stop_reason'] is None and build['error'] is None and not build['cleanup_errors'] and build['owned_group_absent']
assert counts==[[12,12],[24,0],[12,12],[24,0]]
a=read(ROOT/'artifacts/css-counter-scope-append-packaging-v1/DRAFT-ACCEPTANCE.json')
a.update(status='READY_FOR_STANDALONE_SIGNED_COMMIT',phase_counts=counts,observed_repairs=12,unchanged_controls=12,existing_regressions={'counter_end_only_PASS':8,'quote_subtests_PASS':64,'exact_all_phases':True},process_completion_evidence={'driver_outer_exit_observed':False,'driver_result_success':True,'driver_pid_absent':True,'fresh_full_verification':ref(HERE/'PUBLICATION-EXECUTION.json')},final_variant='candidate',terminal_review=ref(review))
for p in [review, RUN/'RESULT.json',RUN/'FINAL.json',HERE/'RESEARCH-PUBLICATION.json',HERE/'PUBLICATION-EXECUTION.json']:
 a['references'][str(p.relative_to(ROOT))]=ref(p)['sha256']
for name,digest in a['references'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
out=ROOT/'artifacts/css-counter-scope-append-acceptance-v1';out.mkdir()
save(out/'ACCEPTANCE.json',a)
(out/'REPORT.md').write_text('Counter append invalidation is ready for a standalone local commit. Both original builds reproduce the same 12 failures; both candidate builds pass all24 cases. Quote64 and existing counter8 regressions remain passing. All three builds and exact-fixture WPT lint succeeded. The two Gecko files and WPT are the complete native patch.\n\nThe original tool session was lost, so its outer exit code is unknown. Independently checked child exits, complete phase records, a successful final driver result, absent driver PID, and fresh full live preservation verification supply the completion evidence. No outer exit code is invented.\n\nDiscovery came from source inspection and browser reproduction. The separate Lean model supports conditional delivery laws; native scope construction, lifecycle, delivery and machine arithmetic remain premises. No clean-upstream build, security or performance claim is made.\n')
save(out/'FILES.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()})
print('Accepted counter136 for exact3path signed commit;12 repairs,12 controls,72 regressions')
