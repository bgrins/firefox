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

def sources():
    for name, record in read('IMPORTS.json').items():
        manifest_path = 'provenance/' + record['capsule'] + '/MANIFEST.json'
        freeze = read('provenance/' + record['capsule'] + '/FREEZE.json')
        assert sha(ROOT / manifest_path) == freeze['manifest_sha256']
        manifest = read(manifest_path)
        assert manifest[record['input']] == record['sha256'] == sha(ROOT / name)
    transfer = read('SOURCE-TRANSFER.json')
    for name, expected in transfer['pins'].items():
        assert sha(ROOT / name) == expected
    before = (ROOT / 'source/map-before.rs').read_text()
    after = (ROOT / 'source/map-after.rs').read_text()
    old = 'if self.get(name) == value.as_ref() {'
    new = 'if can_deduplicate_values(self.get(name), value.as_ref()) {'
    assert before.count(old) == 1 and before.replace(old,new) == after
    before = (ROOT / 'source/cascade-before.rs').read_text()
    after = (ROOT / 'source/cascade-after.rs').read_text()
    old = 'if let Some(existing_value) = existing_value.as_universal() {\n                    return existing_value != value;'
    new = 'if let Some(existing_unparsed) = existing_value.as_universal() {\n                    return existing_value.attr_tainted != value.is_attr_tainted()\n                        || existing_unparsed != value;'
    assert before.count(old) == 1 and before.replace(old,new) == after
    taint = read('provenance/css-custom-properties-map-taint-proof-v1/MANIFEST.json')
    composition = read('provenance/css-custom-properties-map-composition-proof-v1/MANIFEST.json')
    assert sha(ROOT / 'source/map-before.rs') == composition['imports/count/source/combined.rs'] == composition['imports/iterator/source/combined.rs'] == taint['source/original/servo/components/style/custom_properties_map.rs']
    assert sha(ROOT / 'source/map-after.rs') == taint['source/candidate/servo/components/style/custom_properties_map.rs']
    for stage, folder in [('before','original'),('after','candidate')]:
        assert sha(ROOT / ('source/cascade-'+stage+'.rs')) == taint['source/'+folder+'/servo/components/style/properties/cascade.rs']

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    manifest=authenticate()
    sources()
    audit=read('AUDITS.json')
    definitions=(ROOT/'lean/TaintHistory.lean').read_text()
    assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',definitions)
    names=['TaintHistory.'+n for n in re.findall(r'^theorem (\w+)',definitions,re.M)]
    assert names==audit['names']
    assert (ROOT/'lean/HistoryAudit.lean').read_text()=='import TaintHistory\n'+'\n'.join('#print axioms '+n for n in names)+'\n'
    tool=read('TOOLCHAIN.json');lean=Path(tool['lean'])
    assert sha(lean)==tool['lean_sha256']
    for n,h in read('TOOLCHAIN-LIBRARY.json').items():assert sha(lean.parent.parent/n)==h,n
    out=args.output.resolve();source=ROOT.resolve()
    assert not out.exists() and not out.is_relative_to(source) and not source.is_relative_to(out),'fresh external output required'
    out.mkdir(parents=True)
    env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))}
    env['LEAN_PATH']=str(out)
    commands=[]
    def run(arguments,label):
        p=subprocess.run([str(lean),*arguments],cwd=out,env=env,capture_output=True,text=True)
        (out/(label+'.log')).write_text(p.stdout+p.stderr)
        commands.append({'command':[str(lean),*arguments],'cwd':str(out),'label':label,'exit':p.returncode})
        assert p.returncode==0,label+': '+p.stdout+p.stderr
        return p.stdout
    for module in [*audit['modules'],'HistoryAudit']:
        (out/(module+'.lean')).write_bytes((ROOT/'lean'/(module+'.lean')).read_bytes())
    for module in audit['modules']:run(['-o',module+'.olean',module+'.lean'],module)
    log=run(['HistoryAudit.lean'],'axioms')
    reports=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",log)
    assert [n for n,_ in reports]==names
    for n,a in reports:assert {v.strip() for v in a.split(',') if v.strip()} <= {'propext','Quot.sound','Classical.choice'},n
    driver=(ROOT/'Driver.lean').read_text();mutants=[]
    for mutation in [None,*read('MUTATIONS.json')]:
        name='baseline' if mutation is None else mutation['id']
        code=driver
        if mutation:
            assert code.count(mutation['old'])==1
            code=code.replace(mutation['old'],mutation['new'])
        filename='Driver_'+name.replace('-','_')+'.lean';(out/filename).write_text(code)
        run(['-o',filename.replace('.lean','.olean'),filename],name+'-compile')
        observed=run(['--run',filename],name+'-run').strip()
        expected='|'.join(['true']*7) if mutation is None else mutation['expected']
        assert observed==expected,(name,observed,expected)
        if mutation:assert observed!='|'.join(['true']*7)
        mutants.append({'id':name,'observed':observed,'expected':expected,'compiled':True})
    result={'inputs':len(manifest),'compiled_modules':audit['modules'],'new_axiom_reports':len(reports),'names':names,
        'mutations':mutants,'commands':commands,'source_transfer':'exact two replacements; no translation proof',
        'native_execution':False,'native_payload_quotient':'OPEN','upstream_substitution_and_gate_eligibility':'OPEN'}
    (out/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':main()
