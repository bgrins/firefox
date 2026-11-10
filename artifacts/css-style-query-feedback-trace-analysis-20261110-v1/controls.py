import copy
import json
from pathlib import Path
import analyze as a
P=Path(__file__).resolve().parent

def fixture():
    rows=[]
    seq=0
    call=0
    depth=0
    def native(event,obj,**fields):
        nonlocal seq
        seq+=1
        values=dict(pid=42,seq=seq,style_call=call if depth else 0,style_depth=depth,event=event,object=obj,**fields)
        rows.append({'action':'process_output','data':'CSSFB '+' '.join(f'{k}={v}' for k,v in values.items())})
    for row in json.loads((P/'POSITIVE-QF.json').read_text()):
        rows.append(row)
        if '"phase":"armed-after"' not in row.get('data',''):continue
        n=call
        doc,anim,target,fallback,provider=[hex(base+n) for base in [0x100,0x200,0x300,0x400,0x500]]
        t=dict(animation_index=0,target=target,document=doc,timeline=fallback,next=provider,start_null=0,hold_null=1,pending=0,auto_align=0,rate=1)
        call+=1
        depth=1
        native('style',doc,edge='enter')
        native('rebind.enter',anim,**t)
        t.update(timeline=provider,start_null=1,hold_null=1,pending=1,auto_align=1)
        native('rebind.exit',anim,**t)
        native('style',doc,edge='exit')
        depth=0
        native('stale',provider,edge='enter')
        native('cache.enter',provider,document=doc,source='0x0',cached=0)
        native('cache.exit',provider,document=doc,source=target,cached=1,position=9000,range=12000)
        t['next']='0x0'
        native('ready.enter',anim,**t)
        native('align.enter',anim,**t)
        t.update(start_null=0,auto_align=0)
        native('align.exit',anim,**t)
        native('trigger.enter',anim,**t)
        t['pending']=0
        native('trigger.exit',anim,**t)
        native('ready.exit',anim,**t)
        native('stale',provider,edge='exit')
    return rows

def main():
    base=fixture()
    positive=a.analyze(base)
    assert positive['native_records']==56
    assert all(m['ready_restorations_at_style_depth_zero']==1 and m['ready_restorations_at_style_depth_nonzero']==0 and len(m['actual_rebind_transitions'])==1 for m in positive['modes'].values())
    inside=copy.deepcopy(base)
    exit_index=next(i for i,r in enumerate(inside) if 'event=style object=0x100 edge=exit' in r.get('data',''))
    exit_row=inside.pop(exit_index)
    stale_end=next(i for i,r in enumerate(inside) if 'event=stale object=0x500 edge=exit' in r.get('data',''))
    inside.insert(stale_end+1,exit_row)
    for r in inside[exit_index:stale_end+1]:
        r['data']=r['data'].replace('style_call=0 style_depth=0','style_call=1 style_depth=1')
    seq=0
    import re
    for r in inside:
        if r.get('data','').startswith('CSSFB'):
            seq+=1
            r['data']=re.sub(r'seq=[0-9]+ ', f'seq={seq} ', r['data'], count=1)
    detection=a.analyze(inside)
    assert detection['global_restorations_by_method_and_style_depth']['ready']=={'depth_zero':3,'depth_nonzero':1}
    cases={}
    def altered(name,needle,replacement):
        rows=copy.deepcopy(base)
        row=next(r for r in rows if needle in r.get('data',''))
        row['data']=row['data'].replace(needle,replacement)
        cases[name]=rows
    altered('sequence-gap','seq=2 ','seq=3 ')
    altered('wrong-object','event=rebind.exit object=0x200','event=rebind.exit object=0x999')
    altered('wrong-method-document','event=rebind.exit object=0x200 animation_index=0 target=0x300 document=0x100','event=rebind.exit object=0x200 animation_index=0 target=0x300 document=0x999')
    altered('wrong-style-depth','seq=2 style_call=1 style_depth=1','seq=2 style_call=1 style_depth=0')
    altered('duplicate-field','seq=2 ','seq=2 seq=2 ')
    altered('extra-field','seq=2 ','seq=2 extra=1 ')
    altered('nonfinite-rate','rate=1','rate=nan')
    altered('wrong-prefix','CSSFB pid=42 seq=1 ','PREFIX CSSFB pid=42 seq=1 ')
    first=next(r['data'] for r in base if r.get('data','').startswith('CSSFB'))
    altered('cap',first,'CSSFB pid=42 seq=1 event=cap limit=20000')
    altered('trace-error',first,'CSSFB pid=42 seq=1 event=trace-error reason=record-write')
    altered('wrong-QF-mode','"mode":"opposed"','"mode":"unknown"')
    altered('wrong-QF-phase','"phase":"sync-0"','"phase":"sync-99"')
    altered('QF-wrong-type','"pending":false','"pending":0')
    rows=copy.deepcopy(base)
    del rows[max(i for i,r in enumerate(rows) if r.get('data','').startswith('CSSFB'))]
    cases['unbalanced-terminal-scope']=rows
    rows=copy.deepcopy(base)
    for r in rows:
        if 'event=ready.' in r.get('data','') and 'object=0x200' in r['data']:
            r['data']=r['data'].replace('object=0x200','object=0x999')
    cases['wrong-active-animation']=rows
    rows=copy.deepcopy(base)
    next(r for r in rows if r['action']=='test_status')['status']='FAIL'
    cases['callback-failure']=rows
    altered('interleaved-process-fragments',first,first+' CSSFB pid=43 seq=1 style_call=1 style_depth=1 event=style object=0x1 edge=enter')
    outcomes={}
    for name,rows in cases.items():
        try:a.analyze(rows)
        except (ValueError,KeyError,TypeError) as e:outcomes[name]={'rejected':True,'reason':str(e)}
        else:raise AssertionError('accepted negative control: '+name)
    (P/'CONTROLS.json').write_text(json.dumps({'positive_fixture_records':positive['native_records'],'positive_ready_depth_zero_per_mode':1,'positive_inside_style_restoration_detected':True,'negative_controls':outcomes},indent=2)+'\n')
    print('PASS: synthetic four-mode trace and',len(cases),'negative controls')

if __name__=='__main__':main()
