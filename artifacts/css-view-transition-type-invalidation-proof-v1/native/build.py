import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('use -I -S without optimization')
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, subprocess
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if out==ROOT or ROOT in out.parents:raise RuntimeError('external output required')
out.mkdir(parents=True,exist_ok=False)
config=json.loads((ROOT/'TOOLCHAIN.json').read_text());clang=Path(config['clang'])
if hashlib.sha256(clang.read_bytes()).hexdigest()!=config['clang_sha256']:raise RuntimeError('compiler pin')
spec=importlib.util.spec_from_file_location('extract',ROOT/'source_extract.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
bindings=module.bindings()
if bindings!=json.loads((ROOT/'SOURCE-BINDINGS.json').read_text()):raise RuntimeError('source extraction mismatch')
bodies={b['name']:b['complete_text'] for b in bindings}
cases=json.loads((ROOT/'native/CASES.json').read_text())
spec=importlib.util.spec_from_file_location('case_schema',ROOT/'calibration.py');schema=importlib.util.module_from_spec(spec);spec.loader.exec_module(schema);schema.validate_cases(cases)
def serialize(rows):
    return ''.join(' '.join(map(str,[i,*c['setup'],len(c['actions']),*[v for op in c['actions'] for v in op]]))+'\n' for i,c in enumerate(rows))
(out/'INPUT.txt').write_text(serialize(cases));commands=[];env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_','CPATH','CPLUS_INCLUDE_PATH','LIBRARY_PATH'))}
def run(cmd,stdin=None):
    result=subprocess.run(cmd,cwd=out,env=env,input=stdin,text=True,capture_output=True)
    commands.append(dict(command=cmd,exit=result.returncode,stdout=result.stdout,stderr=result.stderr));(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if result.returncode:raise RuntimeError(result.stderr)
    return result.stdout
for variant in ['candidate','original','missing-notification','owner-guard','root-only-delivery','drop-partial']:
    template=(ROOT/'native/template.cpp').read_text()
    replacements={key:bodies[key.lower()] for key in ['ADD','DELETE','CLEAR','CHANGED','POST']}
    if variant=='original':
        for key in ['ADD','DELETE','CLEAR']:replacements[key]=bodies['original_'+key.lower()]
    if variant=='missing-notification':
        replacements['CHANGED']='void ViewTransition::TypesChanged() { mDocument->GetActiveViewTransition(); }'
    if variant=='owner-guard':
        needle='mDocument->GetActiveViewTransition() != this'
        if replacements['CHANGED'].count(needle)!=1:raise RuntimeError('mutation context')
        replacements['CHANGED']=replacements['CHANGED'].replace(needle,'(mDocument->GetActiveViewTransition(), false)')
    if variant=='root-only-delivery':
        needle='if(name&(1u<<j))cache[j]=expected(j,doc);'
        if template.count(needle)!=1:raise RuntimeError('mutation context')
        template=template.replace(needle,'if(j==0 && (name&1))cache[j]=expected(j,doc);')
    if variant=='drop-partial':template=template.replace('if(name==31)manager.pending=false;','manager.pending=false;')
    for key,value in replacements.items():template=template.replace('@@'+key+'@@',value)
    if '@@' in template:raise RuntimeError('unfilled source slot')
    source=out/(variant+'.cpp');source.write_text(template);exe=out/variant
    run([str(clang),'-std=c++20','-O0','-g',str(source),'-o',str(exe)])
    selected=cases if variant=='candidate' else cases[:18] if variant=='original' else cases
    raw=run([str(exe)],serialize(selected));(out/(variant+'.txt')).write_text(raw)
print(json.dumps({'complete':True,'cases':len(cases),'variants':6,'original_cases':18}))
