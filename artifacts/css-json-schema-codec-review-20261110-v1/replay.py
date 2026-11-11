import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

P = Path(__file__).resolve().parent
A = P.parent / 'css-json-schema-codec-20261110-v1'

def digest(data): return hashlib.sha256(data).hexdigest()
def require(condition, message):
    if not condition: raise ValueError(message)

def declarations(path):
    text = path.read_text()
    ns = re.findall(r'^namespace (\S+)', text, re.M)
    require(len(ns) <= 1, 'multiple namespaces: ' + str(path))
    prefix = ns[0] + '.' if ns else ''
    return [prefix + x for x in re.findall(r"^\s*(?:@\[[^]]+\]\s*)*theorem ([\w.']+)", text, re.M)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(); lean=args.lean.resolve(); out=args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources={}; order=[]
    def visit(module):
        name=module.replace('.', '/')+'.lean'
        if name in sources:return
        data=(A/name).read_bytes();sources[name]=data
        for imports in re.findall(r'^import (.+)',data.decode(),re.M):
            for dep in imports.split():
                if (A/(dep.replace('.', '/')+'.lean')).is_file():visit(dep)
        order.append(module)
    visit('Fixture');visit('TypedSchemaLaws');visit('Document')
    pins=json.loads((A/'PRESERVED.json').read_text())
    for name,expected in pins['sha256'].items():
        require(digest((A/name).read_bytes())==expected,'preserved drift:'+name)
    expected=json.loads((P.parent/'css-typed-codec-20261110-v1/EXPECTED.json').read_text())
    sources['escape.json']=(A/'escape.json').read_bytes()
    source_hashes={n:digest(data) for n,data in sources.items()}
    own={n:digest((P/n).read_bytes()) for n in ['Boundary.lean','Runner.lean','replay.py']}
    commands={}
    with tempfile.TemporaryDirectory(prefix='json-schema-review-') as temp:
        work=Path(temp);env=dict(os.environ,LEAN_PATH=str(work))
        for name,data in sources.items():
            dest=work/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        for name in ['Boundary.lean','Runner.lean']:shutil.copyfile(P/name,work/name)
        def run(label,argv,rejected=False):
            r=subprocess.run([str(x) for x in argv],cwd=work,env=env,capture_output=True,text=True,timeout=300)
            text=r.stdout+r.stderr;(out/(label+'.log')).write_text(text)
            commands[label]={'exit_code':r.returncode,'log_sha256':digest(text.encode())}
            if rejected:require(r.returncode!=0 and 'document refused' in text and 'error:' not in text,'wrong rejection:'+label+'\n'+text)
            else:require(r.returncode==0 and 'error:' not in text and 'warning:' not in text,'run failed:'+label+'\n'+text)
            return r.stdout
        run('version',[lean,'--version'])
        allnames=[]
        for module in order:
            name=module.replace('.', '/')+'.lean'
            require(not re.search(r'\bsorry\b|\badmit\b|\bnative_decide\b|^axiom\b|^unsafe\b',sources[name].decode(),re.M),'proof escape:'+name)
            run('compile-'+module,[lean,'-o',module.replace('.', '/')+'.olean',name])
            allnames+=declarations(work/name)
        run('compile-Boundary',[lean,'-o','Boundary.olean','Boundary.lean'])
        allnames+=declarations(work/'Boundary.lean')
        require(len(set(allnames))==len(allnames),'duplicate declarations')
        (work/'Audit.lean').write_text('import Fixture\nimport Boundary\n'+''.join('#print axioms '+n+'\n' for n in allnames))
        audit=run('axioms',[lean,'Audit.lean']);audits={}
        for line in re.sub(r',\n\s*',', ',audit).splitlines():
            m=re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])",line)
            require(bool(m),'unknown audit line:'+line)
            axioms=set(m[3].split(', ')) if m[3] else set()
            require(axioms<={'propext','Quot.sound','Classical.choice'},'unexpected axioms:'+line)
            require(m[1] not in audits,'duplicate audit');audits[m[1]]=sorted(axioms)
        require(set(audits)==set(allnames),'missing audit')
        inputs=[row['input'] for row in expected]
        rows=[json.loads(line) for line in run('actual-file',[lean,'--run','Runner.lean','escape.json',*inputs]).splitlines()]
        require(rows==expected,'actual fixture output mismatch')
        original=json.loads(sources['escape.json'])
        changed=copy.deepcopy(original);changed['program']={'op':'ret','args':[{'op':'scalar','args':[90]}]}
        (work/'different-valid.json').write_text(json.dumps(changed))
        altered=[json.loads(line) for line in run('different-valid-file',[lean,'--run','Runner.lean','different-valid.json',*inputs]).splitlines()]
        require(altered==[{'input':x,'value':90,'rest':x,'error':False} for x in inputs],'runner substitutes reference')
        bad={}
        d=copy.deepcopy(original);d['program']['execute']='payload';bad['extra-node-field']=d
        d=copy.deepcopy(original);d['program']={'op':'ret','args':[{'op':'scalar','args':[0xD800]}]};bad['surrogate']=d
        d=copy.deepcopy(original);d['program']={'op':'ret','args':[{'op':'scalar','args':[90]},{'op':'scalar','args':[91]}]};bad['wrong-arity']=d
        d=copy.deepcopy(original);d['definitions']['hexExpr']={'op':'use','args':['hexExpr']};bad['alias-cycle']=d
        d=copy.deepcopy(original);d['program']={'op':'ret','args':[{'op':'use','args':['decodeExpr']}]};bad['alias-scope']=d
        for label,doc in bad.items():
            name=label+'.json';(work/name).write_text(json.dumps(doc));run(label,[lean,'--run','Runner.lean',name,'41!'],rejected=True)
    require(not work.exists(),'temporary objects retained')
    require(all(digest((A/n).read_bytes())==h for n,h in source_hashes.items()),'author sources changed during replay')
    report={'status':'pass','sources':source_hashes,'reviewer_sources':own,'modules':order,'audits':audits,'boundary_theorems':declarations(P/'Boundary.lean'),'actual_file_rows':len(rows),'different_valid_file_rows':len(altered),'rejected_actual_files':list(bad),'commands':commands,'temporary_build_removed':True,'toolchain_binary_sha256':digest(lean.read_bytes())}
    (out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(order),'modules',len(audits),'audits',len(rows),'fixture rows',len(altered),'different-program rows',len(bad),'rejections')

if __name__=='__main__':main()
