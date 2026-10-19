import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
args=argparse.ArgumentParser();args.add_argument('--lean',required=True);args.add_argument('--manifest-sha',required=True);args=args.parse_args()
assert hashlib.sha256((ROOT/'MANIFEST.json').read_bytes()).hexdigest()==args.manifest_sha
m=json.loads((ROOT/'MANIFEST.json').read_text())
actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and 'build' not in p.relative_to(ROOT).parts}
assert actual in [set(m['files'])|{'MANIFEST.json'},set(m['files'])|{'MANIFEST.json','FREEZE.json'}]
for name,digest in m['files'].items():
    path=Path(name)
    assert not path.is_absolute() and '..' not in path.parts
    assert not (ROOT/path).is_symlink() and (ROOT/path).resolve().is_relative_to(ROOT)
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,name
lean=Path(args.lean).resolve();tool=json.loads((ROOT/'TOOL.json').read_text())
assert hashlib.sha256(lean.read_bytes()).hexdigest()==tool['sha256']
assert subprocess.check_output([lean,'--version'],text=True).strip()==tool['version']
out=ROOT/'build';out.mkdir(exist_ok=True);env=dict(os.environ,LEAN_PATH=str(out))
modules={p.stem:p for p in (ROOT/'lean').glob('*.lean')};done=[];commands=[]
def run(name,command):
    result=subprocess.run(list(map(str,command)),env=env,capture_output=True,text=True)
    (out/(name+'.log')).write_text(result.stdout+result.stderr)
    commands.append({'name':name,'exit':result.returncode})
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert result.returncode==0,(name,result.stdout,result.stderr)
    return result.stdout
while len(done)<len(modules):
    progress=False
    for name,path in modules.items():
        if name in done:continue
        deps=re.findall(r'^import (\w+)',path.read_text(),re.M)
        assert all(dep in modules or dep in ['Std','Lean'] for dep in deps)
        if any(dep in modules and dep not in done for dep in deps):continue
        assert not re.search(r'\b(sorry|axiom|admit|native_decide|bv_decide)\b',path.read_text()),name
        run(name,[lean,'-o',out/(name+'.olean'),path]);done.append(name);progress=True
    assert progress
count=0
for name,path in modules.items():
    names=[]; namespaces=[]
    for line in path.read_text().splitlines():
        opening=re.match(r'^namespace ([\w.]+)',line)
        ending=re.match(r'^end(?: ([\w.]+))?$',line)
        if opening:namespaces.append(opening.group(1))
        elif ending and namespaces:namespaces.pop()
        theorem=re.match(r'^(?:@\[[^]]*\]\s*)?theorem ([\w.]+)',line)
        if theorem:names.append('.'.join(namespaces+[theorem.group(1)]))
    theorems=names
    audit=out/(name+'Axioms.lean');audit.write_text('import '+name+'\n'+'\n'.join('#print axioms '+t for t in theorems)+'\n')
    report=run(name+'Axioms',[lean,audit]);assert 'sorryAx' not in report;count+=len(theorems)
    for group in re.findall(r'depends on axioms: \[([^]]*)\]',report):assert set(map(str.strip,group.split(','))) <= {'propext','Classical.choice','Quot.sound',''}
binding=json.loads((ROOT/'SOURCE-BINDING.json').read_text())
for name,digest in binding['files'].items():
    assert hashlib.sha256((ROOT/'source'/name).read_bytes()).hexdigest()==digest
for record in binding['definitions']:
    source=(ROOT/'source'/record['source']).read_text()
    assert source.count(record['marker'])==1
    start=source.index(record['marker']);end=source.index(record['end_marker'],start)+len(record['end_marker'])
    body=source[start:end]
    assert hashlib.sha256(body.encode()).hexdigest()==record['body_sha256']
    assert (ROOT/'source'/(record['name']+'.cpp')).read_text()==body+'\n'
driver = run('counterexample-driver',[lean,'--run',ROOT/'lean/LFComplexStreamDriver.lean'])
rows=[json.loads(line) for line in driver.splitlines()]
queries=(ROOT/'evidence/provider-inputs.txt').read_text().splitlines()
answers=(ROOT/'evidence/provider-raw.txt').read_text().splitlines()
assert len(rows)==4 and len(queries)==len(answers)==3
for row,query,answer in zip(rows[:3],queries,answers,strict=True):
    width,word,line,script,length,*units=map(int,query.split())
    assert (width,word,line,script)==(16,0,0,0) and len(units)==length
    assert row=={'units':units,'values':list(map(int,answer))}
for variant in ['original','candidate']:
    raw=(ROOT/'evidence'/('stream-'+variant+'.raw.txt')).read_text()
    for key,case in [('whole','ahom-whole'),('before','ahom-before-lf'),('after','ahom-after-lf')]:
        record=next(line for line in raw.splitlines() if line.startswith(case+' BREAKS ')).split()
        assert rows[3][key]==list(map(int,record[4]))
result={'files':len(m['files']),'modules':len(done),'theorem_reports':count,'manifest_sha256':args.manifest_sha,
        'status':'Complete Lean Append/reset counterexample and retained actual provider/native bridge agree; no native rebuild or browser claim',
        'driver':rows}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
