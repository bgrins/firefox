import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import observations

HERE = Path(__file__).resolve().parent
METHODS = {'rebind', 'tick', 'ready', 'trigger', 'align'}
BASE = {'pid', 'seq', 'style_call', 'style_depth', 'event', 'object'}
TIMING = {'animation_index', 'target', 'document', 'timeline', 'next',
          'start_null', 'hold_null', 'pending', 'auto_align', 'rate'}

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def unique_object(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, 'duplicate JSON key: ' + k)
        result[k] = v
    return result

def loads(text):
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite JSON: '+s)))

def pointer(value):
    require(re.fullmatch(r'0x[0-9a-f]+|\(nil\)', value) is not None, 'pointer syntax')
    return None if value == '(nil)' or int(value[2:], 16) == 0 else hex(int(value[2:], 16))

def parse_native(text, row_number):
    require(text.startswith('CSSFB '), 'native prefix')
    tokens = text.rstrip('\n').split(' ')
    require(tokens[0] == 'CSSFB' and all(tokens[1:]), 'native spacing')
    fields = {}
    for token in tokens[1:]:
        require(token.count('=') == 1, 'native key/value token')
        k, v = token.split('=')
        require(k not in fields and bool(v), 'duplicate/empty native field')
        fields[k] = v
    event = fields.get('event')
    require(event not in {'cap', 'trace-error'}, 'trace capped or invalidated')
    if event in {'style', 'refresh', 'stale'}:
        expected = BASE | {'edge'}
        require(fields.get('edge') in {'enter', 'exit'}, 'scope edge')
        kind, edge = event, fields.get('edge')
    elif event in {'cache.enter', 'cache.exit'}:
        expected = BASE | {'document', 'source', 'cached'}
        if event == 'cache.exit':
            expected |= {'position', 'range'}
        kind, edge = event.split('.')
    elif event in {m+'.'+e for m in METHODS for e in ['enter', 'exit']}:
        expected = BASE | TIMING
        kind, edge = event.split('.')
    else:
        raise ValueError('unknown native event: ' + str(event))
    require(set(fields) == expected, 'native exact schema: ' + str(event))
    integers = {'pid', 'seq', 'style_call', 'style_depth', 'animation_index',
                'start_null', 'hold_null', 'pending', 'auto_align', 'cached'} & fields.keys()
    for k in integers:
        require(re.fullmatch(r'0|[1-9][0-9]*', fields[k]) is not None, 'integer syntax: '+k)
        fields[k] = int(fields[k])
    require(fields['pid'] > 0 and fields['seq'] > 0, 'nonpositive process/sequence')
    for k in {'start_null', 'hold_null', 'auto_align', 'cached'} & fields.keys():
        require(fields[k] in {0, 1}, 'boolean bit: '+k)
    if 'pending' in fields:
        require(fields['pending'] in {0, 1, 2}, 'pending enum')
        require(re.fullmatch(r'-?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:e[+-]?[0-9]+)?', fields['rate']) is not None, 'rate syntax')
        fields['rate'] = float(fields['rate'])
        require(math.isfinite(fields['rate']), 'nonfinite rate')
    for k in {'position', 'range'} & fields.keys():
        require(re.fullmatch(r'-?(?:0|[1-9][0-9]*)', fields[k]) is not None, 'coordinate syntax')
        fields[k] = int(fields[k])
    for k in {'object', 'target', 'document', 'timeline', 'next', 'source'} & fields.keys():
        fields[k] = pointer(fields[k])
    require(fields['object'] is not None, 'null event object')
    if kind in METHODS:
        require(fields['target'] is not None and fields['document'] is not None, 'null animation identity')
        require(kind == 'rebind' or fields['next'] is None, 'unexpected candidate timeline')
    if kind == 'cache':
        require(fields['document'] is not None, 'null cache document')
        require(not fields['cached'] or fields['source'] is not None, 'resolved cache without captured source')
    return dict(fields, kind=kind, edge=edge, row=row_number)

def extract(rows):
    native, obs = [], []
    for i, row in enumerate(rows):
        data = row.get('data', row.get('message', ''))
        if not isinstance(data, str):
            continue
        if 'CSSFB' in data:
            require(row.get('action') == 'process_output', 'native action')
            native.append(parse_native(data, i))
        if 'QF_PROBE' in data:
            require(row.get('action') == 'process_output' and data.startswith('QF_PROBE '), 'observation prefix/action')
            v = loads(data[len('QF_PROBE '):])
            require(isinstance(v, dict), 'observation object')
            if 'gate' in v:
                require(type(v['pending']) is bool, 'QF pending type')
                require(v['source'] in {None, 'fallback', 'provider'}, 'QF source')
                require(v['playState'] in {'idle','running','paused','finished'}, 'QF play state')
                require(all(isinstance(v[k],str) for k in ['gate','providerName','repeatGate']), 'QF strings')
                require(v['progress'] is None or (type(v['progress']) in {int,float} and math.isfinite(v['progress'])), 'QF progress')
                for k in ['timelineTime','currentTime','localTime']:
                    require(v[k] is None or isinstance(v[k],str) or (type(v[k]) in {int,float} and math.isfinite(v[k])), 'QF time type')
            obs.append((i,v))
    require(native, 'no native records')
    return native, obs

def pair_native(records):
    states = defaultdict(lambda: {'seq':0,'stack':[],'styles':[],'max_call':0})
    pairs = []
    for r in records:
        s=states[r['pid']]
        require(r['seq']==s['seq']+1, 'noncontiguous per-PID sequence')
        s['seq']=r['seq']
        if r['kind']=='style' and r['edge']=='enter':
            require(r['style_call']==s['max_call']+1, 'style call sequence')
            require(r['style_depth']==len(s['styles'])+1, 'style entry depth')
            s['max_call']=r['style_call']
            s['styles'].append(r)
        require(r['style_depth']==len(s['styles']), 'style depth context')
        require(r['style_call']==(s['styles'][-1]['style_call'] if s['styles'] else 0), 'style call context')
        if r['edge']=='enter':
            r['sampling_scopes']=[{'kind':x['kind'],'object':x['object'],'seq':x['seq']} for x in s['stack'] if x['kind'] in {'refresh','stale'}]
            s['stack'].append(r)
        else:
            require(s['stack'], 'exit without entry')
            entry=s['stack'].pop()
            require((entry['kind'],entry['object'])==(r['kind'],r['object']), 'scope identity/order')
            require((entry['style_call'],entry['style_depth'])==(r['style_call'],r['style_depth']), 'scope style identity')
            if r['kind'] in METHODS:
                require(all(entry[k]==r[k] for k in ['target','document','next']), 'method live identity')
            if r['kind']=='cache':
                require(entry['document']==r['document'], 'cache document identity')
            pairs.append({'enter':entry,'exit':r})
            if r['kind']=='style':
                require(s['styles'].pop() is entry, 'style scope identity')
    require(all(not s['stack'] and not s['styles'] for s in states.values()), 'unbalanced scopes at end')
    return pairs, {str(pid):{'records':s['seq'],'style_calls':s['max_call']} for pid,s in states.items()}

def summarize_mode(mode, obs, records, pairs):
    selected_obs=[(i,v) for i,v in obs if v['mode']==mode]
    start=next(i for i,v in selected_obs if v['phase']=='armed-before')
    end=next(i for i,v in selected_obs if v['phase']=='complete')
    selected=[r for r in records if start < r['row'] < end]
    methods=[r for r in selected if r['kind'] in METHODS]
    identities={(r['pid'],r['document'],r['target'],r['object']) for r in methods}
    require(len(identities)==1, 'mode active animation identity: '+mode)
    identity=next(iter(identities))
    require(all(r['rate']==1 for r in methods), 'fixture playback rate')
    selected_pairs=[p for p in pairs if p['enter']['row'] > start and p['enter']['row'] < end and p['enter']['kind'] in METHODS]
    require(all(p['exit']['row']<end for p in selected_pairs), 'method crosses QF complete')
    restores=[]
    transitions=[]
    for p in selected_pairs:
        a,b=p['enter'],p['exit']
        common={'enter_seq':a['seq'],'exit_seq':b['seq'],'style_call':a['style_call'],'style_depth':a['style_depth'],'sampling_scopes':a['sampling_scopes']}
        if a['start_null']==1 and a['hold_null']==1 and (b['start_null']==0 or b['hold_null']==0):
            restores.append(dict(common,method=a['kind'],timeline_before=a['timeline'],timeline_after=b['timeline']))
        if a['kind']=='rebind' and a['timeline']!=b['timeline']:
            require(b['timeline']==a['next'], 'changed rebind missed candidate')
            transitions.append(dict(common,old=a['timeline'],candidate=a['next'],new=b['timeline'],start_null_after=b['start_null'],hold_null_after=b['hold_null'],pending_after=b['pending']))
    require(transitions, 'no changed association: '+mode)
    ready=[r for r in restores if r['method']=='ready']
    snapshots=[v for _,v in selected_obs if v['phase'].startswith(('sync-','frame-'))]
    signatures=[{k:v[k] for k in ['gate','source','pending','progress','providerName','playState']} for v in snapshots]
    return {'identity':dict(zip(['pid','document','target','animation_pointer'],identity)), 'native_records_in_armed_window':len(selected),'method_pairs':len(selected_pairs), 'ready_restorations_at_style_depth_zero':sum(r['style_depth']==0 for r in ready),'ready_restorations_at_style_depth_nonzero':sum(r['style_depth']>0 for r in ready),'restorations_all_methods':restores,'actual_rebind_transitions':transitions,'distinct_snapshot_signatures':list({json.dumps(v,sort_keys=True):v for v in signatures}.values()),'nullness_is_not_full_state_identity':True,'cross_stream_phase_order_proved':False}

def analyze(rows):
    qf=observations.analyze(rows)
    native, obs=extract(rows)
    pairs,pids=pair_native(native)
    totals={m:{'depth_zero':0,'depth_nonzero':0} for m in sorted(METHODS)}
    changed=[]
    for pair in pairs:
        entry,exit=pair['enter'],pair['exit']
        if entry['kind'] not in METHODS:continue
        if entry['start_null'] and entry['hold_null'] and (not exit['start_null'] or not exit['hold_null']):
            totals[entry['kind']]['depth_nonzero' if entry['style_depth'] else 'depth_zero']+=1
        if entry['kind']=='rebind' and entry['timeline']!=exit['timeline']:
            require(exit['timeline']==entry['next'], 'changed rebind missed candidate')
            changed.append({'pid':entry['pid'],'enter_seq':entry['seq'],'exit_seq':exit['seq'],'style_call':entry['style_call'],'style_depth':entry['style_depth'],'old':entry['timeline'],'new':exit['timeline']})
    per_call=defaultdict(int)
    for change in changed:
        per_call[(change['pid'],change['style_call'],change['style_depth'])]+=1
    histogram=defaultdict(int)
    for count in per_call.values():histogram[str(count)]+=1
    return {'global_changed_rebinds_per_style_call_histogram':dict(sorted(histogram.items())),'cross_stream_phase_order_proved':False,'global_restorations_by_method_and_style_depth':totals,'global_changed_rebinds':changed,'native_records':len(native),'paired_scopes':len(pairs),'pids':pids,'callbacks_pass':4,'harness_ok':1,'caps':0,'observations':qf,'modes':{m:summarize_mode(m,obs,native,pairs) for m in observations.MODES},'full_state_recurrence_established':False,'snapshots_are_atomic':False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('run_directory',type=Path)
    parser.add_argument('--output',type=Path,default=HERE/'ANALYSIS.json')
    args=parser.parse_args()
    receipt_path=args.run_directory/'RESULT.json'
    require(receipt_path.is_file(),'run incomplete: RESULT.json absent')
    receipt=loads(receipt_path.read_text())
    require(not receipt.get('error'),'native transaction failed')
    require(receipt['commands']['build']['exit_code']==0,'native build failed')
    require(receipt['commands']['wpt']['exit_code']==0,'WPT nonzero terminal')
    require(receipt.get('restoration_verified') is True,'runner restoration unverified')
    restored_path=args.run_directory/'RESTORED.json'
    restored=loads(restored_path.read_text())
    require(all(restored.get(k) is True for k in ['source_and_application_restored','index_preserved','temporary_fixture_removed','backup_removed']), 'restoration receipt incomplete')
    for kind in ['build','wpt']:
        require(receipt['commands'][kind].get('group_absent') is True,'owned process group remains')
    raw=args.run_directory/'wpt-raw.jsonl'
    result=analyze([loads(line) for line in raw.read_text().splitlines()])
    result['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [receipt_path,restored_path,raw]}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:',result['native_records'],'records,',result['paired_scopes'],'balanced pairs across',len(result['pids']),'PIDs')
    for m,r in result['modes'].items():
        print(m,'ready depth0/nonzero:',r['ready_restorations_at_style_depth_zero'],r['ready_restorations_at_style_depth_nonzero'],'rebindings:',len(r['actual_rebind_transitions']))

if __name__=='__main__':
    main()
