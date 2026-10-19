import pathlib,json,hashlib,subprocess,tempfile,shutil
R=pathlib.Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((R/'FREEZE.json').read_text());assert H(R/'INPUTS.json')==f['inputs_sha256']
for n,h in json.loads((R/'INPUTS.json').read_text()).items():assert H(R/n)==h,n
ids=json.loads((R/'IDENTITIES.json').read_text());paths=list(ids['files'])
for path,pins in ids['files'].items():
 assert H(R/'candidate'/path)==pins['candidate']
 if pins['original']:assert H(R/'original'/path)==pins['original']
 else:assert not (R/'original'/path).exists()
source,checksum,test=paths
old=(R/'original'/source).read_text();new=(R/'candidate'/source).read_text()
def predicate(s):
 a=s.index('fn is_ident_start(');b=s.index('\nfn consume_ident_like',a);return s[a:b]
assert predicate(old)==predicate((R/'accepted-capsule/original-tokenizer.rs').read_text())
assert predicate(new)==predicate((R/'accepted-capsule/candidate-tokenizer.rs').read_text())
assert new==old.replace(predicate(old),predicate(old).replace('has_newline_at(1)','has_newline_at(2)',1),1)
a=json.loads((R/'original'/checksum).read_text());b=json.loads((R/'candidate'/checksum).read_text())
assert a['files']['src/tokenizer.rs']==H(R/'original'/source)
a['files']['src/tokenizer.rs']=H(R/'candidate'/source);assert a==b
assert H(R/'candidate'/test)=='74983ece77efdaa5aa41ac58d9381ccd16fb232a123588da1dc5f96513765fc4'
assert H(R/'fix-upstream-v1.patch')==ids['patch_sha256']
logs=[]
with tempfile.TemporaryDirectory(prefix='escaped-newline-upstream-') as d:
 d=pathlib.Path(d);shutil.copytree(R/'original',d,dirs_exist_ok=True)
 for reverse in [False,True]:
  args=['patch','--batch','--fuzz=0','-p1','-d',str(d),'-i',str(R/'fix-upstream-v1.patch')]
  if reverse:args.append('-R')
  c=subprocess.run(args,capture_output=True,text=True);logs.append({'reverse':reverse,'exit':c.returncode,'stdout':c.stdout,'stderr':c.stderr})
  assert c.returncode==0 and 'offset' not in c.stdout and 'fuzz' not in c.stdout,logs[-1]
  for path in paths:
   expected=R/('original' if reverse else 'candidate')/path
   if expected.exists():assert (d/path).read_bytes()==expected.read_bytes(),path
   else:assert not (d/path).exists(),path
with tempfile.TemporaryDirectory(prefix='escaped-newline-stack-mismatch-') as d:
 shutil.copytree(R/'original',d,dirs_exist_ok=True)
 c=subprocess.run(['patch','--batch','--fuzz=0','-p1','-d',d,'-i',str(R/'accepted-stack-native.patch')],capture_output=True,text=True)
 assert c.returncode!=0 and 'failed' in c.stdout.lower(),c.stdout
 logs.append({'expected_stack_patch_rejection':True,'exit':c.returncode,'stdout':c.stdout,'stderr':c.stderr})
print(json.dumps({'status':'PASS','files':paths,'upstream':ids['upstream'],'exact_apply_reverse':True,'predicate_source_transfer':True,'earlier_native_dependency':'NONE_FOR_THIS_REPAIR','isolated_base_build_browser':'NOT_RUN','logs':logs},indent=2))
