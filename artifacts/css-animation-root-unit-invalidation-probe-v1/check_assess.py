import copy,json,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('probe_assess',P/'assess.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def example(kind):
    data={'schema':'animation-root-unit-invalidation-v1','userAgent':'synthetic checker control, not browser','cleanup':True,'errors':[],'frames':[]}
    for unit in m.UNITS:
        for order in m.ORDERS:
            f={'unit':unit,'order':order,'compatMode':'CSS1Compat','supports':{'variation':[True,True],'width':True,'opacity':True},'rows':[]};data['frames'].append(f)
            for phase in m.PHASES:
                for timing in ('first','settled'):
                    initial=phase=='initial';size,line=(23,37) if initial else (31,47);base=size if unit=='rem' else line
                    progress=.25 if phase=='seek-quarter' else .5;expected=(1+2*progress)*base;old=(1+2*progress)*(23 if unit=='rem' else 37)
                    stale=(kind=='retained' and phase in ('root-change','seek-quarter','seek-half')) or (kind=='transient' and phase=='root-change' and timing=='first') or (kind=='numeric-only' and phase=='root-change')
                    actual=old if stale else expected;width=expected if kind=='numeric-only' else actual
                    def animation(p):return {'playState':'paused','progress':p,'currentTime':p*1000,'keyframes':[{},{}]}
                    r={'phase':phase,'timing':timing,'rootSize':size,'rootLine':line,'progress':progress,'expectedCurrent':expected,'expectedOriginal':old,
                       'variationRaw':f'"wdth" {actual}','variationValue':actual,'widthRaw':f'{width}px','widthValue':width,'opacityRaw':str(actual/1000),'opacityRatioValue':actual/1000,
                       'staticVariationRaw':f'"wdth" {2*base}','staticVariationValue':2*base,'staticWidthValue':2*base,'staticOpacityRatioValue':2*base/1000,'rootReference':base,
                       'absoluteVariationValue':30,'literalVariationValue':30,'literalWidthValue':30,'opacity':.6,'rootFontSize':f'{size}px','rootLineHeight':f'{line}px','parentFontSize':'30px','childFontSize':'60px',
                       'variationAnimation':animation(progress),'widthAnimation':animation(progress),'opacityAnimation':animation(progress),'literalVariationAnimation':animation(.5),'literalWidthAnimation':animation(.5)}
                    f['rows'].append(r)
    return data
for kind in ['current','retained','transient','numeric-only']:
    out=m.assess(example(kind));assert out['calibrated'] and out['rows_count']==72
    root=[r for r in out['rows'] if r['phase']=='root-change']
    if kind=='current':assert all(r['classifications']['variation']=='current-root' for r in root)
    if kind=='retained':assert all(r['classifications']['variation']=='original-root' for r in root)
    if kind=='transient':assert all(r['classifications']['variation']==('original-root' if r['timing']=='first' else 'current-root') for r in root)
    if kind=='numeric-only':assert all(r['classifications']['variation']=='original-root' and r['classifications']['width']=='current-root' for r in root)
base=example('current');mutations=[]
for key,value in [('cleanup',False),('errors',['error'])]:
    d=copy.deepcopy(base);d[key]=value;mutations.append(d)
d=copy.deepcopy(base);d['frames'].pop();mutations.append(d)
d=copy.deepcopy(base);d['frames'][1]=copy.deepcopy(d['frames'][0]);mutations.append(d)
d=copy.deepcopy(base);d['frames'][0]['rows'].pop();mutations.append(d)
for key,value in [('phase','invented'),('rootSize',99),('variationValue',99),('expectedCurrent',99)]:
    d=copy.deepcopy(base);d['frames'][0]['rows'][0][key]=value;mutations.append(d)
d=copy.deepcopy(base);d['frames'][0]['rows'][0]['variationAnimation']['progress']=.1;mutations.append(d)
for d in mutations:
    try:m.assess(d)
    except (AssertionError,ValueError):pass
    else:raise AssertionError('Corrupted stream admitted')
d=copy.deepcopy(base);d['frames'][0]['rows'][0]['literalWidthValue']=31
out=m.assess(d);assert not out['calibrated'] and out['rows'][0]['classifications']['variation']=='uncalibrated'
print(json.dumps({'synthetic_paths':4,'corruption_rejections':len(mutations),'uncalibrated_control':1,'rows_per_path':72,'browser_execution':False}))
