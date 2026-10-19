import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import bridge
import corpus
import oracle

BASE=Path(__file__).resolve().parent
VERSIONS=('original','B','A','AB')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_native(source,name,out,tc,gtk=False):
    src=out/(name+'.cpp');binary=out/name;log=out/(name+'-compile.log')
    src.write_text(source)
    command=[tc['compiler'],'-isysroot',tc['sdk'],'-std=c++20','-O1','-g','-fsanitize=undefined','-fno-sanitize-recover=all']
    if gtk:command.append('-DMOZ_WIDGET_GTK')
    command += [str(src),'-o',str(binary)]
    with log.open('w') as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=120)
    assert r.returncode==0,(name,'compile',log)
    return binary


def execute(binary,cases,out,name):
    raw=corpus.wire(cases)
    (out/(name+'-input.txt')).write_text(raw)
    r=subprocess.run([str(binary)],input=raw,text=True,capture_output=True,timeout=90)
    (out/(name+'-stdout.txt')).write_text(r.stdout)
    (out/(name+'-stderr.txt')).write_text(r.stderr)
    assert r.returncode==0,(name,'runtime',r.returncode,r.stderr[-3000:])
    rows=[]
    for line in r.stdout.splitlines():
        ident,scores,selected,counters,events=line.split('|')
        ints=lambda s:list(map(int,s.split(','))) if s else []
        rows.append(dict(id=int(ident),scores=ints(scores),selected=ints(selected),counters=ints(counters),events=events.split(',') if events else []))
    assert len(rows)==len(cases)
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default=str(BASE/'replay-development'));parser.add_argument('--skip-lean',action='store_true');parser.add_argument('--reuse-binaries',action='store_true')
    args=parser.parse_args();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    tc=json.loads((BASE/'TOOLCHAIN-v1.json').read_text())
    for name in ('compiler','lean'):
        assert digest(Path(tc[name]))==tc[name+'_sha256'],name
    assert digest(Path(tc['sdk'])/'SDKSettings.json')==tc['sdk_settings_sha256']
    for path,sha in json.loads((BASE/'ORIGINAL-SOURCES.json').read_text()).items():
        assert digest(BASE/'original'/path)==sha,path
    for variant in VERSIONS:
        generated=bridge.generate(variant,(BASE/'driver.cpp').read_text())
        for item in bridge.manifest(variant):
            assert item['body'] in generated,(variant,item['marker'])
    cases=corpus.generate();(out/'CORPUS-v1.json').write_text(json.dumps(cases,indent=2)+'\n')
    rows={};errors=[];spec_checks=0
    for variant in VERSIONS:
        binary=out/variant
        if not args.reuse_binaries:binary=compile_native(bridge.generate(variant,(BASE/'driver.cpp').read_text()),variant,out,tc)
        rows[variant]=execute(binary,cases,out,variant)
        for c,r in zip(cases,rows[variant]):
            assert c['id']==r['id']
            target=3584 if c['target']==30000 else c['target']
            expected_scores=[oracle.legacy_style(f[0],f[1],target,c['allow'],2816 if variant in ('B','AB') else 3584) for f in c['faces']]
            expected=oracle.selected(c,variant)
            if r['scores']!=expected_scores or r['selected']!=expected:
                errors.append(dict(variant=variant,id=c['id'],name=c['name'],expected_scores=expected_scores,actual_scores=r['scores'],expected=expected,actual=r['selected']))
            if variant in ('B','AB') and c['allow']:
                ranks=[];scores=[]
                for f,score in zip(c['faces'],r['scores']):
                    try:rank=oracle.spec_style(f[0],f[1],target)
                    except ValueError:continue
                    ranks.append(rank);scores.append(score)
                for i in range(len(ranks)):
                    for j in range(len(ranks)):
                        assert (ranks[i]<=ranks[j])==(scores[i]<=scores[j]),(variant,c['id'],i,j,'spec order')
                        spec_checks+=1
        print(variant,len(rows[variant]),'executed',flush=True)
    gtk_cases=[c for c in cases if c['operation']==2]
    for variant in VERSIONS:
        name=variant+'-GTK';binary=out/name
        if not args.reuse_binaries:binary=compile_native(bridge.generate(variant,(BASE/'driver.cpp').read_text()),name,out,tc,True)
        results=execute(binary,gtk_cases,out,name)
        for c,r in zip(gtk_cases,results):
            expected=oracle.selected(c,variant,True)
            if r['selected']!=expected:errors.append(dict(variant=name,id=c['id'],name=c['name'],expected=expected,actual=r['selected']))
        print(name,len(results),'executed',flush=True)
    (out/'ERRORS-v1.json').write_text(json.dumps(errors,indent=2)+'\n')
    if errors:
        print(json.dumps(errors[:12],indent=2));raise SystemExit(f'{len(errors)} comparison mismatches')
    unchanged=[c['id'] for c in cases if c['target']==0 or c['target']==25600 and not c['allow']]
    for i in unchanged:
        assert rows['original'][i]==rows['B'][i],('unchanged B',i)
        assert rows['A'][i]==rows['AB'][i],('unchanged AB',i)
    extraction={v:[{k:x for k,x in e.items() if k!='body'} for e in bridge.manifest(v)] for v in VERSIONS}
    (out/'EXTRACTION-v1.json').write_text(json.dumps(extraction,indent=2)+'\n')
    if not args.skip_lean:
        source=(BASE/'Threshold.lean').read_text()
        names=re.findall(r'^theorem (\w+)',source,re.M)
        audited=out/'Audited.lean';audited.write_text(source+'\n'+''.join(f'#print axioms Threshold.{n}\n' for n in names))
        r=subprocess.run([tc['lean'],str(audited)],text=True,capture_output=True,timeout=120)
        (out/'Lean-audit.log').write_text(r.stdout+r.stderr)
        assert r.returncode==0,('lean',r.stdout[-4000:])
        assert len(re.findall(r"'Threshold\.[^']+'",r.stdout))==len(names)
        assert 'sorryAx' not in r.stdout
        for dependencies in re.findall(r'depends on axioms: \[([^\]]*)\]',r.stdout):
            assert set(x.strip() for x in dependencies.split(',') if x.strip()) <= {'propext','Classical.choice','Quot.sound'},dependencies
        assert not re.search(r'\b(sorry|axiom|unsafe|native_decide)\b',source)
    summary=dict(status='PASS',corpus_cases=len(cases),native_calls=len(cases)*4+len(gtk_cases)*4,spec_pairwise_checks=spec_checks,unchanged_cases=len(unchanged),complete_functions_per_variant=len(bridge.ITEMS),browser_executions=0,scope='Universal Lean same-sign/italic-positive model contract; bounded compiled caller/provider-adapter comparison. Cross-kind formula checks are compatibility only; actual parser/platform providers remain assumptions.')
    (out/'RESULT-v1.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
