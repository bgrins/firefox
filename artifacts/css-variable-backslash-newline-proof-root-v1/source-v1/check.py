import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without -O/-OO')
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, os, re, stat, subprocess
ROOT=Path(__file__).resolve().parent
def require(value, message):
    if not value: raise RuntimeError(message)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def unique(pairs):
    result={}
    for key,value in pairs:
        require(key not in result, 'duplicate JSON key: '+key)
        result[key]=value
    return result
def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)
def authenticate():
    for name in ['FILES.json','FREEZE.json']:
        require(stat.S_ISREG((ROOT/name).lstat().st_mode), 'nonregular root seal: '+name)
    manifest=read_json(ROOT/'FILES.json')
    require(isinstance(manifest,list) and manifest, 'invalid manifest')
    expected_files={'FILES.json','FREEZE.json'};expected_dirs={''}
    for row in manifest:
        require(isinstance(row,dict) and set(row)=={'path','bytes','sha256'}, 'invalid manifest row')
        name=row['path'];require(isinstance(name,str), 'invalid manifest path')
        path=PurePosixPath(name)
        require(name==path.as_posix() and bool(path.parts) and not path.is_absolute()
            and all(part not in ('','.','..') for part in path.parts), 'invalid manifest path')
        require(name not in expected_files, 'duplicate / reserved manifest path')
        require(type(row['bytes']) is int and row['bytes']>=0, 'invalid input size')
        require(isinstance(row['sha256'],str) and re.fullmatch('[0-9a-f]{64}',row['sha256']), 'invalid digest')
        expected_files.add(name)
        for parent in path.parents:
            if str(parent)!='.':expected_dirs.add(str(parent))
    actual_files=set();actual_dirs={''}
    def visit(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                rel=Path(entry.path).relative_to(ROOT).as_posix()
                mode=entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode):
                    require(rel in expected_dirs, 'unexpected directory: '+rel)
                    actual_dirs.add(rel);visit(entry.path)
                else:
                    require(stat.S_ISREG(mode), 'nonregular entry: '+rel)
                    actual_files.add(rel)
    visit(ROOT)
    require(actual_files==expected_files, 'file roster mismatch')
    require(actual_dirs==expected_dirs, 'directory roster mismatch')
    for row in manifest:
        path=ROOT/row['path']
        require(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'], 'input mismatch: '+row['path'])
    freeze=read_json(ROOT/'FREEZE.json')
    require(freeze['FILES_sha256']==sha(ROOT/'FILES.json'), 'manifest seal mismatch')
    require(freeze['check_sha256']==sha(ROOT/'check.py'), 'checker seal mismatch')
    return manifest
initial_manifest=authenticate()
config=read_json(ROOT/'TOOLCHAIN.json')
for name in ['lean','rustc']:
    require(sha(Path(config[name]))==config[name+'_sha256'], 'toolchain pin: '+name)
predecessor=read_json(ROOT/'PREDECESSOR.json')
require(sha(ROOT/'lean/Span.lean')==predecessor['Span_sha256'], 'predecessor source')
for row in read_json(ROOT/'SOURCE-PINS.json'):
    require(sha(ROOT/row['path'])==row['sha256'], 'source pin')
for row in read_json(ROOT/'SOURCE-BINDINGS.json'):
    source=(ROOT/row['source']).read_bytes();body=source[row['offset']:row['offset']+row['bytes']]
    require(body==row['complete_text'].encode() and hashlib.sha256(body).hexdigest()==row['sha256'], 'source body binding')
for name in ['tokenizer.rs','serializer.rs']:
    require((ROOT/'source'/name).read_bytes()==(ROOT/'vendor/cssparser/src'/name).read_bytes(), 'native dependency source')
review=read_json(ROOT/'evidence/native-review/FILES.json')
for name in ['baseline','tested','head','upstream']:
    require(sha(ROOT/'evidence/native-review'/(name+'.jsonl'))==review['native-receipts/'+name+'.jsonl'], 'review trace binding')
admission=read_json(ROOT/'SOURCE-REVIEW.json')
for name in ['FILES','FREEZE','REPORT']:
    suffix='.md' if name=='REPORT' else '.json'
    require(sha(ROOT/'evidence/native-review'/(name+suffix))==admission[name+'_sha256'], 'accepted source-review identity')
for file,variant in admission['source_variants'].items():
    native=read_json(ROOT/'evidence/native-review'/(variant+'-bindings.json'))
    require(sha(ROOT/'evidence/native-review'/(variant+'-bindings.json'))==review['native-receipts/'+variant+'-bindings.json'], 'native extraction receipt')
    for name,marker in [('VariableValue::parse','    pub fn parse(\n'),('parse_declaration_value','fn parse_declaration_value('),('parse_declaration_value_block','fn parse_declaration_value_block(')]:
        binding=next(row for row in read_json(ROOT/'SOURCE-BINDINGS.json') if row['name']==file+':'+name)
        actual=[row for row in native if row['marker']==marker]
        require(len(actual)==1 and actual[0]['complete'] and actual[0]['sha256']==binding['sha256'], 'compiled complete constructor/scanner binding')
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
require(out!=ROOT and ROOT not in out.parents, 'external output required')
out.mkdir(parents=True,exist_ok=False)
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))};commands=[]
def run(command,expected=0,extra_env=None):
    result=subprocess.run(command,cwd=out,env=extra_env or env,text=True,capture_output=True)
    commands.append({'command':command,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    require(result.returncode==expected,'command result: '+str(command))
    return result
run([sys.executable,'-I','-S',str(ROOT/'native/build_projection.py'),'--output',str(out/'native')])
projection=(out/'native/PROJECTION.jsonl').read_text()
require(projection==(ROOT/'evidence/PROJECTION.jsonl').read_text(),'fresh tokenizer projection')
rows=[json.loads(line) for line in projection.splitlines()];cases=read_json(ROOT/'native/CASES.json');kind=read_json(ROOT/'native/KIND-MAP.json')
require(len(rows)==len(cases)==56,'calibration roster')
source_cases=[]
for index,(row,case) in enumerate(zip(rows,cases)):
    require(row['index']==index,'projection ordering');tokens=row['tokens'];joined=b'';parts=[]
    for n,token in enumerate(tokens):
        raw=bytes.fromhex(token['raw_hex']);require(raw,'nonempty token span');joined+=raw
        require(token['kind'] in kind and type(token['backslash']) is bool,'exact token role/class')
        if token['kind']=='WhiteSpace':
            require(all(b in [9,10,12,13,32] for b in raw),'raw CSS whitespace')
            require(n==0 or tokens[n-1]['kind']!='WhiteSpace','coalescing')
        if token['backslash']:
            require(token['kind']=='Other' and raw==b'\\','backslash role')
            require(n+1<len(tokens) and tokens[n+1]['kind']=='WhiteSpace' and bytes.fromhex(tokens[n+1]['raw_hex'])[0] in [10,12,13],'backslash follower')
        parts.append('⟨.'+kind[token['kind']]+',['+','.join(map(str,raw))+'],'+str(token['backslash']).lower()+'⟩')
    require(joined==case['css'].encode(),'outer raw partition')
    require(not tokens or tokens[0]['kind']!='WhiteSpace','initial readiness')
    source_cases.append('['+','.join(parts)+']')
generated='import ProtectedSpan\nnamespace ProtectedCalibration\ndef cases : List (List ProtectedSpan.Token) := [\n'+',\n'.join(source_cases)+'\n]\nend ProtectedCalibration\n'
require(generated==(ROOT/'lean/CalibrationCases.lean').read_text(),'model input binding')
run([sys.executable,'-I','-S',str(ROOT/'compile.py'),'--output',str(out/'lean'),'Audit','CalibrationDriver'])
compiles=read_json(out/'lean/COMMANDS.json');audit=next(row['stdout'] for row in compiles if row['command'][-1].endswith('/Audit.lean'));(out/'AUDIT.txt').write_text(audit)
names=read_json(ROOT/'AUDIT-NAMES.json');found=re.findall(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",audit)
require([row[0] for row in found]==names,'theorem audit roster')
for _,_,axioms in found:require(set(axioms.split(', '))<={'','propext','Classical.choice','Quot.sound'},'unapproved axiom')
lean_env={**env,'LEAN_PATH':str(out/'lean')}
model=run([config['lean'],'--root='+str(ROOT/'lean'),'--run',str(ROOT/'lean/CalibrationDriver.lean')],extra_env=lean_env)
require(not model.stderr,'model diagnostics');(out/'CALIBRATION.txt').write_text(model.stdout)
models=model.stdout.splitlines();require(len(models)==56,'model row count')
variants={name:[json.loads(line) for line in (ROOT/'evidence/native-review'/(name+'.jsonl')).read_text().splitlines()] for name in ['tested','head','upstream','baseline']}
for index,line in enumerate(models):
    parts=line.split('|');require(len(parts)==4 and int(parts[0])==index,'model row format')
    for variant,column in [('tested',1),('head',2),('upstream',2),('baseline',3)]:
        require(parts[column]==variants[variant][index]['css_hex'],'native constructor calibration: '+variant+':'+str(index))
mutants={}
for mutation in read_json(ROOT/'LEAN-MUTATIONS.json'):
    text=(ROOT/'lean'/(mutation['module']+'.lean')).read_text();require(text.count(mutation['old'])==1,'mutation uniqueness')
    target=out/'mutants'/mutation['id'];target.mkdir(parents=True);path=target/(mutation['module']+'.lean');path.write_text(text.replace(mutation['old'],mutation['new']))
    result=run([config['lean'],'--root='+str(target),str(path)],expected=1,extra_env=lean_env)
    require('error:' in result.stdout and any(marker in result.stdout for marker in ['unsolved goals','Tactic','Type mismatch','tactic failed']),'semantic proof failure')
    mutants[mutation['id']]=result.returncode
require(authenticate()==initial_manifest,'source capsule changed')
summary={'complete':True,'audits':len(names),'compiled_modules':len(compiles),'source_bindings':len(read_json(ROOT/'SOURCE-BINDINGS.json')),'tokenizer_cases':56,'native_constructor_comparisons':224,'lean_mutants':mutants,'scope':'conditional raw-span/metadata and standalone preservation decision; no full serialization or arbitrary Rust translation'}
(out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
