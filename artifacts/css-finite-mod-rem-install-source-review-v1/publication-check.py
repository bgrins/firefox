from pathlib import Path
import ast,json,hashlib,tempfile
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'artifacts/css-finite-mod-rem-install-bound-v1'
source=P/'install.py';assert hashlib.sha256(source.read_bytes()).hexdigest()=='62cfb2f5cb6fbbfb28590779ca4430ad167da7467cf51aa1edc1ebdc7094be8c'
tree=ast.parse(source.read_text());flow=next(n for n in tree.body if isinstance(n,ast.Try));code=compile(ast.Module(body=[flow,tree.body[-1]],type_ignores=[]),'<actual finalization>','exec')
def need(v,msg):
 if not v:raise RuntimeError(msg)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();results=[]
for failure in [None,'FINAL.json','FINAL-PINS.json','CLEANUP.json','RESULT.json']:
 with tempfile.TemporaryDirectory(prefix='modrem-review-publication-') as directory:
  tmp=Path(directory);(tmp/'fixture-source').write_bytes(b'fixture');calls=[]
  state=dict(ROOT=tmp,HERE=tmp,owned_plan={'temporary_fixtures':{'fixture':{'source':'fixture-source','sha256':sha(tmp/'fixture-source')}}},restoration={'fixture':None},owned={},bodies={'source':{}},current_binaries={},transitions=[],completed=[],captured=[],mutation_started=False,candidate_ready=False,installed=False,failure=None,recovery_errors=[],final=None,acceptance={'fix':128},sha=sha,need=need)
  def write(n,phase):state['mutation_started']=True;calls.append('write-'+phase)
  def build(label,phase,active=True):calls.append('build-'+label)
  def capture(label,phase):calls.append('capture-'+label);state['completed'].append(phase);state['captured'].append(label)
  def restore():calls.append('restore-source');return []
  def cleanup():calls.append('cleanup');(tmp/'fixture').unlink();return ['fixture'],[]
  def verify(phase,*args,**kwargs):return {'pins':dict.fromkeys(range(628)),'installed_tests':dict.fromkeys(range(25 if phase=='candidate' else 24))}
  def save(name,value):
   with (tmp/name).open('x') as f:f.write(json.dumps(value))
   if name==failure:raise OSError('written complete body then error')
  state.update(write_source=write,build=build,capture=capture,restore_sources=restore,cleanup_fixtures=cleanup,verify=verify,save=save)
  error=None
  try:exec(code,state)
  except RuntimeError as e:error=str(e)
  if failure is None:
   assert error is None and state['installed'] and (tmp/'fixture').exists() and calls==['write-candidate','build-candidate','capture-candidate']
  else:
   assert error and not state['installed'] and not (tmp/'fixture').exists()
   receipt=json.loads((tmp/'RECOVERY-RESULT.json').read_text());assert not receipt['installed'] and receipt['restored'] and not receipt['recovery_errors']
   assert failure in receipt['supersedes_partial_success_records']
   assert calls==['write-candidate','build-candidate','capture-candidate','restore-source','build-restored','capture-restored','cleanup']
   assert (tmp/failure).exists()
   if failure=='RESULT.json':assert json.loads((tmp/failure).read_text())['installed'] is True
  results.append({'failure_after_complete_write':failure,'actual_terminal_rejected':error is not None,'installed':state['installed'],'calls':calls})
print(json.dumps({'status':'FULL_BODY_PUBLICATION_CHECK_PASS','checks':results,'live_actions':False},indent=2))
