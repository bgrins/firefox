import hashlib,importlib.util,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
source=ROOT/'artifacts/css-local-signing-20261027-v13/CURRENT-EPOCH.json'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='be1e5611e1d3385ba82ca031f03b818e72e4ab8d08b8687a359d06fb05ac8506'
spec=importlib.util.spec_from_file_location('raw_state',ROOT/'artifacts/css-attr-raw-nested-native-runtime-v1/state.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
epoch=json.loads(source.read_text());before=s.a.verify_current(s.h,ROOT,s.ENV,epoch)
assert epoch['semantic_index']['head']=='eb9c04b94cf3007d4f4b4d45ba99cd826829e455'
assert epoch['raw_attribute_transition']['accepted'] and epoch['raw_attribute_transition']['fix']==138
for name in ['INITIAL-EPOCH.json','CURRENT-EPOCH.json']:
 with (HERE/name).open('xb') as f:f.write(source.read_bytes())
with (HERE/'BEFORE.json').open('x') as f:json.dump(before,f,indent=2,sort_keys=True);f.write('\n')
print('Verified signed fix138 baseline; source and binary unchanged',flush=True)
