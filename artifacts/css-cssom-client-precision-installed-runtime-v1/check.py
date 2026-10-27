import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
import ast
import copy
import hashlib
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    return json.loads(p.read_text())
settings = read(HERE / 'CONFIG.json')
assert settings['ready_for_execution'] is False
assert all(settings[n] is None for n in ['epoch', 'epoch_manifest_sha256', 'root_receipt_sha256'])
for n,h in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT/n) == h,n
proposal = ROOT / 'artifacts/css-cssom-client-precision-proposal-v1'
old = ROOT / 'artifacts/css-cssom-client-precision-browser-v1'
for n in ['probe.html','validate.py']:
    assert (HERE/n).read_bytes() == (old/n).read_bytes() == (proposal/n).read_bytes()
for n in ['run.py','validate.py','check.py']:
    compile((HERE/n).read_text(),n,'exec')
text = (HERE/'run.py').read_text()
marker = "try:\n    result = extras.capture("
old_text = (old/'run.py').read_text()
assert text[text.index(marker):] == old_text[old_text.index(marker):]
function = next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='installed_epoch')
epoch = ROOT / 'artifacts/css-cssom-offset-scroll-install-runtime-v1'
assert sha(epoch/'FILES.json') == settings['required_installation_manifest_sha256']
for n,h in read(epoch/'FILES.json').items():
    assert sha(epoch/n)==h,n
scope=dict(read=read,sha=sha)
exec(compile(ast.Module(body=[function],type_ignores=[]),'<epoch gate>','exec'),scope)
expected,pins,config,installation = scope['installed_epoch'](epoch)
assert len(expected['sources'])==47 and len(pins)==318 and len(config['modified_native_paths'])==25
maps={n:read(epoch/n) for n in ['FINAL.json','STATE.json','ROOT-FINAL-CHECK.json','BEFORE.json','INSTALLATION.json','CONFIG.json','FINAL-PINS.json','RESOURCES.json']}
mutations=[('STATE.json','installed',False),('STATE.json','restored',True),('STATE.json','build_exit',1),('STATE.json','lint_exit',1),('STATE.json','recovery_errors',['error']),('ROOT-FINAL-CHECK.json','status','RESTORED_VERIFIED'),('ROOT-FINAL-CHECK.json','existing_stage_paths',924),('ROOT-FINAL-CHECK.json','other_native_sources_preserved',False),('ROOT-FINAL-CHECK.json','pin_count',317),('INSTALLATION.json','owned_test_sha256','0'*64),('CONFIG.json','modified_native_paths',config['modified_native_paths'])]
for file,key,value in mutations:
    bad=copy.deepcopy(maps)
    bad[file][key]=value
    scope['read']=lambda p:copy.deepcopy(bad[p.name])
    try:
        scope['installed_epoch'](epoch)
    except (AssertionError,KeyError):
        pass
    else:
        raise AssertionError((file,key))
# Reuse only the pure prefix; it executes no browser/compiler or receipt write.
s=(proposal/'check.py').read_text().split("script = (HERE / 'probe.html')",1)[0]
synthetic={'__file__':str(HERE/'check.py'),'__name__':'synthetic_validator_replay'}
exec(compile(s,'proposal-pure-validation','exec'),synthetic)
consolidated=copy.deepcopy(synthetic['old'])
for row,exact in zip(consolidated['rows'],synthetic['payload']['rows']):
    for phase in synthetic['namespace']['PHASES']:
        row[phase]['scrollSize']=exact[phase]['scrollSize'][:]
modeled=synthetic['validate'](consolidated)
assert modeled['first_scroll_matches']==8 and modeled['first_client_matches']==6
assert "summary['first_scroll_matches'] ==" not in text and "summary['first_client_matches'] ==" not in text
result={'disabled_epoch_unset':True,'installed_manifest_authenticated':settings['required_installation_manifest_sha256'],
 'installed_epoch_gate_passes':True,'epoch_negative_checks':len(mutations),'source_guards':47,'resource_binary_pins':318,'native_inventory':25,
 'fixture_validator_byte_identical':True,'capture_validation_cleanup_tail_byte_identical':True,'synthetic_rows':8,'synthetic_phases':32,
 'synthetic_fixed_scroll_matches':8,'synthetic_remaining_client_matches':6,'runtime_outcomes_unconstrained':True,
 'browser_native_build_index_actions':False}
(HERE/'STATIC-CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result))
