import argparse
import json
from pathlib import Path
import statistics
import subprocess
import bridge
import run

BASE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default=str(BASE/'cost-development'));args=p.parse_args();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    tc=json.loads((BASE/'support_b/TOOLCHAIN-v1.json').read_text());rows={};summary=[]
    for variant in ('original','B','A','AB'):
        source=bridge.generate(variant,(BASE/'benchmark.cpp').read_text())
        old='void note(const std::string& label, int id) { events.push_back(label + std::to_string(id)); }'
        assert source.count(old)==1
        source='#include <chrono>\n#include <ctime>\n'+source.replace(old,'uint64_t providerCalls = 0;\nvoid note(const std::string&, int) { ++providerCalls; }')
        binary=run.compile_native(source,variant,out,tc,opt='-O2')
    for round_index,order in enumerate((('original','A','B','AB'),('AB','B','A','original'),('B','original','AB','A'))):
        for variant in order:
            r=subprocess.run([str(out/variant)],capture_output=True,text=True,timeout=120)
            (out/(variant+f'-{round_index}-stdout.txt')).write_text(r.stdout);(out/(variant+f'-{round_index}-stderr.txt')).write_text(r.stderr)
            assert r.returncode==0,r.stderr
            current=[list(map(int,l.split(','))) for l in r.stdout.splitlines()]
            assert len(current)==210
            rows.setdefault(variant,[]).extend(current)
            print(variant,'round',round_index,'cost cases',len(current),flush=True)
    for before,after in (('original','A'),('B','AB')):
        for size in (100,1000,10000):
            for scenario in (0,1):
                for op in range(1,6):
                    get=lambda v:[r for r in rows[v] if r[:3]==[size,scenario,op]]
                    a,b=get(before),get(after)
                    summary.append(dict(before=before,after=after,size=size,scenario='ties' if scenario else 'varied',operation=op,before_ns=statistics.median(r[5] for r in a),after_ns=statistics.median(r[5] for r in b),ratio=statistics.median(r[5] for r in b)/statistics.median(r[5] for r in a),before_provider_calls=a[0][6],after_provider_calls=b[0][6],before_checksum=a[0][7],after_checksum=b[0][7],samples_per_variant=len(a),before_ns_range=[min(r[5] for r in a),max(r[5] for r in a)],after_ns_range=[min(r[5] for r in b),max(r[5] for r in b)]))
    (out/'COST.json').write_text(json.dumps(dict(scope='Extracted full methods, explicit adapters, O2 UBSan, counting provider calls; process CPU time samples (wall clock also retained) on shared host; external build may be active; not browser performance.',rows=summary),indent=2)+'\n')

if __name__=='__main__':main()
