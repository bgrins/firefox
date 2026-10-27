import hashlib, json, stat, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'artifacts/css-cubic-bezier-calc-range-comparison-v1'
output=ROOT/'artifacts/css-cubic-bezier-calc-range-browser-runtime-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert len(sys.argv)==4
assert sha(source/'DRAFT-FILES.json')==sys.argv[1]
peer=ROOT/sys.argv[2];assert sha(peer/'FILES.json')==sys.argv[3]
for directory,manifest in [(source,'DRAFT-FILES.json'),(peer,'FILES.json')]:
 for name,pin in json.loads((directory/manifest).read_text()).items():
  path=Path(name);assert not path.is_absolute() and '..' not in path.parts
  assert stat.S_ISREG((directory/path).lstat().st_mode)
  assert sha(directory/path)==(pin['sha256'] if isinstance(pin,dict) else pin),name
assert not output.exists();output.mkdir()
manifest=json.loads((source/'DRAFT-FILES.json').read_text())
for name in manifest:
 path=output/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((source/name).read_bytes())
(output/'SOURCE-DRAFT-FILES.json').write_bytes((source/'DRAFT-FILES.json').read_bytes())
inputs=json.loads((source/'INPUTS.json').read_text())
inputs['local_pins']={name:(pin['sha256'] if isinstance(pin,dict) else pin) for name,pin in manifest.items() if name != 'INPUTS.json'}
assert inputs['local_pins'] and {'compare.py','build.py','tests.py','policy.py','process_control.py'} <= set(inputs['local_pins'])
review={'status':'CUBIC_BEZIER_CALC_RANGE_COMPARISON_ROOT_REVIEW_GO','local_pins':inputs['local_pins'],'controller_manifest_sha256':sys.argv[1],'peer_manifest':{'path':str((peer/'FILES.json').relative_to(ROOT)),'sha256':sys.argv[3]},'proposal_manifest_sha256':'094e5a064ef3de4dc7e307dc413f839e7abeff2abf064bb0b38306c557a03447','source_review_manifest_sha256':'61478f8df5fdc4310722acb1395532ddf3a6ee28c421562d4e2cb24f40b1ff2b','root_read_full_controller':True,'quarter_parameter_formula_independently_checked':True,'fresh_baseline_required':True,'accepted_fix':False}
(output/'ROOT-REVIEW.json').write_text(json.dumps(review,indent=2)+'\n')
inputs['ready']=True;inputs['root_review']={'path':str((output/'ROOT-REVIEW.json').relative_to(ROOT)),'sha256':sha(output/'ROOT-REVIEW.json')}
(output/'INPUTS.json').write_text(json.dumps(inputs,indent=2)+'\n')
for n,pin in inputs['local_pins'].items():assert sha(output/n)==pin,n
print('Activated exact reviewed comparison payload',output,flush=True)
