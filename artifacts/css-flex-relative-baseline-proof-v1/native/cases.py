import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require isolated nonoptimized Python without site')
sys.dont_write_bytecode=True
from pathlib import Path
import itertools,json
ROOT=Path(__file__).resolve().parent.parent
def generate():
    rows=[]
    for mode,inlineReverse,reverse,old,propertyKind,delta,order in itertools.product(
        range(3),(False,True),(False,True),(-1073741823,23),('absent','fresh','stale'),(-10,0,10),[[],[0],[1],[0,1],[1,0]]):
        items=[]
        for identity in order:
            normal=[7+identity*3,11+identity*5]
            prop=None if propertyKind=='absent' else [v+(3 if propertyKind=='stale' else 0) for v in normal]
            items.append({'identity':identity,'actual':[v+delta for v in normal],'property':prop,
                'normal':normal,'size':[40,50],'first':39-identity*19,'last':37-identity*18})
        rows.append({'id':len(rows),'mode':mode,'inlineReverse':inlineReverse,'reverse':reverse,'old':old,'items':items})
    return rows
def read():
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise ValueError('duplicate case key')
            result[key]=value
        return result
    rows=json.loads((ROOT/'CASES.json').read_text(),object_pairs_hook=unique)
    if json.dumps(rows,sort_keys=True)!=json.dumps(generate(),sort_keys=True): raise ValueError('case roster / schema differs')
    return rows
def oracle(row,candidate):
    values=[];queries=[]
    for last in (False,True):
        order=list(reversed(row['items'])) if last != row['reverse'] else row['items']
        if row['old']!=-1073741823 or not order: values.append(row['old']);continue
        item=order[0]
        position=item['actual']
        if candidate:
            queries.append([item['identity'],item['property'] is not None])
            if item['property'] is not None:position=item['property']
        mode=row['mode']
        start=position[1] if mode==0 else (position[0] if mode==1 else 160-item['size'][0]-position[0])
        value=start+item['last' if last else 'first']
        values.append((80 if mode==0 else 160)-value if last else value)
    return [row['id'],*values,queries]
def encode(result):
    identity,first,last,queries=result
    return f'{identity}|{first}|{last}|'+','.join(f'{i}:{int(p)}' for i,p in queries)
if __name__=='__main__': print(json.dumps({'cases':len(read())}))
