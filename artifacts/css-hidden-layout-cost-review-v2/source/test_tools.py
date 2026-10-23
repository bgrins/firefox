import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require python3 -I -S')
sys.dont_write_bytecode = True
import copy
import importlib.util
import json
import os
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

validator, cleanup = load('validate'), load('cleanup')
config = json.loads((HERE / 'CONFIG.json').read_text())
configs = [(k,s,n) for k in config['kinds'] for s in config['states'] for n in config['sizes']]
rows = []
for round_no in range(config['measured_rounds']):
    for slot in range(len(configs)):
        ordinal = (slot + round_no + config['warmup_rounds']) % len(configs)
        kind, state, count = configs[ordinal]
        n = min(count,config['query_limit'])
        indices = [0] if n == 1 else [i*(count-1)//(n-1) for i in range(n)]
        observations = []
        for iteration in range(config['iterations']):
            width = 168 if iteration % 2 == 0 else 160
            for bucket, selected in [('first',indices[:1]),('repeat',indices[:1]),('distinct',indices[1:]),('secondPass',indices)]:
                observations.extend({'bucket':bucket,'iteration':iteration,'index':i,'width':width,'rect':validator.expected(kind,i,width)} for i in selected)
        final_width = 168 if (config['iterations']-1)%2 == 0 else 160
        for iteration in range(config['no_mutation_iterations']):
            observations.extend({'bucket':'noMutation','iteration':iteration,'index':i,'width':final_width,'rect':validator.expected(kind,i,final_width)} for i in indices)
        rows.append({'round':round_no,'slot':slot,'ordinal':ordinal,'kind':kind,'state':state,'count':count,'indices':indices,
                     'constructionMs':0,'establishMs':0,'mutationFlushMs':0,
                     'outerChecksum':sum((168 if i%2==0 else 160)+64 for i in range(config['iterations'])),
                     'calibration':[{'width':w,'index':i,'rect':validator.expected(kind,i,w)} for w in [160,168] for i in indices],
                     'initial':[validator.expected(kind,i,160) for i in indices],
                     'times':{k:[0]*(config['no_mutation_iterations'] if k=='noMutation' else config['iterations']) for k in validator.BUCKETS},
                     'observations':observations})
observation = {'complete':True,'config':config,'label':'synthetic','elapsedMs':0,'rows':rows}
summary = validator.validate(observation,config,'synthetic')
assert summary['measuredRows']==84 and summary['queryReads']==13440 and summary['geometryMismatches']==0
serialized_bytes = len(json.dumps(observation).encode())
assert serialized_bytes < 4000000
bad = copy.deepcopy(observation);bad['rows'][0]['observations'].pop()
try: validator.validate(bad,config,'synthetic')
except ValueError: pass
else: raise AssertionError('omitted query accepted')
bad = copy.deepcopy(observation);bad['rows'][0]['calibration'][0]['rect'][0] += 1
try: validator.validate(bad,config,'synthetic')
except ValueError: pass
else: raise AssertionError('wrong visible position accepted')
bad = copy.deepcopy(observation);bad['rows'][0]['observations'][0]['rect'][0] += 1
assert validator.validate(bad,config,'synthetic')['geometryMismatches']==1

class Process:
    pid = 12345
    def __init__(self, status=None): self.returncode=status
    def poll(self): return self.returncode
    def terminate(self): self.returncode=-15
    def wait(self,timeout):
        if self.returncode is None: raise cleanup.subprocess.TimeoutExpired('fake',timeout)
        return self.returncode

def member(pid=12345,birth='original',state='S'):
    return {'pid':pid,'pgid':12345,'uid':os.getuid(),'sid':12345,'currentPgid':12345,'state':state,'birth':birth}

results = {}
for text in ['', '12345 12345 malformed\n', '12345 nope 501 S Thu Oct 22 10:00:00 2026\n']:
    with patch.object(cleanup.subprocess,'run',return_value=cleanup.subprocess.CompletedProcess([],0,text,'')):
        try: cleanup.members(12345)
        except (RuntimeError,ValueError): pass
        else: raise AssertionError('malformed ps listing accepted')
results['malformed_ps_rejected'] = ['empty listing','short row','nonnumeric identity']
leader, child = member(), member(12346)
with patch.object(cleanup,'members',side_effect=[[leader],[],[]]), patch.object(cleanup.os,'killpg') as kill:
    result=cleanup.terminate_owned(Process(),[leader]);assert result['terminal'] and not kill.called
    results['graceful_leader_no_group_signal']=result
with patch.object(cleanup,'members',return_value=[]), patch.object(cleanup.os,'killpg') as kill:
    result=cleanup.terminate_owned(Process(0),[leader]);assert result['terminal'] and not kill.called
    results['already_departed_no_group_signal']=result
with patch.object(cleanup,'members',side_effect=[[leader,child],[child],[child],[],[]]), patch.object(cleanup.os,'killpg') as kill:
    result=cleanup.terminate_owned(Process(),[leader,child]);assert result['terminal'] and kill.call_count==1
    results['verified_survivor_TERM_only']=result
with patch.object(cleanup,'members',side_effect=[[leader,child],[child],[child],[child]]), patch.object(cleanup.os,'killpg',side_effect=PermissionError('synthetic EPERM')):
    result=cleanup.terminate_owned(Process(),[leader,child]);assert not result['terminal'] and result['errors']
    results['EPERM_rejected']=result
reused=member(12346,'different-birth')
with patch.object(cleanup,'members',return_value=[reused]), patch.object(cleanup.os,'killpg') as kill:
    result=cleanup.terminate_owned(Process(0),[leader,child]);assert not result['terminal'] and not kill.called
    results['unanchored_reused_group_not_signalled']=result
with patch.object(cleanup,'members',return_value=[member(12346,state='Z')]), patch.object(cleanup.os,'killpg') as kill:
    result=cleanup.terminate_owned(Process(0),[leader]);assert result['terminal'] and not kill.called
    results['zombie_not_live_and_not_signalled']=result
print(json.dumps({'status':'PASS_SYNTHETIC_NO_BROWSER','rows':84,'reads':13440,'serialized_synthetic_bytes':serialized_bytes,
                  'validator_controls':['full roster','omitted query rejected','visible wrong position rejected','target wrong position retained'],
                  'cleanup_controls':results},indent=2))
