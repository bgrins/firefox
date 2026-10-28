import ast, hashlib, json, os, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
I=ROOT/'artifacts/css-round-scalar-capacity-library-integration-v1'; P=ROOT/'artifacts/css-round-scalar-capacity-library-integration-proposal-v1'; L=ROOT/'artifacts/css-spec-lean'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def auth(p,h):
 assert sha(p/'FILES.json')==h
 for n,d in read(p/'FILES.json').items(): assert sha(p/n)==d,n
 return len(read(p/'FILES.json'))
count=auth(I,'a4b7f3d72742e5adc9fb1ff0a76790e19b8ee06fe20ff4e708a06ac5677619e3')
for n,h in read(I/'REFERENCES.json').items(): auth((ROOT/n).parent,h)
e=read(P/'EXPECTED.json');b=read(I/'BEFORE.json'); r=read(I/'verification/report.json');old=read(I/'prior-verification/report.json')
assert b==read(P/'BEFORE.json')
assert read(I/'ROOT-EXECUTION.json')=={'session':32137,'exit':0,'observed_tool_completion':True}
assert read(I/'EXECUTION.json')['exit']==0 and r['status']=='pass'
assert read(I/'APPLIED.json')['postimage_sha256']==e['postimage_sha256']
for n,h in e['preimage_sha256'].items(): assert sha(I/'originals'/n)==h
working={}
for directory,dirs,files in os.walk(L):
 dirs[:]=[x for x in dirs if x not in ('.git','.lake')]
 for name in files:
  p=Path(directory)/name;working[str(p.relative_to(L))]=sha(p)
assert working==dict(b['working_sha256'],**e['postimage_sha256'])
for n,h in r['source_sha256'].items(): assert sha(L/n)==h,n
assert sha(L/'.lake/verification/report.json')==sha(I/'verification/report.json')
for n,c in r['commands'].items():
 assert sha(I/'verification'/(n+'.log'))==c['log_sha256']
 assert c['returncode']==(1 if n.startswith('negative-') else 0)
 if n.startswith('negative-'):
  log=(I/'verification'/(n+'.log')).read_text();assert 'error: Type mismatch' in log and 'but is expected to have type' in log
for n in ['axioms.log','executable-examples.log']:
 assert (I/'verification'/n).read_bytes().startswith((I/'prior-verification'/n).read_bytes())
a={}
audit_text=(I/'verification/axioms.log').read_text()
audit_lines=re.sub(r',\s*\n\s*', ', ', audit_text).splitlines()
for line in audit_lines:
 m=re.fullmatch(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[(.*)\])",line);assert m,line
 name,axioms=m.groups();assert name not in a
 a[name]=[] if axioms is None else axioms.split(', ')
 assert set(a[name])<= {'propext','Quot.sound','Classical.choice'}
assert {n:sorted(v) for n,v in a.items()}==r['declaration_axioms']
assert list(a)[len(old['declaration_axioms']):]==e['new_audit_names']
cases=[]
for line in (I/'verification/executable-examples.log').read_text().splitlines():
 m=re.fullmatch(r'PASS (.*): (true|false)',line);assert m,line
 cases.append({'name':m[1],'result':m[2]=='true'})
assert cases==r['executable_cases']
assert cases[:len(old['executable_cases'])]==old['executable_cases']
assert [[c['name'],c['result']] for c in cases[len(old['executable_cases']):]]==e['new_cases']
tree=ast.parse((L/'check.py').read_text()); assignments={}
for node in tree.body:
 if isinstance(node,ast.Assign):
  for t in node.targets:
   if isinstance(t,ast.Name) and t.id in ('EXPECTED_DECLARATIONS','EXECUTABLE_CASES'):assignments[t.id]=ast.literal_eval(node.value)
assert len(a)==11720 and len(cases)==12304 and len(r['source_sha256'])==2133
assert sum(not c['result'] for c in cases)==127
# Read-only Git calls disable optional locks and fsmonitor.
def gitstate(path):
 def g(*args):return subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false','-C',str(path),*args],env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
 ix=Path(g('rev-parse','--path-format=absolute','--git-path','index').decode().strip())
 return {'head':g('rev-parse','HEAD').decode().strip(),'index_path':str(ix),'index_sha256':sha(ix),'index_entries_sha256':hashlib.sha256(g('ls-files','--stage','-z')).hexdigest(),'staged_diff_sha256':hashlib.sha256(g('diff','--cached','--binary')).hexdigest(),'staged_paths':g('diff','--cached','--name-only').decode().splitlines()}
for name,path in [('parent',ROOT),('nested',L)]:assert gitstate(path)==b[name],name
result={'status':'CANONICAL_INTEGRATION_RESULTS_GO','integration_payloads_authenticated':count,'actual_full_check_session':32137,'actual_full_check_exit':0,'audits':len(a),'cases':len(cases),'source_hashes':len(r['source_sha256']),'expected_false_controls':127,'old_audit_prefix':len(old['declaration_axioms']),'old_case_prefix':len(old['executable_cases']),'new_audits_registered_once':21,'new_cases':20,'old_working_files':len(b['working_sha256']),'old_unchanged_files':len(b['working_sha256'])-8,'exact_postimages':14,'current_working_files':len(working),'nested_staged_paths':len(b['nested']['staged_paths']),'parent_staged_paths':len(b['parent']['staged_paths']),'both_indexes_preserved':True,'live_canonical_report_and_sources_verified':True,'compiler_rerun':False,'new_research_theorem_credit':0}
(OUT/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
