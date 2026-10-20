import argparse, hashlib, json, os, pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--lean',default='/Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean')
parser.add_argument('--output',required=True)
args=parser.parse_args()
lean=pathlib.Path(args.lean).resolve()
output=pathlib.Path(args.output).resolve()
output.mkdir(parents=True,exist_ok=False)
env=dict(os.environ,LEAN_PATH=str(output))
steps=[]
for name,args in [('protocol',['-o',str(output/'Protocol.olean'),str(root/'prototype/Protocol.lean')]),('clients',['--run',str(root/'prototype/Clients.lean')])]:
 command=[str(lean),*args]
 r=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (output/(name+'.log')).write_text(r.stdout)
 steps.append(dict(name=name,command=command,exit_code=r.returncode))
 if r.returncode: raise SystemExit(r.stdout)
text=(output/'clients.log').read_text()
expected={
 'actual_footprint_sufficient':'[propext]', 'run_bind':'[propext]',
 'sizing_substitution':'[propext]', 'animation_substitution':'[propext]',
 'joint_substitution':'[propext]', 'demo_nonvacuous':None,
 'phase_erasure_changes_result':None, 'epoch_erasure_changes_result':None,
 'unsuccessful_request_remains_dependency':'[propext]',
 'inactive_avoids_size_request':None, 'same_key_same_episode':None,
 'changing_reply_not_one_episode':None, 'inactive_change_is_observable':None}
actual=[line for line in text.splitlines() if line.startswith("'CssProtocol.")]
assert len(actual)==len(expected)
for name,axioms in expected.items():
 ending=' depends on axioms: '+axioms if axioms else ' does not depend on any axioms'
 assert "'CssProtocol."+name+"'"+ending in actual
observations=[line for line in text.splitlines() if not line.startswith("'CssProtocol.")]
assert observations==(root/'prototype/EXPECTED-OBSERVATIONS.txt').read_text().splitlines()
receipt=dict(lean=str(lean),lean_sha256=hashlib.sha256(lean.read_bytes()).hexdigest(),
 version=subprocess.check_output([str(lean),'--version'],text=True).strip(),
 commands=steps,axioms=expected,observations=observations,
 source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'prototype').glob('*.lean')},
 scope='Generic finite read-episode composition; synthetic clients, no CSS/native refinement')
(output/'REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
