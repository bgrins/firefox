import ast
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('helper',HERE/'run.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
exp=helper.read(HERE/'EXPERIMENT.json');pins=helper.read(HERE/'SOURCE-PINS.json');current=helper.read(HERE/'SUBSET-MANIFEST.json')
def item(manifest,kind,name):
    value=manifest['items'][kind]
    for part in name.lstrip('/').split('/'):value=value[part]
    return value
seen=set()
for package,digest in exp['packages'].items():
    directory=ROOT/package;helper.authenticate(directory,digest)
    policy=helper.read(directory/'POLICY.json');source=ROOT/policy['capture_package'] if 'capture_package' in policy else directory
    old=helper.read(source/'SUBSET-MANIFEST.json')
    for name,kind in policy['tests'].items():
        assert item(old,kind,name)==item(current,kind,name),name
        seen.add(name)
    for name,value in helper.read(source/'SOURCE-PINS.json').items():assert pins[name]==value,name
assert seen==set(exp['tests'])
for name,item in pins.items():
    path=ROOT/item['origin']
    if item['exists']:
        assert path.is_file() and helper.sha(path)==item['sha256'],name
        assert helper.sha(HERE/item['capture'])==item['sha256'],name
    else:assert not path.exists(),name
for path in HERE.glob('*.py'):ast.parse(path.read_text())
result={'same_parent_test_manifest_entries':len(seen),'source_pin_records':len(pins),'present_captures':sum(i['exists'] for i in pins.values()),'python_syntax':True,'browser_executed':False}
(HERE/'INPUT-CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
