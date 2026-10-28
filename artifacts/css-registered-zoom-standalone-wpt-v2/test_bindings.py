import copy
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=load('run');validator=load('bindings')
experiment=base.read(HERE/'EXPERIMENT.json');positives=[];negatives=[]
class Helper:
    need=staticmethod(base.need)
    def __init__(self,pol,epoch,result):self.pol=pol;self.epoch=epoch;self.result=result
    def read(self,p):
        if p==HERE/'EXPERIMENT.json':return experiment
        if str(p).endswith('RESULT.json'):return self.result
        if str(p).endswith('EPOCH.json'):return self.epoch
        raise ValueError(p)
    def sha(self,p):
        return 'result' if str(p).endswith('RESULT.json') else 'epoch' if str(p).endswith('EPOCH.json') else 'experiment'
for role in ['original','candidate']:
    pol=base.read(HERE/'POLICY.json');pol.update(phase=role+'-1',build_result='artifacts/css-registered-number-native-runtime-v1/zoom-standalone-'+role+'-build-1/RESULT.json',build_result_sha256='result',epoch_sha256='epoch',build_epoch_sha256='epoch')
    pol['build_epoch']=pol['build_result'].replace('RESULT.json','EPOCH.json');pol['phase_binaries']={n:'binary'+str(i) for i,n in enumerate(pol['normal_binaries'])}
    epoch={'semantic_index':{'head':pol['frozen_head']},'registered_number_transition':{'role':role,'variant':'zoom-standalone-v1','compiled':True,'accepted':False,'last_phase':Path(pol['build_result']).parent.name},'modified_native_paths':[] if role=='original' else sorted(experiment['zoom_source_paths']),'pins':dict(pol['source_roles'][role],**pol['phase_binaries'])}
    result={'source_role':role,'command_success':True,'preservation_verified':True,'owned_processes':{},'publication_errors':[]}
    validator.validate_phase(ROOT,HERE,pol,epoch,Helper(pol,epoch,result));positives.append(role)
    changes=[('wrong receipt role',lambda p,e,r:r.update(source_role='other')),('failed build',lambda p,e,r:r.update(command_success=False)),('unpreserved build',lambda p,e,r:r.update(preservation_verified=False)),('live build process',lambda p,e,r:r.update(owned_processes={'pid':1})),('publication error',lambda p,e,r:r.update(publication_errors=['x'])),('wrong variant',lambda p,e,r:e['registered_number_transition'].update(variant='other')),('uncompiled',lambda p,e,r:e['registered_number_transition'].update(compiled=False)),('accepted',lambda p,e,r:e['registered_number_transition'].update(accepted=True)),('wrong HEAD',lambda p,e,r:e['semantic_index'].update(head='other')),('wrong dirty count',lambda p,e,r:e['modified_native_paths'].append('extra')),('native drift',lambda p,e,r:e['pins'].update({next(iter(p['source_roles'][role])):'other'})),('binary drift',lambda p,e,r:e['pins'].update({p['normal_binaries'][0]:'other'})),('wrong saved epoch hash',lambda p,e,r:p.update(build_epoch_sha256='other')),('wrong build receipt hash',lambda p,e,r:p.update(build_result_sha256='other')),('wrong last phase',lambda p,e,r:e['registered_number_transition'].update(last_phase='other')),('test roster drift',lambda p,e,r:p['tests'].pop(next(iter(p['tests']))))]
    for name,mutate in changes:
        p,e,r=copy.deepcopy((pol,epoch,result));mutate(p,e,r)
        try:validator.validate_phase(ROOT,HERE,p,e,Helper(p,e,r))
        except (RuntimeError,KeyError,ValueError):negatives.append(role+':'+name)
        else:raise AssertionError(name)
(HERE/'BINDING-CONTROLS.json').write_text(json.dumps({'positive':positives,'negative':negatives,'browser_executed':False},indent=2)+'\n')
print(json.dumps({'positive':len(positives),'negative':len(negatives)}))
