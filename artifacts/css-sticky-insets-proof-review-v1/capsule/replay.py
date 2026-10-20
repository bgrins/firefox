import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
MODULES=['StickyAxis','StickyPosition','StickyWritingMode','StickyGeometry','StickyRanges',
         'StickyNumeric','StickyContinuations','StickyMachineGeometry','StickyConsumers','StickyPipeline','StickyChallenges']
VARIANTS=['original','auto-only','writing-only','combined']

def decode(text):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('duplicate key '+k)
            result[k]=v
        return result
    return json.loads(text,object_pairs_hook=pairs)

def load_json(path):
    return decode(Path(path).read_text())

def same(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b

def need(ok,message):
    if not ok:raise RuntimeError(message)

def parse_rows(text,cases):
    result=[decode(line) for line in text.splitlines()]
    need(len(result)==len(cases),'incomplete row roster')
    need(all(type(r)==dict and type(r.get('id')) is int for r in result),'row/id type')
    need([r['id'] for r in result]==list(range(len(cases))),'row identities')
    return result

def check_rows(cases,actual,variant):
    from oracle import observe,expected_trace
    need(len(cases)==len(actual),'comparison roster')
    for c,r in zip(cases,actual):
        e=observe(c,variant);e['trace']=expected_trace(c,variant)
        need(same(r,e),variant+' row mismatch '+str(c['id']))

def run(output,tools):
    output=Path(output)
    sys.path.insert(0,str(ROOT/'native'))
    from generate import generate
    from generate_mode import rust_source
    from corpus import cases,input_text,MODE_FLAGS,MODES,mode_flags
    from oracle import observe,expected_trace
    from mutations import MUTATIONS,mutated
    from calibrate import lean_source
    spec=importlib.util.spec_from_file_location('source_extract',ROOT/'source_extract.py')
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    bindings={v:source.selected(v) for v in VARIANTS}
    need(same(bindings,load_json(ROOT/'SOURCE-BINDINGS.json')),'source extraction changed')
    (output/'SOURCE-BINDINGS.json').write_text(json.dumps(bindings,indent=2)+'\n')
    records=[]
    env=os.environ.copy();env.pop('LEAN_SYSROOT',None);env.pop('LEAN_SRC_PATH',None)
    env['LEAN_PATH']=str(output/'lean');env['PYTHONDONTWRITEBYTECODE']='1'
    (output/'lean').mkdir()
    def command(cmd,stem,stdin=None,expected=0):
        with (output/(stem+'.log')).open('w') as log:
            p=subprocess.run(cmd,input=stdin,text=True,stdout=log,stderr=subprocess.STDOUT,cwd=output,env=env)
        records.append({'argv':cmd,'exit':p.returncode,'log':stem+'.log'})
        (output/'COMMANDS.json').write_text(json.dumps(records,indent=2)+'\n')
        if expected is not None:need(p.returncode==expected,'command failed: '+stem)
        return p.returncode
    for name in MODULES:
        command([tools['lean'],'--root='+str(ROOT/'lean'),'-o',str(output/'lean'/(name+'.olean')),str(ROOT/'lean'/(name+'.lean'))],'lean-'+name)
    audits=load_json(ROOT/'AUDITS.json')
    (output/'Audit.lean').write_text('import StickyChallenges\n'+'\n'.join('#print axioms '+n for n in audits)+'\n')
    command([tools['lean'],str(output/'Audit.lean')],'axioms')
    axiom_text=(output/'axioms.log').read_text()
    need('sorryAx' not in axiom_text,'sorry axiom')
    seen=re.findall(r"^'([^']+)' (?:depends on axioms:|does not depend on any axioms)",axiom_text,re.M)
    need(seen==audits,'closed axiom roster')
    allowed={'propext','Quot.sound','Classical.choice'}
    found=set()
    for body in re.findall(r'depends on axioms:\s*\[([^]]*)\]',axiom_text):found.update(x.strip() for x in body.split(',') if x.strip())
    need(found<=allowed,'unexpected axiom')
    rows=cases();need(same(rows,load_json(ROOT/'native/CASES.json')),'case roster changed')
    data=input_text(rows);(output/'INPUT.txt').write_text(data)
    historical=load_json(ROOT/'inputs/ORACLE-ROWS.json')
    native_results={};expected_failure_counts={'original':186,'auto-only':168,'writing-only':18,'combined':0}
    def cpp(source_text,stem):
        file=output/(stem+'.cpp');file.write_text(source_text)
        command([tools['clang'],'-std=c++20','-O0','-fsanitize=undefined','-fno-sanitize-recover=all',str(file),'-o',str(output/stem)],stem+'-compile')
        command([str(output/stem)],stem+'-rows',data)
        parsed=parse_rows((output/(stem+'-rows.log')).read_text(),rows)
        return parsed
    for variant in VARIANTS:
        actual=cpp(generate(variant,'driver.cpp'),'native-'+variant)
        check_rows(rows,actual,variant)
        failures=0
        for c,r,h in zip(rows[:len(historical)],actual,historical):
            axis=c['axis'];measured=r['position'][axis]-c['scroll'][axis]
            need(measured==h['predicted_variants'][variant]*60,'historical measured projection')
            failures+=measured!=h['expected']*60
        need(failures==expected_failure_counts[variant],'historical attribution')
        native_results[variant]={'rows':len(actual),'historical_failures':failures}
        if variant=='combined':combined=actual
    modefile=output/'mode-provider.rs';modefile.write_text(rust_source())
    command([tools['rustc'],'--edition=2021','--cfg','feature="gecko"',str(modefile),'-o',str(output/'mode-provider')],'mode-rust-compile')
    command([str(output/'mode-provider')],'mode-rust')
    modes=[decode(line) for line in (output/'mode-rust.log').read_text().splitlines()]
    expected_modes=[[m,d,o,mode_flags(MODES[m],d,o)] for m in range(5) for d in range(2) for o in range(3)]
    need(same(modes,expected_modes),'actual Rust mode provider')
    modefile=output/'mode-driver.cpp';modefile.write_text(generate('combined','mode_driver.cpp'))
    command([tools['clang'],'-std=c++20','-O0','-fsanitize=undefined','-fno-sanitize-recover=all',str(modefile),'-o',str(output/'mode-driver')],'mode-cpp-compile')
    command([str(output/'mode-driver')],'mode-cpp')
    encoded=[decode(line) for line in (output/'mode-cpp.log').read_text().splitlines()]
    need(len(encoded)==256 and [r[0] for r in encoded]==list(range(256)),'raw mode roster')
    for raw,vertical,bs,be,ins,ine in encoded:
        need(vertical==raw%2 and bs^2==be and ins^2==ine,'raw side opposite consistency')
    for m,d,o,raw in modes:
        rtl=0 if m in [1,2] and o==1 else d
        block_end=[2,3,1,3,1][m]
        inline_end=(3 if rtl else 1) if m==0 else (2 if rtl else 0) if m==4 else (0 if rtl else 2)
        need(encoded[raw]==[raw,int(m!=0),block_end^2,block_end,inline_end^2,inline_end],'CSS mapping')
    (output/'Calibration.lean').write_text(lean_source(rows))
    command([tools['lean'],str(output/'Calibration.lean')],'calibration')
    calibrated=[decode(line) for line in (output/'calibration.log').read_text().splitlines()]
    need(len(calibrated)==len(rows)*2,'Lean raw bridge roster')
    for index,(c,r) in enumerate(zip(rows,combined)):
        for axis in [0,1]:
            stick,contain=r['current']
            expected=[c['id'],r['position'][axis],r['position'][axis],stick[axis],stick[axis]+stick[axis+2],contain[axis],contain[axis]+contain[axis+2]]
            need(same(calibrated[index*2+axis],expected),'Lean/source raw bridge '+str(c['id']))
    mutation_results=[]
    for name in MUTATIONS:
        actual=cpp(mutated(name),'mutant-'+name)
        differences=[]
        for c,r,good in zip(rows,actual,combined):
            need(type(r)==dict and r.keys()==good.keys(),'mutant fields')
            diff={k:{'actual':r[k],'expected':good[k]} for k in good if not same(r[k],good[k])}
            if diff:differences.append({'id':c['id'],'differences':diff})
        semantic=[d for d in differences if set(d['differences'])!={'trace'}]
        need(semantic,'no semantic mutation witness '+name)
        result={'name':name,'rows':len(actual),'semantic_rows':len(semantic),'different_rows':len(differences),'first_witness':semantic[0]}
        mutation_results.append(result)
    (output/'MUTATIONS.json').write_text(json.dumps(mutation_results,indent=2)+'\n')
    lean_mutants=[('auto','StickyAxis','if active i then','if i.near.isSome && i.far.isSome then','normalization_refines'),
      ('mode','StickyWritingMode','| .sidewaysLr => if direction then .bottom else .top','| .sidewaysLr => if direction then .top else .bottom','css_provider_refines'),
      ('range','StickyRanges','normal-stickNear','stickNear-normal','position_range_agreement')]
    lean_mutation_results=[]
    for name,module,before,after,theorem in lean_mutants:
        text=(ROOT/'lean'/(module+'.lean')).read_text();need(text.count(before)>=1,'Lean mutation anchor')
        if name=='auto':text=text.replace(before,after,1)
        else:text=text.replace(before,after)
        target=output/('LeanMutant-'+name+'.lean');target.write_text(text)
        rc=command([tools['lean'],str(target)],'lean-mutant-'+name,expected=None)
        log=(output/('lean-mutant-'+name+'.log')).read_text()
        need(rc!=0 and 'error:' in log and not any(x in log for x in ['unexpected token','unknownIdentifier','unknown identifier']),'Lean mutant failed for wrong reason')
        lean_mutation_results.append({'name':name,'exit':rc,'anchor':before,'claimed_target':theorem})
    result={'status':'pass','modules':len(MODULES),'audits':len(audits),'axioms':sorted(found),
      'extraction_items_per_variant':{v:len(bindings[v]) for v in VARIANTS},'native':native_results,
      'rust_mode_rows':len(modes),'cpp_raw_mode_rows':len(encoded),'lean_native_rows':len(calibrated),
      'native_mutants':mutation_results,'lean_mutants':lean_mutation_results,
      'limitations':'Finite compiled source agreement plus conditional universal models; provider/machine/compiler/lifecycle admissions remain explicit.'}
    (output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
