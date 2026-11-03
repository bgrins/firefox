import difflib, hashlib, importlib.util, json, shutil, subprocess, tempfile
from pathlib import Path
H=Path(__file__).resolve().parent
R=H.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
refs=json.loads((H/'REFERENCES.json').read_text())
for path,digest in refs.items():assert sha(R/path)==digest,path
roles=json.loads((H/'SOURCE-ROLES.json').read_text())
for f,values in roles.items():
 for value in values.values():assert sha(R/value['path'])==value['sha256']

for role,name in [('attribute','ATTRIBUTE-DELTA.patch'),('size','SIZE-DELTA.patch'),('base','native.patch')]:
 expected=''
 for f,values in roles.items():expected+=''.join(difflib.unified_diff((R/values[role]['path']).read_text().splitlines(True),(R/values['candidate']['path']).read_text().splitlines(True),fromfile='a/'+f,tofile='b/'+f))
 assert (H/name).read_text()==expected
 with tempfile.TemporaryDirectory(prefix='attribute-frontier-check-',dir='/private/tmp') as tmp:
  for f,values in roles.items():
   p=Path(tmp)/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/values[role]['path'],p)
  for reverse in [False,True]:
   cmd=['patch','-p1','--fuzz=0','--batch','-i',str(H/name)]
   if reverse:cmd+=['-R']
   result=subprocess.run(cmd,cwd=tmp,capture_output=True,text=True);assert result.returncode==0,(cmd,result.stdout,result.stderr)
   for f,values in roles.items():assert sha(Path(tmp)/f)==values[role if reverse else 'candidate']['sha256']
 assert not Path(tmp).exists()
for f,values in roles.items():
 common=(R/values['common']['path']).read_text().splitlines(True);changes=[]
 for label in ['attribute','size']:
  value=(R/values[label]['path']).read_text().splitlines(True)
  for op,i,j,k,l in difflib.SequenceMatcher(a=common,b=value,autojunk=False).get_opcodes():
   if op!='equal':changes.append((i,j,value[k:l],label))
 changes.sort(key=lambda e:(e[0],e[1]));pos=0;merged=[];records=[]
 for i,j,lines,label in changes:
  assert i>=pos;merged.extend(common[pos:i]);merged.extend(lines);pos=j;records.append({'base_start':i,'base_end':j,'parent':label,'replacement_sha256':hashlib.sha256(''.join(lines).encode()).hexdigest(),'replacement_lines':len(lines)})
 merged.extend(common[pos:]);assert ''.join(merged)==(R/values['candidate']['path']).read_text();assert records==json.loads((H/'MERGE.json').read_text())['edits'][f]
for copy,path in [('ATTRIBUTE-PARENT.patch','css-resumable-attribute-root-entry-v1'),('SIZE-V1-PARENT.patch','css-resumable-computed-size-selection-v1'),('SIZE-V2-PARENT.patch','css-resumable-computed-size-selection-v2')]:
 assert (H/copy).read_bytes()==(R/'artifacts'/path/'PARENT-DELTA.patch').read_bytes()
assert (H/'ORIGINAL-TARGETS.json').read_bytes()==(R/'artifacts/css-resumable-computed-size-selection-v2/ORIGINAL-TARGETS.json').read_bytes()
original=json.loads((H/'ORIGINAL-TARGETS.json').read_text());assert len(original['cases'])==21 and sum(c['original']=='FAIL' for c in original['cases'])==15
obs=json.loads((R/'artifacts/css-font-input-dependency-browser-probe-v1/observations.json').read_text());assert len(obs['rows'])==48
for row in obs['rows']:assert row['syntaxSupported'] and row['first']==row['reference']==str(row['size'])+'px'
spec=importlib.util.spec_from_file_location('reader',R/'artifacts/css-variable-origin-proof-v2/native/rust_reader.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
texts=[(H/'candidate'/f).read_text() for f in roles]+[(R/'servo/components/style/values/specified/length.rs').read_text()]
def body(text,marker):
 start=text.index(marker);tokens=reader.tokens(text[start:]);i=next(i for i,t in enumerate(tokens) if t[0]=='{');j=reader.pair(tokens,i);return text[start:start+tokens[j][2]]
for file,unit,positive,negative in [('TEST-PROVIDER-SIZE-run2.json','EXTRACTED.rs',36,18),('TEST-GRAPH-run1.json','GRAPH-EXTRACTED.rs',14,7)]:
 d=json.loads((H/file).read_text());assert d['source_sha256']==sha(H/'candidate/servo/components/style/custom_properties.rs');assert d['extracted_sha256']==sha(H/unit)
 for path,digest in d['test_inputs'].items():assert sha(H/path)==digest,path
 for marker,digest in d['parts'].items():
  if marker.startswith('    fn has_references'):candidates=[body(text[text.index('impl References {'):],marker) for text in texts if 'impl References {' in text]
  elif marker in ['    fn from_value(','    fn new(']:candidates=[body(text[text.index("impl<'a> Substitution<'a> {"):],marker) for text in texts if "impl<'a> Substitution<'a> {" in text]
  else:candidates=[body(text,marker) for text in texts if marker in text]
  assert any(hashlib.sha256(v.encode()).hexdigest()==digest for v in candidates),marker
 rec=[r for r in d['records'] if r.get('variant')]
 assert len(rec)==2*(negative+1)
 for i in range(0,len(rec),2):
  compile,run=rec[i:i+2];assert compile['exit']==0
  assert (run['exit']==0)==(run['variant']=='positive')
  if run['variant']=='positive':assert f'{positive} passed; 0 failed' in run['stdout']
  else:assert 'test result: FAILED' in run['stdout']
 assert d['scratch_removed'] and not Path(d['scratch']).exists()
for p in H.glob('TEST-*.json'):
 d=json.loads(p.read_text())
 if 'scratch' in d:assert not Path(d['scratch']).exists(),p
rustfmt='/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustfmt'
r=subprocess.run([rustfmt,'--check','--edition','2024','--config','skip_children=true',*[str(H/'candidate'/f) for f in roles]],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
print(json.dumps({'references':len(refs),'roles':len(roles),'exact_patches':3,'roundtrips':3,'provider_size_tests':36,'provider_size_compiled_controls':18,'graph_tests':14,'graph_compiled_controls':7,'scratch_absent':True,'native_run':False}))
