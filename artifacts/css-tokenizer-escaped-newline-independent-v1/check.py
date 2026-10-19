import argparse,hashlib,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--replay-output',type=pathlib.Path);p.add_argument('--lean',type=pathlib.Path);a=p.parse_args()
f=json.loads((R/'FREEZE.json').read_text());assert H(R/'INPUTS.json')==f['inputs_sha256']
m=json.loads((R/'INPUTS.json').read_text())
for n,h in m.items():assert H(R/n)==h,n
assert H(R/'capsule/FREEZE.json')=='6881694a18d5877b096c5daa107e0e091c6ebf450aba234832d3daf856fabb5e'
assert H(R/'capsule/MANIFEST.json')=='f92c56cbf00c8f8e9b6adbc5d9edb7bac6895e2f12c6002eaa82d9349a28e176'
v=json.loads((R/'replay/RESULT.json').read_text());assert v['predicate_theorem_audits']==8 and v['patch_apply_reverse'] and v['vendor_checksum_exact']
assert all(x['exit']==0 for x in json.loads((R/'MUTANT-WITNESSES.json').read_text()))
assert all(x['exit']!=0 and x['rejected_before_Lean'] for x in json.loads((R/'TAMPER.json').read_text()))
if a.replay_output:
 assert a.lean and H(a.lean)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
 subprocess.run(['python3',str(R/'capsule/check.py'),'--lean',str(a.lean.resolve()),'--output',str(a.replay_output.resolve())],check=True)
print(json.dumps({'status':'PASS','authenticated':len(m),'verdict':'APPROVED_NARROW_FORMAL_SOURCE_COMPONENT','native_acceptance':'ROOT_GATES_OPEN','full_name_escape':'OPEN'}))
