import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
PLAN=HERE.parent/'css-grid-baseline-grid-bundle-validation-plan-20261112-v1'
RUN=HERE.parent/'css-grid-baseline-grid-bundle-validation-native-20261112-v1'
OUTCOMES=HERE.parent/'css-grid-baseline-grid-bundle-outcome-review-20261112-v1'
def read(p): return json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,value):
 with (HERE/name).open('x') as f: json.dump(value,f,indent=2);f.write('\n')
assert sha(PLAN/'FILES.json')=='45e16af90418fd31582a27c84cdd3c6b766cf10322c3a2c2727679a8d1ea942d'
for name,pin in read(PLAN/'FILES.json')['files'].items(): assert sha(PLAN/name)==pin['sha256'],name
result=read(RUN/'RESULT.json')
assert result==read(RUN/'RESTORATION.json')
assert result['status']=='COMPLETED_AND_RESTORED correctness gate only'
assert result['source_restored'] and result['build_restored'] and result['fresh_groups_absent']
assert result['accepted_repair'] is False
assert not any(k.endswith('error') for k in result)
labels=['baseline-focused','baseline-alignment','candidate-build','candidate-focused','candidate-alignment','restored-build','restored-focused','restored-alignment']
commands=read(RUN/'COMMANDS.json');assert [r['label'] for r in commands]==labels
for row in commands:
 assert row['exit']==0 and row['safe_cleanup'] and row['group_absent'] and not row.get('timeout')
 assert row['cwd']==str(ROOT)
 if row['label'].endswith('build'): assert row['argv']==['/Users/bgrins/venvs/firefox/bin/python','./mach','build','binaries','-j2']
 else:
  assert row['argv'][:6]==['/Users/bgrins/venvs/firefox/bin/python','./mach','wpt','--headless','--no-pause-after-test','--processes=1']
  tests=read(PLAN/'FOCUSED.json') if row['label'].endswith('focused') else ['testing/web-platform/tests/css/css-grid/alignment']
  assert row['argv'][9:]==list(tests)
proc=subprocess.run(['ps','-axo','pid=,pgid=,command='],capture_output=True,text=True,check=True,timeout=10)
rows=[line.strip().split(None,2) for line in proc.stdout.splitlines()]
assert rows and all(len(r)>=2 and r[0].isdigit() and r[1].isdigit() for r in rows)
groups={r['pgid'] for r in commands};assert not any(int(r[1]) in groups for r in rows)
for n,digest in read(PLAN/'LIVE-PINS.json').items(): assert sha(ROOT/n)==digest,n
for n,pin in read(PLAN/'TOOL-PINS.json').items(): assert str(Path(n).resolve())==pin['resolved'] and sha(Path(n))==pin['sha256'],n
originals=[p for p in (PLAN/'original').rglob('*') if p.is_file()];assert len(originals)==3
for p in originals: assert (ROOT/p.relative_to(PLAN/'original')).read_bytes()==p.read_bytes()
for phase in ['baseline','candidate','restored']:
 outcome=read(OUTCOMES/(phase.upper()+'.json'));details=read(OUTCOMES/(phase.upper()+'-FAILURE-DETAILS.json'))
 assert outcome['status']=='EXACT_OUTCOMES_AND_RAW_EVENTS_MATCH'
 assert details['status']=='UNCHANGED_FAILURE_DETAILS' and not details['changes'] and len(details['pngs'])==22
 for suite in ['focused','alignment']:
  label=phase+'-'+suite
  assert read(RUN/(label+'-before-BINARIES.json'))==read(RUN/(label+'-after-BINARIES.json'))
  evidence=outcome['results'][label]
  assert evidence['report_sha256']==sha(RUN/(label+'-wptreport.json')) and evidence['raw_sha256']==sha(RUN/(label+'-raw.log'))
final=read(RUN/'restored-alignment-after-BINARIES.json');assert len(final)==2
assert final==read(RUN/'restored-build-BINARIES.json')
for name,pin in final.items(): assert sha(Path(name))==pin['sha256'] and Path(name).stat().st_size==pin['bytes'],name
save('RUNTIME-AUTHORITY.json',final)
save('REVIEW.json',dict(status='CORRECTNESS_AND_RESTORATION_ACCEPTED',commands=8,focused_subtests_per_phase=700,alignment_files_per_phase=457,alignment_outcomes_per_phase=2947,unchanged_failures=64,unchanged_pngs=22,live_pins=len(read(PLAN/'LIVE-PINS.json')),tool_pins=5,original_sources=3,owned_groups_absent=sorted(groups),accepted_repair=False,performance_claim=False,remaining=['Work cost','Provider checks','Timing','Key adequacy','Padding repair independence']))
save('EXECUTION-FILES.json',{str(p.relative_to(RUN)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(RUN.rglob('*')) if p.is_file()})
print('CORRECTNESS_AND_RESTORATION_ACCEPTED')
