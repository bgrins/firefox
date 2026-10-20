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
def serialize(rows):
    return ''.join(' '.join(map(str,[i,c['kind'],len(c['initial']),*c['initial'],len(c['ops']),*[v for op in c['ops'] for v in op]]))+'\n' for i,c in enumerate(rows))
(out/'INPUT.txt').write_text(serialize(cases));commands=[];env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_','CPATH','CPLUS_INCLUDE_PATH','LIBRARY_PATH'))}
def run(cmd,stdin=None):
    result=subprocess.run(cmd,cwd=out,env=env,input=stdin,text=True,capture_output=True)
    commands.append(dict(command=cmd,exit=result.returncode,stdout=result.stdout,stderr=result.stderr));(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if result.returncode:raise RuntimeError(result.stderr)
    return result.stdout
for variant in ['candidate','original','reverse-order','omit-native-delete']:
    template=(ROOT/'native/template.cpp').read_text()
    startup=bodies['startup_original' if variant=='original' else 'startup']
    init=startup[startup.index('  nsTArray<RefPtr<nsAtom>> types;'):startup.index('  RefPtr transition =')]
    if variant=='reverse-order':
        needle='types.AppendElement(std::move(atom));'
        if init.count(needle)!=1:raise RuntimeError('mutation context')
        init=init.replace(needle,'types.insert(types.begin(), std::move(atom));')
    replacements={'ATOM_EQUALS':bodies['atom_equals'],'HASH_INSERT':bodies['hash_count_insert'],'CONSTRUCTOR':bodies['constructor'],'TYPES':bodies['types'],'ADD':bodies['add'],'DELETE':bodies['delete'],'CLEAR':bodies['clear'],'INITIALIZE':init,'BRIDGE':bodies['selector_bridge'],'VALIDITY':bodies['selector_validity']}
    if variant=='omit-native-delete':
        needle='mTransition->GetTypeList().RemoveElement(atom);'
        if replacements['DELETE'].count(needle)!=1:raise RuntimeError('mutation context')
        replacements['DELETE']=replacements['DELETE'].replace(needle,'(void)atom;')
    for key,value in replacements.items():template=template.replace('@@'+key+'@@',value)
    if '@@' in template:raise RuntimeError('unfilled source slot')
    source=out/(variant+'.cpp');source.write_text(template);exe=out/variant
    flags=['-std=c++20','-O0','-g']
    run([str(clang),*flags,str(source),'-o',str(exe)])
    selected=cases if variant=='candidate' else cases[:21]
    raw=run([str(exe)],serialize(selected));(out/(variant+'.txt')).write_text(raw)
print(json.dumps({'complete':True,'cases':len(cases),'variants':4,'original_cases':21,'mutant_cases':21}))
