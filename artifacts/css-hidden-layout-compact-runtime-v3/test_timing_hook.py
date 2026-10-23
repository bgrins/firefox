import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S')
sys.dont_write_bytecode = True
import ast
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import shutil
import tempfile
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parent
module = ast.parse((SOURCE/'experiment.py').read_text())
selected = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'timing_run']
if len(selected)!=1: raise RuntimeError('missing timing hook')
code = compile(ast.Module(body=selected,type_ignores=[]),'extracted-timing-hook','exec')
with contextlib.redirect_stdout(io.StringIO()):
    synthetic=runpy.run_path(str(SOURCE.parent/'css-hidden-layout-cost-review-v2/source/test_tools.py'))
observation=synthetic['observation']; observation['label']='baseline'
summary=synthetic['validator'].validate(observation,synthetic['config'],'baseline')
def need(ok,why):
    if not ok: raise RuntimeError(why)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
results={}
for scenario in ['complete','measurement-failure','cleanup-error','live-group','nested-terminal-false','missing-receipt','pin-mismatch','resource-drift','summary-mismatch','profile-remains']:
    with tempfile.TemporaryDirectory(prefix='hidden-cost-hook-') as tmp:
        root=Path(tmp); here=root/'artifact'; here.mkdir(); shutil.copytree(SOURCE/'cost',here/'cost')
        for n in ['native','firefox','XUL','resource']: (root/n).write_text(n)
        paths=['native','firefox','XUL','resource']; pins={n:sha(root/n) for n in paths}
        expected={str((here/'cost'/n).resolve()):sha(here/'cost'/n) for n in ['probe.html','benchmark.js','CONFIG.json','run.py','validate.py','cleanup.py']}
        expected.update({str((root/n).resolve()):pins[n] for n in ['native','firefox','XUL']})
        output=here/'baseline-timing'
        def save(n,value): (here/n).write_text(json.dumps(value))
        def command(name,args):
            output.mkdir()
            result={'before':expected,'after':copy.deepcopy(expected),'stable':True,
                    'cleanupErrors':[],'profileRemoved':True,'terminal':True,'noLiveGroup':True,
                    'termination':{'terminal':True,'noLiveGroup':True,'errors':[]},'failure':None,'observations':[observation]}
            status=0
            if scenario=='measurement-failure': status=1; result['failure']='deadline'; result['observations']=[]
            if scenario=='cleanup-error': result['cleanupErrors']=['EPERM']
            if scenario=='live-group': result['noLiveGroup']=False
            if scenario=='nested-terminal-false': result['termination']['terminal']=False
            if scenario=='pin-mismatch': result['after'][str(root/'native')]='wrong'
            if scenario=='resource-drift': (root/'resource').write_text('drift')
            if scenario=='profile-remains': (output/'profile').mkdir()
            if scenario!='missing-receipt': (output/'RESULT.json').write_text(json.dumps(result))
            saved_summary=copy.deepcopy(summary)
            if scenario=='summary-mismatch': saved_summary['queryReads']+=1
            (output/'SUMMARY.json').write_text(json.dumps(saved_summary))
            return status
        env={'HERE':here,'ROOT':root,'c':{'guard_sources':['native']},'inputs':{'resource_pins':{'resource':pins['resource']}},
             'TIMING_FILES':['probe.html','benchmark.js','CONFIG.json','run.py','validate.py','cleanup.py'],
             'sha':sha,'sys':sys,'json':json,'importlib':importlib,'need':need,
             'epoch':lambda:None,'sources_expected':lambda s:None,'authenticate_payloads':lambda:None,
             'wpt':SimpleNamespace(BINARIES=['firefox','XUL'],pins=lambda names:{n:sha(root/n) for n in names},save=save,command=command)}
        exec(code,env)
        try:
            result=env['timing_run']('baseline',{})
        except RuntimeError as error:
            if scenario in ['complete','measurement-failure']: raise
            results[scenario]={'rejected':True,'reason':str(error)}
        else:
            if scenario not in ['complete','measurement-failure']: raise RuntimeError('unsafe hook accepted '+scenario)
            need(result['cleanup_verified'] and result['measurement_complete']==(scenario=='complete'),'wrong outcome')
            results[scenario]={'accepted':True,'measurement_complete':result['measurement_complete']}
print(json.dumps({'status':'PASS','scope':'Extracted parent hook with synthetic files/receipts; no browser, build or Git.','cases':results},indent=2))
