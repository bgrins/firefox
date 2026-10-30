import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LEAN=ROOT/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(LEAN)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
assert len(sys.argv)==2 and Path(sys.argv[1]).name==sys.argv[1]
out=HERE/sys.argv[1];out.mkdir()
prior=ROOT/'artifacts/css-contextual-duration-queue-state-model-v1'
for package, expected in [(prior,'19de0845a6637692756eaa9bc523d5ffc917c10a214d6ed557c47d5e693efd40'),(ROOT/'artifacts/css-contextual-duration-dispatch-attempt-model-v1','d7a58a9ac71b269e44724bcdc9fe454d67ef0a2c6aa8b265e73e444f91b34f3e')]:
 assert sha(package/'FILES.json')==expected
 for name, info in json.loads((package/'FILES.json').read_bytes()).items():assert sha(package/name)==(info if isinstance(info,str) else info['sha256'])
completion=ROOT/'artifacts/css-contextual-duration-first-read-completion-model-v1'
assert sha(completion/'FILES.json')=='7f359d3fb32ddfcfacab2d3055e294979d133a06a31a927c233b000269e9d1ee'
for name, info in json.loads((completion/'FILES.json').read_bytes()).items():assert sha(completion/name)==info['sha256']
assert sha(prior/'QueueState.lean')=='b49bdbac6a3ae1abfc9569e2c5405defbfcaf203125e78b2ba90212ccea5f291'
names=re.findall(r'^theorem (\w+)',(HERE/'Oracle.lean').read_text(),re.M)
false_cases={
 'WrongOddEndpoint':'metric 1 true = 32',
 'MissingLeafEdge':'leaf 1 true = opacity (metric 1 true)',
 'WrongEvenOpacity':'opacity (metric 8 true) = 1',
 'TwoRoundsDepthEight':'leaf 9 ((Completion.run 9 2 (Completion.initial 9 .absent)).value 9) = opacity (metric 8 true)',
}
records=[]
(out/'TOOLCHAIN.txt').write_bytes(subprocess.check_output([str(LEAN),'--version']))
with tempfile.TemporaryDirectory(prefix='css-finite-depth-oracle-') as temporary:
 scratch=Path(temporary);env=dict(os.environ,LEAN_PATH=str(scratch))
 (out/'SCRATCH.json').write_text(json.dumps({'path':temporary})+'\n')
 for source in [ROOT/'artifacts/css-contextual-duration-dispatch-attempt-model-v1/DispatchAttempt.lean',prior/'QueueState.lean',completion/'Completion.lean',HERE/'Oracle.lean']:
  shutil.copyfile(source,scratch/source.name);shutil.copyfile(source,out/source.name)
 (scratch/'Audit.lean').write_text('import Oracle\n'+''.join('#print axioms Oracle.'+n+'\n' for n in names))
 for name,claim in false_cases.items():(scratch/(name+'.lean')).write_text('import Oracle\nopen Oracle\nexample : '+claim+' := by decide\n')
 for source in scratch.glob('*.lean'):shutil.copyfile(source,out/source.name)
 for name,expected in [('DispatchAttempt',True),('QueueState',True),('Completion',True),('Oracle',True),('Audit',True)]+[(n,False) for n in false_cases]:
  result=subprocess.run([str(LEAN),'-o',name+'.olean',name+'.lean'],cwd=scratch,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
  (out/(name+'.log')).write_bytes(result.stdout);records.append({'module':name,'exit':result.returncode,'expected_success':expected})
  (out/'COMMANDS.json').write_text(json.dumps(records,indent=2)+'\n')
  assert (result.returncode==0)==expected,(name,result.stdout.decode())
  if not expected:assert b'Tactic `decide` proved that the proposition' in result.stdout and b'is false' in result.stdout
 audit=(out/'Audit.log').read_text()
 assert audit.count('depends on axioms:')+audit.count('does not depend on any axioms')==len(names)
 assert 'sorryAx' not in audit and 'Lean.ofReduceBool' not in audit
 axioms={n.strip() for group in re.findall(r'axioms: \[(.*?)\]',audit) for n in group.split(',') if n.strip()}
 assert axioms<={'propext','Quot.sound','Classical.choice'}
assert not scratch.exists()
(out/'CHECK.json').write_text(json.dumps({'audited_theorems':names,'false_controls_rejected':len(false_cases),'source_sha256':sha(HERE/'Oracle.lean'),'scratch_removed':True,'native_refinement':False,'canonical_coverage_increment':0},indent=2)+'\n')
print(len(names),'audits;',len(false_cases),'false controls rejected')
