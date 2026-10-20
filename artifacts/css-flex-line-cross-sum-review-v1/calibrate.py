import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import tempfile

LIMIT = 1073741823
MAX32 = 2147483647
HERE = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def require(x, why):
    if not x:
        raise RuntimeError(why)

def extract(p):
    s = p.read_text()
    initials = re.findall(r"nscoord sumLineCrossSizes = [^;]+;", s)
    steps = re.findall(r"sumLineCrossSizes (?:\+=|=) [^;]+;", s)
    require(len(initials) == 1 and len(steps) == 2, "sum slice count")
    return initials[0], steps[1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    require(not out.exists(), "new output")
    out.mkdir(parents=True)
    initial, step = extract(args.candidate)
    old_initial, old_step = extract(args.before)
    require("int64_t(aCrossGapSize) * int64_t(flr.mLines.Length() - 1)" in initial, "candidate initial expression")
    require("int64_t(sumLineCrossSizes) + line.LineCrossSize()" in step, "candidate step expression")
    variants = {
        "candidate":(initial, step),
        "before":(old_initial, old_step),
        "gap-count-mutant":(initial.replace("Length() - 1", "Length()"), step),
        "zero-gap-mutant":(initial.replace("nscoord_MAX,", "0,"), step),
        "uncapped-step-mutant":(initial, "sumLineCrossSizes = int64_t(sumLineCrossSizes) + line.LineCrossSize();"),
    }
    cases = []
    def add(gap, lines):
        require(0 <= gap <= MAX32 and 1 <= len(lines) <= 4294967295 and all(0 <= v <= MAX32 for v in lines), "outside provider domain")
        cases.append({"gap":gap,"lines":lines,"count":len(lines),"kind":"fold","expected":min(LIMIT,gap*(len(lines)-1)+sum(lines))})
    boundaries=[0,1,LIMIT-1,LIMIT,LIMIT+1,MAX32-1,MAX32]
    for gap in boundaries:
        for a in boundaries:
            add(gap,[a])
            add(gap,[a,0])
            add(gap,[a,a])
            add(gap,[a,0,a])
    for lines in [[720000000]*3,[720000000]*2,[1200]*4,[0],[0]*4,[20,30,40],[LIMIT,1,0],[1,LIMIT,1]]:
        for gap in [0,1,720000000]: add(gap,lines)
    rng=random.Random(492401)
    for _ in range(400):
        add(rng.choice(boundaries+[rng.randrange(MAX32+1)]),[rng.choice(boundaries+[rng.randrange(MAX32+1)]) for _ in range(rng.randrange(1,33))])
    for count in [1,2,3,2147483647,2147483648,4294967294,4294967295]:
        for gap in boundaries:
            cases.append({"gap":gap,"lines":[],"count":count,"kind":"product","expected":min(LIMIT,gap*(count-1))})
    (out/'CASES.json').write_text(json.dumps(cases,indent=2)+'\n')
    source_prefix = r"""#include <algorithm>
#include <cstdint>
#include <iostream>
#include <vector>
using nscoord = int32_t;
constexpr nscoord nscoord_MAX = 1073741823;
struct FlexLine { nscoord value; nscoord LineCrossSize() const { return value; } };
struct Lines {
  uint32_t count;
  size_t Length() const { return count; }
};
struct FLR { Lines mLines; };
"""
    source_tail = r"""
int main() {
  uint64_t count, length;
  int64_t gap;
  while (std::cin >> count >> gap >> length) {
    if (count < 1 || count > UINT32_MAX || gap < 0 || gap > INT32_MAX || length > 100000) return 41;
    std::vector<FlexLine> lines;
    for (size_t i=0; i<length; ++i) {
      int64_t value;
      if (!(std::cin >> value) || value < 0 || value > INT32_MAX) return 42;
      lines.push_back({int32_t(value)});
    }
    if (length && count != length) return 43;
    std::cout << compute(int32_t(gap), uint32_t(count), lines) << '\n';
  }
}
"""
    def wire(rows):
        return ''.join(str(c['count'])+' '+str(c['gap'])+' '+str(len(c['lines']))+' '+ ' '.join(map(str,c['lines']))+'\n' for c in rows)
    results=[]
    env=dict(os.environ)
    with tempfile.TemporaryDirectory(prefix='flex-lines-independent-') as tmp:
        for name,(init,increment) in variants.items():
            code=source_prefix+'nscoord compute(nscoord aCrossGapSize, uint32_t count, const std::vector<FlexLine>& lines) {\n FLR flr{{count}};\n '+init+'\n for (const FlexLine& line : lines) {\n '+increment+'\n }\n return sumLineCrossSizes;\n}\n'+source_tail
            source=out/(name+'.cpp'); source.write_text(code)
            for opt in ['O0','O2']:
                binary=Path(tmp)/(name+'-'+opt)
                cmd=['/usr/bin/clang++','-std=c++17','-'+opt,'-fsanitize=undefined','-fno-sanitize-recover=undefined',str(source),'-o',str(binary)]
                build=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env)
                (out/(name+'-'+opt+'-build.log')).write_text(build.stdout)
                require(build.returncode==0,'compile '+name)
                selected=cases if name!='before' else [c for c in cases if c['gap']*(c['count']-1)+sum(c['lines'])<=MAX32]
                run=subprocess.run([str(binary)],input=wire(selected),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
                (out/(name+'-'+opt+'.stdout')).write_text(run.stdout)
                (out/(name+'-'+opt+'.stderr')).write_text(run.stderr)
                require(run.returncode==0,'unexpected runtime failure '+name)
                actual=[int(x) for x in run.stdout.splitlines()]
                require(len(actual)==len(selected),'output roster')
                expected=[c['gap']*(c['count']-1)+sum(c['lines']) if name=='before' else c['expected'] for c in selected]
                mismatch=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
                require(bool(mismatch)==('mutant' in name),'comparison '+name)
                results.append({'variant':name,'optimization':opt,'compile_command':cmd,'compile_exit':0,'run_exit':0,'cases':len(selected),'mismatches':len(mismatch),'first_witness':None if not mismatch else {'input':selected[mismatch[0]],'actual':actual[mismatch[0]],'expected':expected[mismatch[0]]},'binary_sha256':sha(binary)})
                if name=='candidate':
                    for label,raw in [('zero-count','0 0 0\n'),('negative-gap','1 -1 0\n'),('negative-line','1 0 1 -1\n'),('oversized-count','4294967296 0 0\n')]:
                        bad=subprocess.run([str(binary)],input=raw,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
                        require(bad.returncode in [41,42] and bad.stdout=='','domain guard '+label)
                    results[-1]['invalid_domain_guards']=4
                if name=='before':
                    bad=subprocess.run([str(binary)],input='3 0 3 720000000 720000000 720000000\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
                    (out/('before-'+opt+'-overflow.stderr')).write_text(bad.stderr)
                    require(bad.returncode!=0 and 'signed integer overflow' in bad.stderr,'old overflow witness')
                    results[-1]['signed_overflow_witness_exit']=bad.returncode
    receipt={'status':'PASS','input_sha256':{str(args.before):sha(args.before),str(args.candidate):sha(args.candidate)},'source_slices':{'initial':initial,'step':step,'before_initial':old_initial,'before_step':old_step},'clang_sha256':sha(Path('/usr/bin/clang++')),'cases':len(cases),'results':results,'temporary_compiler_products_removed':True,'scope':'Extracted changed arithmetic expressions, not complete Gecko execution. Synthetic uint32 counts exercise only the gap expression, not allocated huge arrays. Facade provides nonnegative signed32 line/gap values and the documented uint32 count; observer/provider proofs are separate.'}
    (out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':'PASS','cases':len(cases),'configurations':len(results)}))
if __name__=='__main__': main()
