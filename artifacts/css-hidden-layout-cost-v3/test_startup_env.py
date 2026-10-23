import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S')
sys.dont_write_bytecode=True
import ast
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
here=Path(__file__).resolve().parent
nodes=ast.parse((here/'run.py').read_text()).body
start=next(i for i,n in enumerate(nodes) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='child_env' for t in n.targets))
end=next(i for i,n in enumerate(nodes[start:],start) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='posts' for t in n.targets))
code=compile(ast.Module(body=nodes[start:end],type_ignores=[]),'child-environment','exec')
results=[]
for present in [False,True]:
    inherited={'UNCHANGED':'control','MOZ_DISABLE_SAFE_MODE_KEY':'old'}
    if present: inherited['MOZ_SAFE_MODE_RESTART']='dummy-private-value'
    before=dict(inherited)
    with tempfile.TemporaryDirectory(prefix='startup-env-check-') as tmp:
        output=Path(tmp)
        env={'os':SimpleNamespace(environ=inherited),'output':output,'json':json}
        exec(code,env)
        expected={'UNCHANGED':'control','MOZ_DISABLE_SAFE_MODE_KEY':'1'}
        assert env['child_env']==expected and inherited==before
        raw=(output/'STARTUP-ENV.json').read_text(); receipt=json.loads(raw)
        assert receipt['MOZ_SAFE_MODE_RESTART_inherited_present']==present
        assert 'dummy-private-value' not in raw and receipt['MOZ_SAFE_MODE_RESTART_removed'] is True
        results.append({'inherited_restart_present':present,'parent_unchanged':True,'child_controls_exact':True,'value_not_recorded':True})
print(json.dumps({'status':'PASS','cases':results,'scope':'Synthetic environment dictionaries only.'},indent=2))
