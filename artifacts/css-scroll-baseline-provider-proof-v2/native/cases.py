import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require isolated nonoptimized Python without site')
sys.dont_write_bytecode=True
from pathlib import Path
import itertools,json
ROOT=Path(__file__).resolve().parent.parent

def roster():
    numeric=[(59,50,9,30),(59,50,0,30),(60,200,9,10),(59,50,9,100),
        (59,50,9,-100),(0,50,9,30),(59,0,9,0),(100,50,9,0),
        (100,50,-20,5),(100,2147483647,2147483647,-2147483648),
        (100,0,2147483647,2147483647),(2147483647,2147483647,-2147483648,-2147483648),
        (2147483647,0,-2147483648,2147483647),(100,100,0,100),
        (100,100,0,0),(60,200,9,None)]
    result=[]
    for mode in range(3):
        for first,line,block,button,contain in itertools.product([False,True],repeat=5):
            for outer,inner,border,child in numeric:
                result.append(dict(id=len(result),mode=mode,first=first,line=line,block=block,
                    button=button,contain=contain,outer=outer,inner=inner,border=border,
                    fallback=77,child=child))
    return result

def read():
    rows=json.loads((ROOT/'CASES.json').read_text())
    if rows!=roster() or any(type(r[k]) is not bool for r in rows for k in ['first','line','block','button','contain']) or any(type(r[k]) is not int for r in rows for k in ['id','mode','outer','inner','border','fallback']) or any(r['child'] is not None and type(r['child']) is not int for r in rows):
        raise ValueError('case roster / schema')
    return rows

def oracle(r,candidate):
    legacy=r['line'] and not r['first'] and r['block'] and not r['button']
    if not candidate and not legacy and not r['contain'] and r['child'] is not None and not -2147483648<=r['border']+r['child']<=2147483647:
        return (r['id'],'SKIP',[])
    calls=[]
    if r['line'] and not r['first']:
        calls.append(0)
        if r['block']:calls.append(1)
    if legacy:return (r['id'],r['fallback'],calls+[2])
    calls.append(3)
    if r['contain']:return(r['id'],None,calls)
    calls.append(4)
    if r['child'] is None:return(r['id'],None,calls)
    if candidate and not r['first']:calls.append(5)
    calls.extend([6,7])
    point=r['border']+r['child'] if not candidate or r['first'] else r['border']+r['inner']-r['child']
    point=0 if point<0 else r['outer'] if point>r['outer'] else point
    value=r['outer']-point if candidate and not r['first'] else point
    return(r['id'],value,calls)

def encode(row):
    identity,value,calls=row
    return str(identity)+'|'+('none' if value is None else str(value))+'|'+','.join(map(str,calls))

if __name__=='__main__':print(json.dumps({'cases':len(read())}))
