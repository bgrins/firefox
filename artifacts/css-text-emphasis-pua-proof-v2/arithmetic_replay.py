import itertools
import json
import random
import subprocess
from arithmetic_mutations import ARITHMETIC_MUTATIONS


def cases():
    rows=[]
    widths=[-2147483648,-2147483647,-1501,-1,0,1,1501,2147483646,2147483647]
    totals=[1,2,3,65535,65536,2147483647,2147483648,2147483649,4294967295]
    for width,total,final in itertools.product(widths,totals,[False,True]):
        for index,count in sorted({(0,0),(0,1),(0,total),(total,0),(total-1,1),(1,0),(total//2,total-total//2)}):
            rows.append([width,total,index,count,final])
    rng=random.Random(230018)
    for _ in range(2048):
        total=rng.randrange(1,1<<32);index=rng.randrange(total+1)
        rows.append([rng.randrange(-(1<<31),1<<31),total,index,rng.randrange(total-index+1),bool(rng.randrange(2))])
    rows += [[-1,2,1,1,False],[-2147483648,2147483649,1,1,False],[-1,2,1,1,True],[10,2,1,1,False]]
    return rows


def expected(row,signed):
    width,total,index,count,final=row
    q=(abs(width)//total)*(-1 if width<0 else 1) if signed else (width%(1<<32))//total
    advance=index*q
    part=count*q+(width-total*q if final else 0)
    return [advance,part,int(count==0 or index>0),int(count==0 or index+count<total)]


def replay_arithmetic(out,compile):
    rows=cases();data="".join(" ".join(str(int(v)) for v in row)+"\n" for row in rows)
    (out/"ARITHMETIC-CORPUS.json").write_text(json.dumps(rows)+"\n")
    receipts=[]
    for signed in [False,True]:
        name="arithmetic-signed" if signed else "arithmetic-legacy"
        executable=compile(name,signed=signed)
        result=subprocess.run([str(executable),"arithmetic"],input=data,capture_output=True,text=True)
        assert result.returncode==0
        actual=[json.loads(line) for line in result.stdout.splitlines()]
        assert actual==[expected(row,signed) for row in rows]
        (out/(name+".json")).write_text(json.dumps(actual)+"\n")
        receipts.append(dict(name=name,rows=len(rows),status="PASS",scope="actual arithmetic slice from complete separately extracted ComputeLigatureData; raw count inputs, not allocated billion-unit buffers"))
    mutants=[]
    wanted=[expected(row,True) for row in rows]
    for mutation in ARITHMETIC_MUTATIONS:
        executable=compile("arithmetic-"+mutation,signed=True,arithmetic_mutant=mutation)
        result=subprocess.run([str(executable),"arithmetic"],input=data,capture_output=True,text=True)
        assert result.returncode==0
        actual=[json.loads(line) for line in result.stdout.splitlines()]
        assert len(actual)==len(rows)
        differences=[i for i,(a,e) in enumerate(zip(actual,wanted)) if a!=e]
        assert differences
        kernel_rows={"floor_negative":[-1,2,1,1,False],"narrow_denominator":[-2147483648,2147483649,1,1,False],"unsigned_quotient":[-1,2,1,1,False],"omit_remainder":[-1,2,1,1,True],"omit_part_index":[10,2,1,1,False]}
        i=rows.index(kernel_rows[mutation])
        assert i in differences
        mutants.append(dict(name=mutation,compile_exit=0,run_exit=0,rows=len(rows),differences=differences,
                            witness=dict(input=rows[i],actual=actual[i],expected=wanted[i]),
                            kernel_witness="Emphasis.SignedWitness."+mutation))
    (out/"ARITHMETIC-RESULT.json").write_text(json.dumps(dict(variants=receipts,mutants=mutants),indent=2)+"\n")
    return receipts,mutants
