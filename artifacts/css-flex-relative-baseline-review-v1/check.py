import argparse
from collections import Counter
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
if sys.flags.optimize:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
CPP='layout/generic/nsFlexContainerFrame.cpp'
PINS={
 'natural':('85d6c3a15d2f3f12fd4664669f4b2cb956d4cf94aa45f4b1ab6f543a28be9e60','07513403c70015a983d6b590881e44071843b2a37eba05b4a10c7141a008ce58',19),
 'relative':('11ded3db7013c651482a2e3ae5120c001c816673324d5b72df1027f359abe37e','5f596d6365f40612e8eac52ea217ec2ed470b71f0caee03d67ba2b60b1a8778f',96)}
def sha(data):return hashlib.sha256(data).hexdigest()
def data(role,name):return (ROOT/'inputs'/role/name).read_bytes()
def js(role,name):return json.loads(data(role,name))
def tokens(data):
    text=data.decode()
    return re.findall(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_][A-Za-z_0-9]*|[0-9]+|[^\s]',text)

def authenticate():
 for role,(mh,fh,count) in PINS.items():
  root=ROOT/'inputs'/role
  assert sha(data(role,'FILES.json'))==mh and sha(data(role,'FREEZE.json'))==fh
  rows=js(role,'FILES.json')['files'];assert len(rows)==count
  assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() or p.is_symlink()}=={x['path'] for x in rows}|{'FILES.json','FREEZE.json'}
  assert not any(p.is_symlink() for p in root.rglob('*'))
  for x in rows:assert sha(data(role,x['path']))==x['sha256'] and len(data(role,x['path']))==x['bytes']
 root=ROOT/'inputs/previous-natural'
 assert sha(data('previous-natural','FILES.json'))=='fe66685b2dd06ceff1a3d1e3c8ab5e8dc23e9c38a607c2591d013e2f422e718b'
 expected={'candidate.cpp','fix-candidate-v1.patch','REPORT.md','FILES.json','FREEZE.json','baseline-wpt-v1/RUN.json','baseline-wpt-v1/raw.json'}
 assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}==expected
 roster={x['path']:x for x in js('previous-natural','FILES.json')['files']}
 for name in expected-{'FILES.json','FREEZE.json'}:assert sha(data('previous-natural',name))==roster[name]['sha256']
 assert sha(data('previous-natural','FREEZE.json'))=='3e203eed811dcbab2e0f3eb588fca9d52e8e8c5b3029c166ea5be9b1c4981298'

def authenticate_providers():
 for row in json.loads((ROOT/'PROVIDER-PINS.json').read_text()):
  retained=(ROOT/row['retained']).read_bytes();indexed=(ROOT/row['indexed']).read_bytes()
  assert sha(retained)==row['sha256'] and sha(indexed)==row['indexedSha256']
  assert (retained==indexed)==row['indexedIdentical']
 assert sha((ROOT/'retained-nsIFrameInlines.h').read_bytes())=='1c8903d04354e4f093f08830fe8a629d88cd34286390496e62e074ad077be2df'
 assert sha((ROOT/'retained-nsIFrame.h').read_bytes())=='75c701ea858955468d5c5dc8ebbde16be17845a5fcc454279502156b50efb5d2'

def rows(role,path):return [json.loads(l) for l in data(role,path).decode().splitlines() if l.strip()]
def statusmap(events):return {(e['test'],e['subtest']):(e['status'],e.get('message')) for e in events if e.get('action')=='test_status'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 authenticate()
 authenticate_providers()
 assert data('natural','candidate.cpp')==data('relative','candidate.cpp')
 assert data('relative','before.cpp')==data('previous-natural','candidate.cpp')
 for role in ['natural','relative']:
  build=js(role,'BUILD.json');assert build['exit']==0 and build['source_stable'] and build['source_sha256']==sha(data(role,'candidate.cpp'))
 assert js('natural','BUILD.json')==js('relative','BUILD.json')
 paired={}
 for phase in ['baseline','candidate']:
  run=js('relative',phase+'-wpt-v1/RUN.json');raw=rows('relative',phase+'-wpt-v1/raw.json')
  assert run['complete'] and run['stable_pins'] and run['before']==run['after'] and run['exit']==(1 if phase=='baseline' else 0)
  role='before.cpp' if phase=='baseline' else 'candidate.cpp'
  assert run['before'][CPP]==sha(data('relative',role))
  for path,pin in run['before'].items():
   p=ROOT/'inputs/relative'/(phase+'-wpt-v1/inputs')/path
   if pin is None:assert not p.exists()
   elif not path.startswith('objdir-'):assert sha(p.read_bytes())==pin
  statuses=[e for e in raw if e.get('action')=='test_status'];ends=[e for e in raw if e.get('action')=='test_end']
  assert statuses==run['rows'] and ends==run['harness'] and len(ends)==1 and ends[0]['status']=='OK'
  mapping=statusmap(raw);assert len(mapping)==288
  paired[phase]=(run,mapping)
 base,b=paired['baseline'];final,c=paired['candidate'];assert b.keys()==c.keys()
 assert Counter(v[0] for v in b.values())=={'FAIL':192,'PASS':96}
 assert all(v[0]=='PASS' for v in c.values()) and sum(b[k]==c[k] for k in b)==96
 assert all(v[0]!='FAIL' or 'Relative item offset does not move its container' in v[1] for v in b.values())
 expectedchanges={CPP,'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'}
 assert {k for k in base['before'] if base['before'][k]!=final['before'][k]}==expectedchanges
 for path,pin in js('relative','BUILD.json')['binaries'].items():assert final['before'][path]==pin
 run=js('relative','regressions-v1/RUN.json');assert run['complete'] and run['exit']==0 and run['stable_pins'] and run['before']==run['after']
 raw=rows('relative','regressions-v1/raw.json');tests=[e for e in raw if e.get('action')=='test_end'];subs=[e for e in raw if e.get('action')=='test_status']
 assert tests==run['tests'] and subs==run['subtests']
 assert len(tests)==29 and Counter(e['status'] for e in tests)=={'PASS':23,'OK':6}
 assert len(subs)==309 and all(e['status']=='PASS' for e in subs)
 assert run['before'][CPP]==sha(data('relative','candidate.cpp'))
 for path,pin in js('relative','BUILD.json')['binaries'].items():assert run['before'][path]==pin
 assert data('natural','regressions/RUN.json')==data('relative','regressions-v1/RUN.json')
 assert data('natural','regressions/raw.json')==data('relative','regressions-v1/raw.json')
 previous=js('previous-natural','baseline-wpt-v1/RUN.json');donor_base=statusmap(rows('previous-natural','baseline-wpt-v1/raw.json'))
 donor_final={k:v for k,v in statusmap(raw).items() if k[0]=='/css/css-flexbox/flexbox-natural-baseline-donor.html'}
 assert donor_base.keys()==donor_final.keys() and len(donor_final)==48
 assert sum(v[0]=='FAIL' for v in donor_base.values())==16 and all(v[0]=='PASS' for v in donor_final.values())
 assert sum(donor_base[k]==donor_final[k] for k in donor_base)==32
 final_donor=js('natural','FINAL-WPT.json')
 assert sha(data('previous-natural','baseline-wpt-v1/RUN.json'))==final_donor['baseline_run_sha256']
 assert sha(data('natural','regressions/RUN.json'))==final_donor['final_regression_run_sha256']
 patches={role:ROOT/'inputs'/role/name for role,name in [('natural','fix-candidate-v2.patch'),('relative','fix-candidate-v1.patch')]}
 packages={role:js(role,'PACKAGING.json') for role in patches}
 for role in patches:assert sha(patches[role].read_bytes())==packages[role]['patch_sha256']
 commute=[]
 for record in packages['relative']['checks']:
  baseid=record['base'];original=subprocess.check_output(['git','-c','core.fsmonitor=false','show',baseid+':'+CPP],cwd=a.repo)
  assert sha(original)==record['before_sha256']
  outputs=[]
  with tempfile.TemporaryDirectory(prefix='baseline-independent-patches-') as temp:
   def fresh(name):
    work=Path(temp)/name;source=work/CPP;source.parent.mkdir(parents=True);source.write_bytes(original);return work
   def apply(work,patch,reverse=False):
    proc=subprocess.run(['git','-c','core.fsmonitor=false','apply',*(['--reverse'] if reverse else []),str(patch)],cwd=work,capture_output=True,text=True)
    assert proc.returncode==0,proc.stdout+proc.stderr
   for role in ['natural','relative']:
    work=fresh(role);apply(work,patches[role]);actual=(work/CPP).read_bytes()
    entry=next(x for x in packages[role]['checks'] if x['base']==baseid)
    assert sha(actual)==entry['after_sha256'] and actual==data(role,'standalone-'+baseid[:12]+'.cpp')
    assert {str(p.relative_to(work)) for p in work.rglob('*') if p.is_file()}==set(entry['paths'])
    for name in entry['paths']:
     if name!=CPP:assert sha((work/name).read_bytes())==packages[role]['wpt_sha256']
    if role=='natural':
     old=fresh('previous');apply(old,ROOT/'inputs/previous-natural/fix-candidate-v1.patch')
     marker='item.Frame()->GetLogicalPosition(wm, aContainerSize)'
     oldbytes=(old/CPP).read_bytes();assert oldbytes.count(marker.encode())==1
     assert oldbytes.replace(marker.encode(),marker.replace('GetLogicalPosition','GetLogicalNormalPosition').encode())==actual
    else:
     assert tokens(actual.replace(b'GetLogicalNormalPosition',b'GetLogicalPosition'))==tokens(original)
    apply(work,patches[role],True);assert (work/CPP).read_bytes()==original
   for i,order in enumerate([['natural','relative'],['relative','natural']]):
    work=fresh('order'+str(i))
    for role in order:apply(work,patches[role])
    outputs.append({str(p.relative_to(work)):sha(p.read_bytes()) for p in work.rglob('*') if p.is_file()})
    for role in reversed(order):apply(work,patches[role],True)
    assert {str(p.relative_to(work)) for p in work.rglob('*') if p.is_file()}=={CPP} and (work/CPP).read_bytes()==original
   assert outputs[0]==outputs[1]
   claimed=next(x for x in js('relative','COMMUTATION.json')['checks'] if x['base']==baseid)
   assert outputs[0]==claimed['combined_files']
   work=fresh('shared');(work/CPP).write_bytes(data('relative','before.cpp'));apply(work,ROOT/'inputs/relative/shared-native-delta.patch');assert (work/CPP).read_bytes()==data('relative','candidate.cpp')
   commute.append({'base':baseid,'bothIndependent':True,'bothOrdersIdentical':True,'exactReversal':True,'outputs':outputs[0]})
 result={'authenticClosedPackages':{'natural':19,'relative':96},'previousEvidenceSubsetAuthenticated':True,'naturalDelta':'one new-helper query only','relativeDelta':'two existing fallback queries only','sharedDelta':'three query replacements','relativePaired':{'cases':288,'failToPass':192,'unchanged':96},'naturalFinal':{'cases':48,'v1FailuresNowPassing':16,'unchanged':32,'causality':'v1 isolated donor experiment retained; v2 shared runtime includes relative repair'},'regression':{'files':29,'reftestsPASS':23,'subtestsPASS':309,'harnessOK':6},'commutation':commute,'upstreamStandaloneBrowserBuild':False}
 (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
