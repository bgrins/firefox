import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("require isolated nonoptimized Python without site")
sys.dont_write_bytecode = True
from pathlib import Path
import json, subprocess

ROOT = Path(__file__).resolve().parent.parent

def cases():
    rows = []
    for seed in range(4):
        old = [100 + seed, -1 if seed % 2 else 20, 0, 1073741823, 1073741823,
               seed, seed + 1, 40 + seed, seed + 3, 240, 200 + seed]
        variants = [old[:]]
        for field in range(11):
            for delta in [-1, 1]:
                new = old[:]
                new[field] += delta
                variants.append(new)
        variants.append(old[:9] + [old[10],old[9]])
        for new in variants:
            for present in [0, 1]:
                for dirty in [0, 1]:
                    rows.append(dict(id=len(rows), old=old, new=new, present=present, dirty=dirty))
    return rows

FACADE = r'''
#include <algorithm>
#include <cstdint>
#include <iostream>
using nscoord = int32_t;
struct WritingMode {};
struct LogicalSize { int32_t i,b; bool operator==(const LogicalSize&) const = default; };
struct LogicalMargin {
  int32_t iStart,iEnd,bStart,bEnd;
  bool operator==(const LogicalMargin&) const = default;
  int32_t BStartEnd(WritingMode) const { return bStart+bEnd; }
};
struct ReflowInput {
  int32_t data[11];
  LogicalSize mContainingBlockSize;
  LogicalSize ComputedSize() const { return {data[0],data[1]}; }
  LogicalMargin ComputedLogicalBorderPadding(WritingMode) const { return {data[5],data[6],data[7],data[8]}; }
  WritingMode GetWritingMode() const { return {}; }
  int32_t ComputedMinBSize() const { return data[2]; }
  int32_t ComputedMaxBSize() const { return data[3]; }
  int32_t AvailableBSize() const { return data[4]; }
};
struct ReflowOutput { int32_t BSize(WritingMode) const { return 100000; } };
class nsFlexContainerFrame { public: class CachedBAxisMeasurement; };
'''
MAIN = r'''
int main() {
  int id,present,dirty;
  while(std::cin>>id>>present>>dirty) {
    ReflowInput old{},current{};
    for(auto& value:old.data) if(!(std::cin>>value)) return 2;
    for(auto& value:current.data) if(!(std::cin>>value)) return 2;
    old.mContainingBlockSize={old.data[9],old.data[10]};
    current.mContainingBlockSize={current.data[9],current.data[10]};
    nsFlexContainerFrame::CachedBAxisMeasurement cached(old,ReflowOutput{});
    bool valid=cached.IsValidFor(current);
    std::cout<<id<<" "<<valid<<" "<<(present&&!dirty&&valid)<<" "<<cached.BSize()<<"\n";
  }
}
'''

def execute(output):
    output.mkdir()
    rows = cases()
    payload = ''.join(' '.join(map(str, [r['id'], r['present'], r['dirty']] + r['old'] + r['new']))+'\n' for r in rows)
    (output/'CASES.json').write_text(json.dumps(rows, indent=2)+'\n')
    bindings = json.loads((ROOT/'SOURCE-BINDINGS.json').read_text())
    bodies = {b['variant']:b['body'] for b in bindings if b['name']=='class nsFlexContainerFrame::CachedBAxisMeasurement'}
    new = bodies['candidate']
    basis = '          mContainingBlockSize(aRI.mContainingBlockSize),'
    if new.count(basis)!=1: raise RuntimeError('candidate initializer anchor')
    variants = dict(bodies)
    variants.update(
        zero_basis=new.replace(basis,'          mContainingBlockSize{0,0},'),
        omit_inline=new.replace(basis,'          mContainingBlockSize{0,aRI.mContainingBlockSize.b},'),
        omit_block=new.replace(basis,'          mContainingBlockSize{aRI.mContainingBlockSize.i,0},'))
    records = []
    for name, body in variants.items():
        source = output/(name+'.cpp')
        source.write_text(FACADE+body+'\n'+MAIN)
        for mode, flags in [('debug',['-O0']),('release',['-O2']),('ubsan',['-O1','-fsanitize=undefined','-fno-sanitize-recover=all'])]:
            if name not in bodies and mode!='release':
                continue
            binary=output/(name+'-'+mode)
            command=['/usr/bin/clang++','-std=c++20','-Wall','-Wextra','-Werror']+flags+[str(source),'-o',str(binary)]
            build=subprocess.run(command,capture_output=True,text=True)
            record=dict(variant=name,mode=mode,command=command,build_exit=build.returncode,build_stdout=build.stdout,build_stderr=build.stderr)
            if build.returncode or build.stderr:
                raise RuntimeError(record)
            run=subprocess.run([str(binary)],input=payload,capture_output=True,text=True)
            record.update(run_exit=run.returncode,run_stderr=run.stderr)
            (output/(name+'-'+mode+'.txt')).write_text(run.stdout)
            if run.returncode or run.stderr:
                raise RuntimeError(record)
            actual=[list(map(int,line.split())) for line in run.stdout.splitlines()]
            if len(actual)!=len(rows) or any(len(a)!=4 or a[0]!=i for i,a in enumerate(actual)):
                raise RuntimeError('native row grammar/roster mismatch')
            mismatches=[]
            for row,values in zip(rows,actual):
                old,new=row['old'],row['new']
                valid = (old[:9]==new[:9] if name=='original' else
                         old[:5]==new[:5] if name=='upstream-original' else
                         old[:5]+old[9:]==new[:5]+new[9:] if name=='upstream-candidate' else old==new)
                expected=[row['id'],int(valid),int(row['present'] and not row['dirty'] and valid),100000-old[7]-old[8]]
                if values!=expected: mismatches.append(dict(id=row['id'],actual=values,expected=expected))
            record['mismatches']=mismatches
            if name in bodies and mismatches:
                raise RuntimeError(record)
            if name not in bodies and not mismatches:
                raise RuntimeError('semantic mutant survived')
            records.append(record)
            (output/'RESULT.json').write_text(json.dumps(records,indent=2)+'\n')
    return dict(cases=len(rows),runs=len(records),mutants={r['variant']:len(r['mismatches']) for r in records if r['mismatches']})

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('fresh absolute output argument required')
    out=Path(sys.argv[1])
    if not out.is_absolute() or out.exists() or out.resolve().is_relative_to(ROOT):
        raise SystemExit('fresh external output required')
    print(json.dumps(execute(out)))
