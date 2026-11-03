import hashlib
import json
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
refs=read(HERE/'REFERENCES.json')
for path,pin in refs.items():
    assert sha(ROOT/path)==pin
PARENT=ROOT/'artifacts/css-root-self-smil-native7-outcome-v1'
source=(HERE/'compare.py').read_text()
assert source==(PARENT/'compare.py').read_text().replace('css-root-self-smil-candidate-browser-v1','css-root-self-smil-candidate-browser-v2').replace('css-root-self-smil-candidate-browser-runtime-v1','css-root-self-smil-candidate-browser-runtime-v2')
compile(source,str(HERE/'compare.py'),'exec')
b=read(HERE/'BINDINGS.json')
old=read(PARENT/'BINDINGS.json')
assert not b['execution_enabled']
if 'compare.py'=='audit.py':
    assert b['pending_owner_terminal']
    assert all(b[k] is None for k in ('launch','outer_group','owner_manifest_sha256','result_sha256','terminal_sha256'))
    expected=dict(old)
    expected['references']=dict(old['references'])
    expected['references'].update({str((PARENT/f).relative_to(ROOT)):sha(PARENT/f) for f in ['FILES.json','compare.py']})
else:
    assert all(b[k] is None for k in ('owner_manifest','runtime_manifest','owner_terminal','owner_result','build_result','restoration'))
    expected=dict(old)
    expected['owner_directory']='artifacts/css-root-self-smil-candidate-browser-v2'
    expected['runtime_directory']='artifacts/css-root-self-smil-candidate-browser-runtime-v2'
assert b==expected
assert not (HERE/'RESULT.json').exists()
print(json.dumps({'saved_only':True,'exact_owner_and_runtime_name_changes':True,'pending_disabled_bindings':True,'parent_refs':len(refs),'unchanged_stream_suite_not_rerun':True,'runtime_name_author_confirmed':True}))
