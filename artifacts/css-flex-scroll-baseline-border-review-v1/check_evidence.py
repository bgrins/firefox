#!/usr/bin/env python3
import collections,hashlib,json,pathlib,shutil,subprocess,tempfile
P=pathlib.Path(__file__).resolve().parent
N=P/'inputs/native'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def events(role):return [json.loads(s) for s in (N/role/'raw.json').read_text().splitlines()]
def rows(role):return {x['subtest']:x for x in events(role) if x['action']=='test_status'}
a,b=rows('baseline-wpt-v1'),rows('candidate-wpt-v1')
assert len(a)==len(b)==384 and a.keys()==b.keys()
fixed=[k for k in a if a[k]['status']=='FAIL' and b[k]['status']=='PASS']
same=[k for k in a if (a[k]['status'],a[k].get('message'))==(b[k]['status'],b[k].get('message'))]
assert len(fixed)==72 and len(same)==312 and all(v['status']=='PASS' for v in b.values())
assert all('exports the same text baseline' in a[k]['message'] for k in fixed)
for role in ['baseline-wpt-v1','candidate-wpt-v1']:
 r=json.loads((N/role/'RUN.json').read_text());assert r['complete'] and r['stable_pins'] and r['before']==r['after']
 assert [x['status'] for x in events(role) if x['action']=='test_end']==['OK']
runs=[json.loads((N/role/'RUN.json').read_text()) for role in ['baseline-wpt-v1','candidate-wpt-v1']]
pin_changes={k:[runs[0]['before'][k],runs[1]['before'][k]] for k in runs[0]['before'] if runs[0]['before'][k]!=runs[1]['before'][k]}
assert set(pin_changes)=={'layout/generic/ScrollContainerFrame.cpp','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'}
e=events('regressions-v1');sub=[x for x in e if x['action']=='test_status'];end=[x for x in e if x['action']=='test_end']
assert len(sub)==675 and all(x['status']=='PASS' for x in sub)
assert len(end)==38 and collections.Counter(x['status'] for x in end)=={'PASS':24,'OK':14}
r=json.loads((N/'regressions-v1/RUN.json').read_text());assert r['complete'] and r['stable_pins']
patch=N/'fix-candidate-v1.patch';assert sha(patch)=='f23e2c05119aad4303f332659d387a75ba259a8a4ec7c3284b0f4e70c365f5c5'
pack=[]
for base in ['92a6fddf18e5828b17d7491a34663a0d5a9c12ad','976279105b2e78b8666a959eb3f25c9176cefaf8']:
 path='layout/generic/ScrollContainerFrame.cpp';wpt='testing/web-platform/tests/css/css-align/scroll-container-baseline-borders.html'
 before=subprocess.check_output(['git','show',base+':'+path],cwd=P)
 assert before==(N/'before.cpp').read_bytes()
 absent=subprocess.run(['git','cat-file','-e',base+':'+wpt],cwd=P,capture_output=True);assert absent.returncode!=0
 with tempfile.TemporaryDirectory(prefix='patch-replay-',dir=P) as t:
  t=pathlib.Path(t);f=t/path;f.parent.mkdir(parents=True);f.write_bytes(before)
  for reverse in [False,True]:
   cmd=['git','apply','--unsafe-paths']+(['-R'] if reverse else [])+[str(patch)]
   x=subprocess.run(cmd,cwd=t,capture_output=True,text=True);assert x.returncode==0,x.stderr
   if not reverse:
    assert f.read_bytes()==(N/'candidate.cpp').read_bytes()==(N/('standalone-'+base[:12]+'.cpp')).read_bytes()
    assert sha(t/wpt)=='c975b9a711e71758caa9164ec6234260f059b3a6683aaf592ac9e123df2ea2dd'
   else:assert f.read_bytes()==before and not (t/wpt).exists()
 pack.append({'base':base,'apply_reverse':True,'candidate_identical':True})
(P/'EVIDENCE-RESULTS.json').write_text(json.dumps({'paired':{'rows':384,'fixed':len(fixed),'unchanged':len(same),'all_failures_after_calibration':True},'pin_changes':pin_changes,'regressions':{'files':len(end),'PASS_subtests':len(sub),'ends':dict(collections.Counter(x['status'] for x in end))},'packaging':pack},indent=2)+'\n')
print((P/'EVIDENCE-RESULTS.json').read_text())
