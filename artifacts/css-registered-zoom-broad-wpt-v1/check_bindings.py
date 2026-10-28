import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

helper = load('broad_runner', HERE / 'run.py')
succession = load('broad_succession', HERE / 'succession.py')
adoption = load('broad_adoption', HERE / 'adoption.py')
policy = helper.read(HERE / 'POLICY.json')
receipt = helper.read(HERE / 'HEAD-SUCCESSION.json')
previous = helper.read(ROOT / receipt['fixture_predecessor'] / 'POLICY.json')
roles = helper.read(ROOT / receipt['proposal'] / 'SOURCE-ROLES.json')
build,before,after = [helper.read(ROOT / receipt[key]) for key in ['build_epoch','before_epoch','after_epoch']]
base = [receipt,policy,previous,roles,build,before,after]
succession.validate_core(*base,helper.need)
rejected = []

def reject(name, mutate):
    values = copy.deepcopy(base)
    mutate(values)
    try:
        succession.validate_core(*values,helper.need)
    except (RuntimeError,KeyError):
        rejected.append(name)
    else:
        raise AssertionError(name)

reject('wrong original HEAD',lambda v:v[0].update(old_head='0'*40))
reject('wrong successor HEAD',lambda v:v[1].update(frozen_head='0'*40))
reject('changed held assertion',lambda v:next(iter(v[1]['held_subtests'].values())).pop())
reject('removed target',lambda v:next(iter(v[1]['target_subtests'].values())).pop())
reject('missing reftest',lambda v:v[1]['tests'].pop(next(n for n,k in v[1]['tests'].items() if k=='reftest')))
reject('old candidate source',lambda v:v[1]['source_roles']['candidate'].update({'servo/components/style/values/computed/length.rs':'0'*64}))
reject('removed unchanged source guard',lambda v:v[1]['unchanged_native_sources'].pop(next(iter(v[1]['unchanged_native_sources']))))
reject('missing candidate role',lambda v:v[3].pop(next(iter(v[3]))))
for index,label in [(4,'build'),(5,'signing before'),(6,'signing after')]:
    reject(label+' source drift',lambda v,i=index:v[i]['pins'].update({'servo/components/style/custom_properties.rs':'0'*64}))
    reject(label+' wrong provenance',lambda v,i=index:v[i]['registered_number_transition'].update(compiled=False))
    reject(label+' wrong HEAD',lambda v,i=index:v[i]['semantic_index'].update(head='0'*40))
reject('wrong binary binding',lambda v:v[0]['candidate_binaries'].update({next(iter(v[0]['candidate_binaries'])):'0'*64}))
reject('missing binary role',lambda v:v[0]['candidate_binaries'].pop(next(iter(v[0]['candidate_binaries']))))
actual = succession.validate(ROOT,HERE,policy,helper)
original = helper.read(HERE / 'ADOPTED-ORIGINAL.json')
path = ROOT / original['runtime'] / 'ASSESSMENT.json'
adopted = adoption.validate(ROOT,HERE,path,original['assessment_sha256'],policy,helper)
for name,probe_path,probe_sha in [
    ('another original path', path.with_name('RESULT.json'),original['assessment_sha256']),
    ('wrong original digest',path,'0'*64),
]:
    try:
        adoption.validate(ROOT,HERE,probe_path,probe_sha,policy,helper)
    except RuntimeError:
        rejected.append(name)
    else:
        raise AssertionError(name)
print(json.dumps({'actual_signed_chain':actual,'actual_original_raw_replay':adopted,
                  'core_positive':True,'rejected_controls':rejected,
                  'main_executed':False,'browser_executed':False},indent=2))
