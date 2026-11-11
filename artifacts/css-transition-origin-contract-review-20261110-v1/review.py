import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'artifacts/css-transition-origin-contract-20261110-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def run(command,cwd,env=None):
 return subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True,timeout=180)
manifest=load(SOURCE/'SOURCE-ONLY.json')
assert all(sha(SOURCE/n)==h for n,h in manifest.items())
provenance=load(SOURCE/'PROVENANCE.json')
for row in provenance['copied_evidence']:
 assert sha(ROOT/row['source'])==sha(SOURCE/row['copy'])==row['sha256']
native=load(SOURCE/'inputs/native-excerpts.json')
for row in native:
 result=subprocess.run(['git','-c','core.fsmonitor=false','show',row['revision']+':'+row['path']],cwd=ROOT,capture_output=True,check=True,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
 assert hashlib.sha256(result.stdout).hexdigest()==row['source_sha256']
 assert result.stdout.decode()[row['character_start']:row['character_end']]==row['text']
 assert hashlib.sha256(row['text'].encode()).hexdigest()==row['text_sha256']
lean=ROOT/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
assert sha(lean)==provenance['lean_sha256']
with tempfile.TemporaryDirectory(prefix='transition-origin-independent-') as temporary:
 scratch=Path(temporary)
 for n,h in manifest.items():
  f=scratch/n;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/n,f)
 assert all(sha(scratch/n)==h for n,h in manifest.items())
 # The manifest authenticates inputs, including checker and documentation.
 shutil.copyfile(SOURCE/'SOURCE-ONLY.json',scratch/'SOURCE-ONLY.json')
 result=run([sys.executable,'-B',str(scratch/'check.py'),'--lean',str(lean),'--out',str(HERE/'cold-replay-final')],scratch)
 (HERE/'cold-replay-final.stdout').write_text(result.stdout);(HERE/'cold-replay-final.stderr').write_text(result.stderr)
 assert result.returncode==0,(result.stdout,result.stderr)
 check=load(HERE/'cold-replay-final/REPORT.json')
 assert check['theorem_audits']==30 and check['executable_rows']==13 and check['compiling_semantic_mutants']==3
 env=dict(os.environ,LEAN_PATH=str(scratch))
 for name in ['Model','Fixtures']:
  result=run([str(lean),'-o',name+'.olean',name+'.lean'],scratch,env)
  assert result.returncode==0,(result.stdout,result.stderr)
 # Mutant witnesses must be false on the baseline, not merely true on mutants.
 controls=[]
 for mutant in load(HERE/'cold-replay-final/MUTANTS.json'):
  witness=scratch/'BaselineWitness.lean';witness.write_text(mutant['witness_source'])
  result=run([str(lean),str(witness)],scratch,env)
  (HERE/(mutant['name']+'-baseline.stdout')).write_text(result.stdout)
  (HERE/(mutant['name']+'-baseline.stderr')).write_text(result.stderr)
  assert result.returncode==1 and 'Tactic `decide` proved that the proposition' in result.stdout and '\nis false\n' in result.stdout,(mutant['name'],result.stdout,result.stderr)
  assert 'unknown identifier' not in result.stdout and 'unexpected token' not in result.stdout
  controls.append(mutant['name'])
assert all(sha(SOURCE/n)==h for n,h in manifest.items())
(HERE/'REVIEW.json').write_text(json.dumps({'status':'PASS','source_manifest_sha256':sha(SOURCE/'SOURCE-ONLY.json'),'source_inputs':len(manifest),'native_excerpts_authenticated':len(native),'native_file_count':len(set(x['path'] for x in native)),'cold_theorem_audits':30,'symbolic_rows':13,'compiled_mutants_rejected':3,'baseline_false_witnesses':controls,'owned_compiled_scratch_removed':not scratch.exists(),'native_refinement':False,'spec_policy_proved':False},indent=2)+'\n')
