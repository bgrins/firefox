from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys
assert sys.flags.isolated and sys.flags.no_site
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output',type=Path,required=True)
p.add_argument('--olean',type=Path,required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True,exist_ok=False)
env = {k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))}
commands = []
def run(arguments, log, expected=0):
    cmd = [sys.executable,'-I','-S',*map(str,arguments)]
    r = subprocess.run(cmd,text=True,capture_output=True,env=env)
    (out/log).write_text(r.stdout+r.stderr)
    commands.append({'command':cmd,'exit':r.returncode,'log':log})
    assert (r.returncode==0) if expected==0 else (r.returncode!=0), (log,r.stdout+r.stderr)
    return r.stdout+r.stderr
raw = []
for mode,flags in [('debug',[]),('release',['--release']),('fast-release',['--fast','--release'])]:
    run([ROOT/'native/build.py','--output',out/mode,*flags],mode+'-build.log')
    run([ROOT/'native/check_states.py','--cases',ROOT/'CASES.json','--raw',out/mode/'raw.txt',
         '--output',out/(mode+'-states.json')],mode+'-states.log')
    raw.append((out/mode/'raw.txt').read_bytes())
assert raw[0]==raw[1]==raw[2]
run([ROOT/'native/build.py','--output',out/'plain-release','--release','--plain'],'plain-build.log')
plain=(out/'plain-release/raw.txt').read_text().splitlines()
assert plain==[line for line in raw[0].decode().splitlines() if line.split('|')[1]=='token']
run([ROOT/'native/model_compare.py','--raw',out/'fast-release/raw.txt','--olean',a.olean,
     '--output',out/'model'],'model.log')
mutants = []
for mutation in json.loads((ROOT/'MUTATIONS.json').read_text()):
    name = mutation['id'];folder = out/('mutation-'+name)
    run([ROOT/'native/build.py','--output',folder,'--mutation',name],name+'-build.log')
    error = run([ROOT/'native/check_states.py','--cases',ROOT/'CASES.json','--raw',folder/'raw.txt',
         '--output',folder/'CHECK.json'],name+'-rejection.log',1)
    assert 'AssertionError' in error and 'SyntaxError' not in error
    mutants.append({'id':name,'compiled':True,'source_state_or_slice_check':'REJECTED'})
    if name=='bulk-last-newline':
        old_rows=[line for line in (folder/'raw.txt').read_text().splitlines() if int(line.split('|')[0])<58]
        (folder/'old58.txt').write_text('\n'.join(old_rows)+'\n')
        run([ROOT/'native/check_states.py','--cases',ROOT/'predecessor/CASES-58-before-bulk.json','--raw',folder/'old58.txt',
             '--output',folder/'OLD58.json'],'bulk-prior58-survival.log')
for kind,tag,field in [('function-packed','exit',4),('slice-start','slice',2)]:
    lines = raw[0].decode().splitlines()
    selected = next(i for i,line in enumerate(lines)
                    if line.split('|')[1]==tag and (tag!='exit' or line.split('|')[5]=='function'))
    fields = lines[selected].split('|');fields[field]=str(int(fields[field])+1)
    lines[selected]='|'.join(fields)
    corrupt = out/(kind+'.txt');corrupt.write_text('\n'.join(lines)+'\n')
    error = run([ROOT/'native/check_states.py','--cases',ROOT/'CASES.json','--raw',corrupt,
         '--output',out/(kind+'.json')],kind+'-rejection.log',1)
    assert 'AssertionError' in error
receipt = {'status':'PASS','states':json.loads((out/'debug-states.json').read_text()),
           'model':json.loads((out/'model/CHECK.json').read_text()),
           'modes':['debug','release','fast_match_byte release'],
           'raw_sha256':hashlib.sha256(raw[0]).hexdigest(),'mutants':mutants,'uninstrumented_token_preservation':True,
           'comparator_corruptions':['function-packed','slice-start'],'commands':commands}
(out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='commands'}))
