import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

from support_b import corpus
import bridge
import provider_oracle
import cases as case_module

BASE=Path(__file__).resolve().parent
VERSIONS=('original','B','A','AB')


def compile_native(source,name,out,tc,gtk=False,opt='-O1'):
    src=out/(name+'.cpp');binary=out/name;log=out/(name+'-compile.log')
    src.write_text(source)
    command=[tc['compiler'],'-isysroot',tc['sdk'],'-std=c++20',opt,'-g','-fsanitize=undefined','-fno-sanitize-recover=all']
    if gtk:command.append('-DMOZ_WIDGET_GTK')
    command += [str(src),'-o',str(binary)]
    with log.open('w') as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=120)
    assert r.returncode==0,(name,'compile',log)
    return binary


def execute(binary,cases,out,name):
    raw=corpus.wire(cases);(out/(name+'-input.txt')).write_text(raw)
    r=subprocess.run([str(binary)],input=raw,text=True,capture_output=True,timeout=120)
    (out/(name+'-stdout.txt')).write_text(r.stdout);(out/(name+'-stderr.txt')).write_text(r.stderr)
    assert r.returncode==0,(name,'runtime',r.returncode,r.stderr[-3000:])
    rows=[]
    for line in r.stdout.splitlines():
        ident,scores,selected,counters,events=line.split('|')
        ints=lambda s:list(map(int,s.split(','))) if s else []
        rows.append(dict(id=int(ident),scores=ints(scores),selected=ints(selected),counters=ints(counters),events=events.split(',') if events else []))
    assert len(rows)==len(cases)
    return rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default=str(BASE/'development'));p.add_argument('--reuse',action='store_true');p.add_argument('--variants',default=','.join(VERSIONS));p.add_argument('--gtk',action='store_true')
    args=p.parse_args();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    tc=json.loads((BASE/'support_b/TOOLCHAIN-v1.json').read_text())
    cases=case_module.generate()
    if args.gtk:cases=[c for c in cases if c['operation'] in (2,12,13)]
    (out/'CORPUS.json').write_text(json.dumps(cases,indent=2)+'\n')
    errors=[];all_rows={};all_expected={};coordinate_checks=0
    for variant in args.variants.split(','):
        name=variant+('-GTK' if args.gtk else '')
        generated=bridge.generate(variant,(BASE/'driver.cpp').read_text())
        for item in bridge.manifest(variant):assert item['body'] in generated
        binary=out/name if args.reuse else compile_native(generated,name,out,tc,args.gtk)
        rows=execute(binary,cases,out,name);all_rows[variant]=rows
        sizes=tuple(rows[-1]['selected']);assert sizes==(16,48),sizes
        expected=[]
        for c,r in zip(cases,rows):
            e=provider_oracle.expected(c,variant,args.gtk,sizes);expected.append(e)
            for f in c['faces']:
                for value in provider_oracle.ranks.coordinates(c,f,variant):
                    assert 0<=value<=2000 and (value*256).denominator==1
                    assert provider_oracle.ranks.float32(value)==value
                    coordinate_checks+=1
            if e!=r:errors.append(dict(variant=name,case=c,expected=e,actual=r))
        (out/(name+'-oracle.json')).write_text(json.dumps(expected,indent=2)+'\n')
        print(name,len(cases),'executed; cumulative mismatches',len(errors),flush=True)
    (out/'ERRORS.json').write_text(json.dumps(errors,indent=2)+'\n')
    print(json.dumps(errors[:3],indent=2))
    assert not errors,len(errors)
    unchanged=0
    if set(all_rows)==set(VERSIONS):
        for i,c in enumerate(cases):
            if c['target']==0 or c['target']==25600 and not c['allow']:
                assert all_rows['original'][i]==all_rows['B'][i]
                assert all_rows['A'][i]==all_rows['AB'][i]
                unchanged+=1
    extraction={v:[{k:x for k,x in item.items() if k!='body'} for item in bridge.manifest(v)] for v in all_rows}
    (out/'EXTRACTION.json').write_text(json.dumps(extraction,indent=2)+'\n')
    operation_counts=Counter(c['operation'] for c in cases)
    multiplier=len(all_rows)
    summary=dict(status='PASS',cases=len(cases),variants=list(all_rows),total_comparison_rows=len(cases)*multiplier,operation_counts_per_variant=dict(sorted(operation_counts.items())),complete_consumer_entry_rows=sum(n for op,n in operation_counts.items() if op not in (0,8,13))*multiplier,helper_only_rows=operation_counts[0]*multiplier,fixedpoint_provider_rows=operation_counts[8]*multiplier,abi_rows=operation_counts[13]*multiplier,unchanged_B_controls=unchanged,exact_coordinate_checks=coordinate_checks,all_rows_compare=['scores','ordered selected identities','public counters and global cmap return','ordered provider events'],browser_executions=0)
    (out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':main()
