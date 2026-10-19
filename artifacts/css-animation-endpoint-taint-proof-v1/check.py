import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError("isolated nonoptimized Python required")
ROOT = Path(__file__).absolute().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def unique(pairs):
    d = {}
    for k, v in pairs:
        assert k not in d, 'duplicate JSON key'
        d[k] = v
    return d

def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)

def authenticate():
    assert not any(p.is_symlink() for p in [ROOT, *ROOT.parents]), 'source path symlink'
    for p in ROOT.rglob('*'):
        assert not p.is_symlink() and (p.is_file() or p.is_dir()), 'nonregular input'
    seal = read('FREEZE.json')
    assert sha(ROOT / 'MANIFEST.json') == seal['manifest_sha256'], 'manifest hash'
    assert sha(ROOT / 'check.py') == seal['checker_sha256'], 'checker hash'
    m = read('MANIFEST.json')
    expected = set(m) | {'FREEZE.json', 'MANIFEST.json'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == expected, 'closed file roster'
    dirs = {str(p) for n in expected for p in Path(n).parents if str(p) != '.'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_dir()} == dirs, 'closed directory roster'
    for n, h in m.items():
        assert not Path(n).is_absolute() and '..' not in Path(n).parts and str(Path(n)) == n, 'unsafe input name'
        assert sha(ROOT / n) == h, 'input hash: ' + n
    return m

def source_bindings():
    import difflib
    assert sha(ROOT/'proposal/MANIFEST.json')==read('proposal/FREEZE.json')['manifest_sha256']
    proposal=read('proposal/MANIFEST.json')
    for n,h in read('SOURCE-PINS.json').items():assert sha(ROOT/n)==h==proposal[n],n
    assert sha(ROOT/'native.patch')==proposal['native.patch']
    paths=['servo/components/style/properties_and_values/value.rs','servo/ports/geckolib/glue.rs','dom/animation/KeyframeEffect.cpp']
    regenerated=''
    for n in paths:
        old=(ROOT/'source/original'/n).read_text().splitlines(keepends=True)
        new=(ROOT/'source/candidate'/n).read_text().splitlines(keepends=True)
        regenerated+=''.join(difflib.unified_diff(old,new,fromfile='a/'+n,tofile='b/'+n))
    assert regenerated==(ROOT/'native.patch').read_text(),'exact candidate delta'
    rows=read('SOURCE-BINDINGS.json')
    for row in rows:
        raw=(ROOT/row['file']).read_bytes();body=raw[row['start_byte']:row['end_byte']]
        assert body.decode()==row['body'] and hashlib.sha256(body).hexdigest()==row['sha256']
        text=raw.decode();i=text.index(row['signature'],text.index(row['scope']) if row['scope'] else 0)
        assert len(text[:i].encode())==row['start_byte'] and row['body'].rstrip().endswith('}')
    assert sha(ROOT/'import-origin/MANIFEST.json')==read('import-origin/FREEZE.json')['manifest_sha256']
    record=read('IMPORT.json')
    assert sha(ROOT/record['retained'])==record['sha256']==read('import-origin/MANIFEST.json')['lean/Model.lean']
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    manifest=authenticate();bindings=source_bindings();audit=read('AUDITS.json')
    names=[]
    for module in audit['modules']:
        text=(ROOT/'lean'/(module+'.lean')).read_text()
        assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',text)
        names+=['EndpointTaint.'+n for n in re.findall(r'^theorem (\w+)',text,re.M)]
    assert names==audit['names']
    assert (ROOT/'lean/Audit.lean').read_text()=='import Witnesses\n'+'\n'.join('#print axioms '+n for n in names)+'\n'
    tool=read('TOOLCHAIN.json');lean=Path(tool['lean']);assert sha(lean)==tool['lean_sha256']
    for n,h in read('TOOLCHAIN-LIBRARY.json').items():assert sha(lean.parent.parent/n)==h,n
    out=args.output.resolve();source=ROOT.resolve()
    assert not out.exists() and not out.is_relative_to(source) and not source.is_relative_to(out),'fresh external output required'
    out.mkdir(parents=True)
    env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))}
    commands=[]
    def run(arguments,cwd,label):
        p=subprocess.run([str(lean),*arguments],cwd=cwd,env=dict(env,LEAN_PATH=str(cwd)),capture_output=True,text=True)
        (cwd/(label+'.log')).write_text(p.stdout+p.stderr)
        commands.append({'label':label,'command':[str(lean),*arguments],'cwd':str(cwd),'exit':p.returncode})
        assert p.returncode==0,label+': '+p.stdout+p.stderr
        return p.stdout
    for module in [*audit['modules'],'Audit']:
        (out/(module+'.lean')).write_bytes((ROOT/'lean'/(module+'.lean')).read_bytes())
    for module in audit['modules']:run(['-o',module+'.olean',module+'.lean'],out,module)
    log=run(['Audit.lean'],out,'axioms')
    reports=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",log)
    assert [n for n,_ in reports]==names
    for n,a in reports:assert {v.strip() for v in a.split(',') if v.strip()} <= {'propext','Quot.sound','Classical.choice'},n
    mutations=[];model=(ROOT/'lean/Model.lean').read_text()
    for mutant in [None,*read('MUTATIONS.json')]:
        name='baseline' if mutant is None else mutant['id'];d=out/name;d.mkdir();code=model
        if mutant:
            assert code.count(mutant['old'])==1
            code=code.replace(mutant['old'],mutant['new'])
        (d/'TaintValue.lean').write_bytes((ROOT/'lean/TaintValue.lean').read_bytes())
        (d/'Model.lean').write_text(code);(d/'Driver.lean').write_bytes((ROOT/'Driver.lean').read_bytes())
        for n in ['TaintValue','Model','Driver']:run(['-o',n+'.olean',n+'.lean'],d,n)
        observed=run(['--run','Driver.lean'],d,'observations').strip()
        expected='|'.join(['true']*8) if mutant is None else mutant['expected']
        assert observed==expected,(name,observed,expected)
        if mutant:assert observed!='|'.join(['true']*8)
        mutations.append({'id':name,'observed':observed,'expected':expected,'compiled':True})
    result={'inputs':len(manifest),'modules':audit['modules'],'axiom_reports':len(reports),'names':names,'source_bindings':len(bindings),
        'mutations':mutations,'commands':commands,'native_execution':False,'native_provider_publication_scheduler_admission':'OPEN',
        'payload_observational_quotient':'OPEN'}
    (out/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
