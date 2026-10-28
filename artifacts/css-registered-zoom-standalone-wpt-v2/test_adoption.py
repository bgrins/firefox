import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
h=load('run');adopt=load('adoption');binding=h.read(HERE/'BASELINE.json');policy=h.read(HERE/'POLICY.json');runtime=ROOT/binding['runtime'];baseline=runtime/'ASSESSMENT.json'
expected=adopt.validate(ROOT,HERE,baseline,binding['assessment_sha256'],policy,h)
checks=[]
def reject(name,path,mutate):
    value=copy.deepcopy(h.read(path));mutate(value)
    helper=SimpleNamespace(**{k:getattr(h,k) for k in ['authenticate','sha','need','load','require_compiled_transition']})
    helper.read=lambda p:value if p==path else h.read(p)
    try:adopt.validate(ROOT,HERE,baseline,binding['assessment_sha256'],policy,helper)
    except (RuntimeError,ValueError,KeyError):checks.append(name)
    else:raise AssertionError(name)
for name,mutate in [
 ('binding not ready',lambda v:v.update(ready=False)),
 ('wrong assessment digest',lambda v:v.update(assessment_sha256='bad')),
 ('missing inventory entry',lambda v:v['files'].pop('raw.jsonl')),
 ('changed inventory digest',lambda v:v['files'].update({'raw.jsonl':'bad'})),
 ('changed tools symlink',lambda v:v['symlinks'].update({'tests/tools':'other'})),
]:reject(name,HERE/'BASELINE.json',mutate)
for name,mutate in [
 ('incomplete original',lambda v:v.update(complete=False)),
 ('unpreserved original',lambda v:v.update(execution_preserved=False)),
 ('wrong original role',lambda v:v.update(phase='candidate-1')),
 ('wrong original capsule',lambda v:v.update(capsule_manifest_sha256='bad')),
 ('wrong original experiment',lambda v:v.update(experiment_sha256='bad')),
 ('wrong original source map',lambda v:v.update(native_sources={})),
]:reject(name,baseline,mutate)
reject('unremoved processes',runtime/'CLEANUP.json',lambda v:v.update(owned_group_absent=False))
reject('temporary root retained',runtime/'CLEANUP.json',lambda v:v.update(temporary_root_removed=False))
reject('post metadata drift',runtime/'APPLICATION-METADATA-POST.json',lambda v:v.update(browser_build_id='other'))
reject('result execution error',runtime/'RESULT.json',lambda v:v.update(execution_error='error'))
reject('result preservation error',runtime/'RESULT.json',lambda v:v.update(preservation_error='error'))
reject('compiled baseline role drift',runtime/'EPOCH.json',lambda v:v['registered_number_transition'].update(role='candidate'))
reject('saved baseline native dirt',runtime/'EPOCH.json',lambda v:v['modified_native_paths'].append('extra'))
assert adopt.validate(ROOT,HERE,baseline,binding['assessment_sha256'],policy,h)==expected
(HERE/'ADOPTION-CONTROLS.json').write_text(json.dumps({'actual_baseline_positive':True,'negative_controls':checks,'owned_runtime_mutated':False,'browser_executed':False},indent=2)+'\n')
print(json.dumps({'positive':1,'negative':len(checks)}))
