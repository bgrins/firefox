import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('use -I -S without optimization')
sys.dont_write_bytecode = True
import importlib.util, json

def validate_cases(cases):
    def require(ok,message):
        if not ok:raise RuntimeError(message)
    require(type(cases) is list,'case list')
    for case in cases:
        require(type(case) is dict and set(case)=={'setup','actions','label'},'case schema')
        setup=case['setup'];actions=case['actions']
        require(type(setup) is list and len(setup)==6 and all(type(x) is int for x in setup),'setup schema')
        require(setup[0] in range(3) and all(x in range(2) for x in setup[1:4]) and all(x in range(4) for x in setup[4:]),'setup range')
        require(type(actions) is list and len(actions) in (2,3),'actions schema')
        require(type(case['label']) is str,'case label')
        for operation in actions:
            require(type(operation) is list and len(operation)==4 and all(type(x) is int for x in operation),'action framing')
            tag,actor,name,error=operation
            require(tag in range(4) and actor in range(2),'action tag/actor')
            if tag==0:require(name in range(2) and error in range(3),'add range')
            if tag==1:require(name in range(2) and error in range(2),'delete range')
            if tag==2:require(name==0 and error in range(2),'clear range')
            if tag==3:require(actor==0 and name in (1,30,31) and error==0,'delivery range')
    expected=[]
    operations=[('add',0,0),('delete',1,1),('clear',2,1),('add-existing',0,1),('delete-absent',1,0),('clear-empty',2,0)]
    for phase in ['synchronous','ready']:
        for name,tag,initial in operations:expected.append(dict(setup=[0,1,1,1,initial,0],actions=[[tag,0,0,0],[3,0,31,0]],label='wpt-'+phase+'-'+name))
    for owner in [2,1]:
        for name,tag,initial in operations[:3]:expected.append(dict(setup=[owner,1,1,1,initial,2],actions=[[tag,0,0,0],[3,0,31,0]],label='wpt-old-'+str(owner)+'-'+name))
    require(cases[:18]==expected,'WPT operation/owner projection changed')
    controls=[]
    for actor in range(2):
        for name in range(2):
            for error in range(3):controls.append([0,actor,name,error])
    for actor in range(2):
        for name in range(2):
            for error in range(2):controls.append([1,actor,name,error])
    for actor in range(2):
        for error in range(2):controls.append([2,actor,0,error])
    for owner in range(3):
        for root in range(2):
            for composed in range(2):
                for pres in range(2):
                    for first in range(4):
                        for second in range(4):
                            for operation in controls:
                                expected.append(dict(setup=[owner,root,composed,pres,first,second],
                                    actions=[operation,[3,0,31,0]],label='single-error-owner-presentation'))
    history_actions=[[0,0,0,0],[0,0,1,0],[1,0,0,0],[2,0,0,0],[0,1,0,0],
        [1,1,0,0],[0,0,0,2],[3,0,1,0],[3,0,30,0],[3,0,31,0]]
    for owner in range(3):
        for initial in range(2):
            for a in history_actions:
                for b in history_actions:
                    for c in history_actions:
                        expected.append(dict(setup=[owner,1,1,1,initial,2],actions=[a,b,c],label='three-action-history'))
    require(len(cases)==15234 and cases==expected,'exact advertised case roster')

def validate(root, native, lean):
    def require(ok,message):
        if not ok:raise RuntimeError(message)
    spec=importlib.util.spec_from_file_location('oracle',root/'oracle.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    cases=json.loads((root/'native/CASES.json').read_text())
    validate_cases(cases)
    oracle=m.rows(cases)
    candidate=(native/'candidate.txt').read_text()
    require(candidate==oracle==lean,'native / independent set oracle / Lean discrepancy')
    rows=candidate.splitlines();original=(native/'original.txt').read_text().splitlines()
    require(len(original)==18,'historical source calibration count')
    style_diff=[]
    for i,(old,new) in enumerate(zip(original,rows)):
        old_style=old.split('|')[-1].split(',')[5:]
        new_style=new.split('|')[-1].split(',')[5:]
        if old_style!=new_style:style_diff.append(i)
    require(style_diff==[0,1,2,6,7,8],'six active mutation cache discrepancies')
    mutants={}
    for variant in ['missing-notification','owner-guard','root-only-delivery','drop-partial']:
        changed=(native/(variant+'.txt')).read_text().splitlines()
        require(len(changed)==len(rows),'mutant row count')
        count=sum(a!=b for a,b in zip(rows,changed))
        require(count>0,'native mutant not distinguished: '+variant);mutants[variant]=count
    return dict(cases=len(cases),snapshots=sum(1+len(c['actions']) for c in cases),
        historical_source_cases=18,historical_source_style_differences=style_diff,native_mutants=mutants,
        subjects=5,scope='source-extracted control with substituted providers; cache resolver/delivery are calibration implementations, not extracted Stylo')
