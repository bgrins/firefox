import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT/'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT/'tools/third_party').iterdir() if p.is_dir()] + [str(WPT/'tools'),str(WPT),str(ROOT/'third_party/python/pyyaml/lib')]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

page = 'animation-duration-feedback-consistency-observation.tentative.html'
handler_name = 'duration-feedback-discriminator-record.py'
source = (HERE/page).read_text()
dom = html5lib.parse(source,namespaceHTMLElements=False)
scripts = [node.text or '' for node in dom.iter('script') if not node.get('src')]
assert len(scripts)==1 and dom.find('body').find('script') is not None
assert source.index('await collect("repeat-750")') < source.index('await fetch(') < source.index('  for (const trajectory of trajectories)')
assert source.index('animation.currentTime = 751') < source.index('await collect("action-751")') < source.index('await collect("return-750")')
program = "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{promise_test:(fn,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"
names = json.loads(subprocess.run(['node','-e',program],input=scripts[0],text=True,capture_output=True,check=True).stdout)
assert names == ['Observation only: coupled duration feedback read order, seek, restyle and override',
                 'Observation only: zero-start duration feedback read order, seek, restyle and override']
spec = importlib.util.spec_from_file_location('discriminator_record',HERE/handler_name)
handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler)


def record(kind):
    count = 2 if kind=='coupled' else 1
    style = {'font':'22.85px','cssDuration':'1.42813s','opacity':'0.428571','outlineWidth':'0px'}
    effect = {'name':'fontCycle','time':750,'duration':1428.125,'progress':None,'state':'paused'}
    def reading(order):
        return {'order':order,'style':copy.deepcopy(style),'effects':[copy.deepcopy(effect) for _ in range(count)],
                'repeatEffects':[copy.deepcopy(effect) for _ in range(count)],'repeatStyle':copy.deepcopy(style),
                'sameAnimations':[False]*count,'sameEffects':[True]*count,
                'currentEffects':[],'afterMembershipStyle':copy.deepcopy(style)}
    return {'kind':kind,'trajectories':[{'role':role,
            'acquisition':{'beforeReady':reading('timing-first'),'afterReady':reading('timing-first')},
            'phases':[{'name':name,'reads':[reading(order) for order in
                (['timing-first','style-first'] if index%2 else ['style-first','timing-first'])]}
                for index,name in enumerate(handler.PHASES)]} for role in handler.ROLES]}


positive, negative = 0, []
with tempfile.TemporaryDirectory(prefix='duration-discriminator-transport-') as temporary:
    parent = Path(temporary)
    directory = parent/'records'
    directory.mkdir(mode=0o700)
    keys = ['DURATION_FEEDBACK_RECORD_DIR','DURATION_FEEDBACK_RUN_ID']
    old = {key:os.environ.get(key) for key in keys}
    run_id = 'discriminator-static-0123456789'
    os.environ.update(DURATION_FEEDBACK_RECORD_DIR=str(directory),DURATION_FEEDBACK_RUN_ID=run_id)
    def snapshot():
        return {p.name:p.read_bytes() for p in directory.iterdir() if p.is_file() and not p.is_symlink()}
    def invoke(value,method='POST'):
        return handler.main(SimpleNamespace(method=method,body=json.dumps(value).encode()),None)
    def reject(label,call):
        before = snapshot()
        try:
            call()
        except (AssertionError,ValueError,TypeError,KeyError,OSError):
            pass
        else:
            raise AssertionError(label)
        assert snapshot()==before
        negative.append(label)
    try:
        for kind,filename in handler.FILES.items():
            value = record(kind)
            headers,body = invoke(value)
            assert json.loads(body)=={'run_id':run_id,'kind':kind,'sampleCount':20}
            assert json.loads((directory/filename).read_bytes())=={'run_id':run_id,**value}
            assert stat.S_IMODE((directory/filename).stat().st_mode)==0o600
            reject('exclusive '+kind,lambda:invoke(value))
            positive += 1
        for path in directory.iterdir():
            path.unlink()
        valid = record('coupled')
        def altered(change):
            value = copy.deepcopy(valid)
            change(value)
            return invoke(value)
        for label,change in [
            ('path from request',lambda v:v.update(kind='../escape')),
            ('extra field',lambda v:v.update(extra=True)),
            ('missing acquisition',lambda v:v['trajectories'][0]['acquisition'].pop('beforeReady')),
            ('missing phase',lambda v:v['trajectories'][0]['phases'].pop()),
            ('phase order',lambda v:v['trajectories'][0]['phases'].reverse()),
            ('role order',lambda v:v['trajectories'].reverse()),
            ('missing read',lambda v:v['trajectories'][0]['phases'][0]['reads'].pop()),
            ('wrong read order',lambda v:v['trajectories'][0]['phases'][0]['reads'].reverse()),
            ('missing effect',lambda v:v['trajectories'][0]['phases'][0]['reads'][0]['effects'].pop()),
            ('boolean progress',lambda v:v['trajectories'][0]['phases'][0]['reads'][0]['effects'][0].update(progress=True)),
            ('numeric membership',lambda v:v['trajectories'][0]['phases'][0]['reads'][0].update(sameAnimations=[1,1])),
        ]:
            reject(label,lambda change=change:altered(change))
        reject('wrong method',lambda:invoke(valid,'GET'))
        reject('too large',lambda:handler.main(SimpleNamespace(method='POST',body=b' '*65537),None))
        reject('non-JSON number',lambda:handler.main(SimpleNamespace(method='POST',body=b'{"kind":NaN}'),None))
        os.environ[keys[1]]='short'
        reject('short run ID',lambda:invoke(valid))
        os.environ[keys[1]]=run_id
        os.environ[keys[0]]='relative'
        reject('relative directory',lambda:invoke(valid))
        os.environ[keys[0]]=str(directory)
        directory.chmod(0o755)
        reject('public directory',lambda:invoke(valid))
        directory.chmod(0o700)
        alias=parent/'alias';alias.symlink_to(directory,target_is_directory=True)
        os.environ[keys[0]]=str(alias)
        reject('symlink directory',lambda:invoke(valid))
        os.environ[keys[0]]=str(directory)
        retained=parent/'retained';retained.write_text('retained')
        (directory/'coupled.json').symlink_to(retained)
        reject('symlink destination',lambda:invoke(valid))
        assert retained.read_text()=='retained'
    finally:
        for key,value in old.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value

with tempfile.TemporaryDirectory(prefix='duration-discriminator-manifest-') as temporary:
    scratch=Path(temporary)
    folder=scratch/'css/css-animations';folder.mkdir(parents=True)
    for name in [page,handler_name]:shutil.copyfile(HERE/name,folder/name)
    (scratch/'lint.ignore').write_text('')
    paths=['css/css-animations/'+name for name in [page,handler_name]]
    manifest=Manifest(str(scratch),'/');manifest.update([(path,None,True) for path in paths],parallel=False)
    serialized=json.loads(json.dumps(manifest.to_json()))
    assert set(serialized['items']['testharness']['css']['css-animations'])=={page}
    (HERE/'SUBSET-MANIFEST.json').write_text(json.dumps(serialized,indent=2,sort_keys=True)+'\n')
    previous=os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch),paths,'normal',jobs=1)==0
    finally:os.chdir(previous)
result={'registered_names':names,'explicit_body':True,'acquisition_reads_per_callback':10,
        'phase_target_rows_per_callback':20,'ordered_reads_per_phase_target':2,
        'positive_transport_cases':positive,'negative_transport_cases':negative,
        'observed_inconsistency_accepted_by_transport':True,'lint_errors':0,
        'browser_or_http_server_executed':False,'scratch_removed':True}
(HERE/'CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2))
