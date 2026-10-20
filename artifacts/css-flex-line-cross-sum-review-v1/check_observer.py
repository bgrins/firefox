import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S")
sys.dont_write_bytecode=True
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import tempfile
L=1073741823

def require(x,msg):
    if not x: raise RuntimeError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def body(text,signature):
    start=text.index(signature); opening=text.index('{',start); depth=1;end=opening+1
    while depth:
        if text[end]=='{': depth+=1
        elif text[end]=='}': depth-=1
        end+=1
    return text[start:end]
def bounds(x,lo,hi):
    return max(min(x,hi) if hi!=L else x,lo) if lo!=L else (min(x,hi) if hi!=L else x)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--reflow',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    out=args.output.resolve();require(not out.exists(),'new output');out.mkdir(parents=True)
    consumer=body(args.candidate.read_text(),'nscoord nsFlexContainerFrame::ComputeCrossSize(')
    helper=body(args.reflow.read_text(),'nscoord ApplyMinMaxBSize(nscoord aBSize, nscoord aConsumed = 0) const')
    inputs=[]
    for column,automatic,computed,contained,lo,hi,total in itertools.product([0,1],[0,1],[0,6000,L],[0,1],[0,3000,6000,L],[0,3000,6000,L],[0,5000,6000,L,L+1,1440000000]):
        definite=bool(column or (computed!=L and not automatic) or contained)
        if column: ideal=8000
        elif computed!=L and not automatic: ideal=computed
        elif contained: ideal=bounds(3000,lo,hi)
        else:
            ideal=bounds(total,lo,hi)
            if automatic: ideal=max(ideal,computed)
        inputs.append({'wire':[column,automatic,computed,contained,lo,hi,total],'expected':[min(L,ideal),int(definite)]})
    (out/'CASES.json').write_text(json.dumps(inputs,indent=2)+'\n')
    prefix = r"""#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <optional>
using nscoord = int32_t;
template<class T> using Maybe = std::optional<T>;
constexpr nscoord NS_UNCONSTRAINEDSIZE = 1073741823;
#define MOZ_ASSERT(x, ...) assert(x)
struct FlexboxAxisTracker { bool column; bool IsColumnOriented() const { return column; } };
struct Frame { Maybe<nscoord> contained; Maybe<nscoord> ContainIntrinsicBSize() const { return contained; } };
struct ReflowInput {
  bool automatic; nscoord computed, lo, hi; Frame* mFrame;
  bool ShouldApplyAutomaticMinimumOnBlockAxis() const { return automatic; }
  nscoord ComputedBSize() const { return computed; }
  nscoord ComputedMinBSize() const { return lo; }
  nscoord ComputedMaxBSize() const { return hi; }
"""
    middle = r"""
};
class nsFlexContainerFrame { public:
  nscoord ComputeCrossSize(const ReflowInput&, const FlexboxAxisTracker&, nscoord, nscoord, bool*) const;
};
"""
    tail = r"""
int main() {
  int column, automatic, contained;
  int32_t computed, lo, hi;
  int64_t total;
  while (std::cin >> column >> automatic >> computed >> contained >> lo >> hi >> total) {
    Frame f{contained ? Maybe<nscoord>(3000) : std::nullopt};
    ReflowInput input{bool(automatic),computed,lo,hi,&f};
    bool definite=false;
    nscoord result=nsFlexContainerFrame().ComputeCrossSize(input, {bool(column)}, 8000,
      std::min<int64_t>(1073741823,total), &definite);
    std::cout << result << " " << definite << "\n";
  }
}
"""
    variants={'candidate':(consumer,helper),'drop-automatic-minimum':(consumer.replace('return std::max(contentBSize, computedBSize);','return contentBSize;'),helper),'treat-absent-max-as-zero':(consumer,helper.replace('aBSize += aConsumed;','aBSize += aConsumed; if (NS_UNCONSTRAINEDSIZE == ComputedMaxBSize()) aBSize = 0;')),'reverse-minmax-priority':(consumer,helper.replace('return aBSize - aConsumed;','if (NS_UNCONSTRAINEDSIZE != ComputedMaxBSize()) aBSize = std::min(aBSize, ComputedMaxBSize()); return aBSize - aConsumed;'))}
    results=[];wire=''.join(' '.join(map(str,c['wire']))+'\n' for c in inputs)
    with tempfile.TemporaryDirectory(prefix='flex-observer-independent-') as tmp:
        for name,(c,h) in variants.items():
            source=out/(name+'.cpp');source.write_text(prefix+h+middle+c+tail)
            for opt in ['O0','O2']:
                binary=Path(tmp)/(name+'-'+opt)
                cmd=['/usr/bin/clang++','-std=c++17','-'+opt,'-fsanitize=undefined','-fno-sanitize-recover=undefined',str(source),'-o',str(binary)]
                build=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(out/(name+'-'+opt+'-build.log')).write_text(build.stdout)
                require(build.returncode==0,'compile '+name)
                run=subprocess.run([str(binary)],input=wire,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                (out/(name+'-'+opt+'.stdout')).write_text(run.stdout);(out/(name+'-'+opt+'.stderr')).write_text(run.stderr)
                require(run.returncode==0,'run '+name)
                rows=[[int(v) for v in line.split()] for line in run.stdout.splitlines()]
                require(len(rows)==len(inputs) and all(len(r)==2 for r in rows),'row shape')
                bad=[i for i,(row,c) in enumerate(zip(rows,inputs)) if row!=c['expected']]
                require(bool(bad)==(name!='candidate'),'oracle '+name)
                results.append({'variant':name,'optimization':opt,'cases':len(inputs),'compile_command':cmd,'compile_exit':0,'run_exit':0,'mismatches':len(bad),'first_witness':None if not bad else {'input':inputs[bad[0]],'actual':rows[bad[0]]},'binary_sha256':sha(binary)})
    result={'status':'PASS','input_sha256':{str(args.candidate):sha(args.candidate),str(args.reflow):sha(args.reflow)},'consumer_sha256':hashlib.sha256(consumer.encode()).hexdigest(),'helper_sha256':hashlib.sha256(helper.encode()).hexdigest(),'cases':len(inputs),'results':results,'temporary_compiler_products_removed':True,'scope':'Complete frozen ComputeCrossSize and ApplyMinMaxBSize method bodies with scalar provider facades, default consumed=0. Exact-sum reference evaluated in Python then capped. Finite calibration and independently proved conditional optional observer; not proof of all input provider construction or other layout arithmetic.'}
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(inputs),'configurations':len(results)}))
if __name__=='__main__': main()
