import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
import ast
import hashlib
import json
from pathlib import Path
D=Path(__file__).resolve().parent
R=D.parents[1]
P=R/'artifacts/css-cssom-scroll-client-proposal-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
assert read(D/'CONFIG.json')['ready_for_execution'] is False
for n,h in read(D/'REFERENCES.json').items():assert sha(R/n)==h,n
for n in ['probe.html','validate.py']:assert (D/n).read_bytes()==(P/n).read_bytes()
for n in ['run.py','validate.py','check.py']:compile((D/n).read_text(),n,'exec')
s=(P/'check.py').read_text().split("script = (HERE / 'probe.html')",1)[0]
scope={'__file__':str(D/'check.py'),'__name__':'synthetic_validator_replay'}
exec(compile(s,'proposal-synthetic-validation','exec'),scope)
assert scope['summary']['calibrated']==8 and scope['summary']['phase_calibrated']==32
assert scope['prediction']['first_scroll_matches']==6 and scope['prediction']['first_client_matches']==8
html=(D/'probe.html').read_text()
assert all(n not in html for n in ['offsetWidth','offsetHeight','offsetLeft','offsetTop'])
assert 'offsetParent === host' in html
run=(D/'run.py').read_text();tree=ast.parse(run)
ready=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assert) and "ready_for_execution" in ast.unparse(n.test))
capture=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Try))
assert ready<capture
assert "summary['calibrated'] == summary['repeat_stable'] == summary['restored_stable'] == 8" in run
assert "summary['phase_calibrated'] == 32" in run
assert "summary['first_scroll_matches'] == 6" not in run
result={'status':'PASS_INERT_DRAFT','fixture_validator_byte_identical':True,'syntax_files':3,'synthetic_rows':8,'synthetic_phases':32,'retains_predicted_errors_without_forcing_them':True,'bad_calibration_and_roster_checks_pass':True,'numeric_offsets_absent_from_fixture':True,'offset_parent_is_identity_only':True,'epoch_bound':bool(read(D/'CONFIG.json')['epoch']),'browser_native_build_index_actions':False}
(D/'STATIC-CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
