import copy, hashlib, importlib.util, json, subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('assessment',P/'assess.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def synthetic(mode):
    data={'schema':'root-self-animation-context-v1','cleanup':True,'errors':[],'cases':[]}
    info={'targetIsRoot':True,'progress':.5,'playState':'paused','currentTime':500,'keyframes':[{},{}]}
    initial={'fontSize':'16px','lineHeight':'normal','rem':16,'rlh':19}
    for unit in ('rem','rlh'):
        for prop in ('fontVariationSettings','fontSize'):
            for size,line in ((23,37),(31,47)):
                expected=2*initial[unit];root=2*(size if unit=='rem' else line)
                c={'unit':unit,'property':prop,'size':size,'line':line,'compatMode':'CSS1Compat','referenceCompatMode':'CSS1Compat','initial':copy.deepcopy(initial),'referenceInitial':copy.deepcopy(initial),'supports':[True,True],'literalInfo':copy.deepcopy(info),'literalRaw':'30px' if prop=='fontSize' else '"wdth" 30','inheritedControlRaw':'32px','inheritedControlInfo':copy.deepcopy(info),'underlying':{'fontSize':f'{size}px','lineHeight':f'{line}px','writingMode':'horizontal-tb','textOrientation':'mixed'},'ordinarySizeRaw':f'{expected}px','ordinarySizeValue':expected,'ordinaryVariationRaw':f'"wdth" {expected}','ordinaryVariationValue':expected,'samples':[]}
                for timing in ('first','settled'):
                    value=expected if mode=='initial-reference' else root if mode=='underlying-root' else 111 if mode=='other' or timing=='settled' else expected
                    c['samples'].append({'timing':timing,'raw':f'{value}px' if prop=='fontSize' else f'"wdth" {value}','value':value,'animation':copy.deepcopy(info)})
                data['cases'].append(c)
    return data
for mode in ('initial-reference','underlying-root','other','unstable'):
    r=m.assess(synthetic(mode));assert r['rows_count']==16 and r['calibrated']
    if mode=='unstable':assert not any(x['stable'] for x in r['rows'])
    else:assert all(x['classification']==mode for x in r['rows'])
d=synthetic('initial-reference');d['cases'][0]['ordinarySizeRaw']='99px';d['cases'][0]['ordinarySizeValue']=99
assert m.assess(d)['calibrated'] is False
mutants={
 'missing':lambda d:d['cases'].pop(),
 'duplicate':lambda d:d['cases'].__setitem__(0,d['cases'][1]),
 'cleanup':lambda d:d.__setitem__('cleanup',False),
 'compat':lambda d:d['cases'][0].__setitem__('compatMode','BackCompat'),
 'admission':lambda d:d['cases'][0].__setitem__('supports',[False,True]),
 'initial_mismatch':lambda d:d['cases'][0]['referenceInitial'].__setitem__('rlh',22),
 'literal':lambda d:d['cases'][0].__setitem__('literalRaw','"wdth" 31'),
 'inherited_base':lambda d:d['cases'][0].__setitem__('inheritedControlRaw','46px'),
 'underlying':lambda d:d['cases'][0]['underlying'].__setitem__('fontSize','99px'),
 'target':lambda d:d['cases'][0]['samples'][0]['animation'].__setitem__('targetIsRoot',False),
 'timing':lambda d:d['cases'][0]['samples'][0]['animation'].__setitem__('progress',.25),
 'raw':lambda d:d['cases'][0]['samples'][0].__setitem__('raw','"wdth" 99'),
}
for name,mutate in mutants.items():
    d=synthetic('initial-reference');mutate(d)
    try:m.assess(d)
    except AssertionError:pass
    else:raise AssertionError(name)
subprocess.run(['node','--check',str(P/'probe.js')],check=True)
result={'synthetic_positive_paths':4,'uncalibrated_path':1,'rejecting_controls':len(mutants),'javascript_syntax':True,'browser_execution':False,'native_execution':False,'tested_inputs':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['probe.js','assess.py','check.py']}}
(P/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
