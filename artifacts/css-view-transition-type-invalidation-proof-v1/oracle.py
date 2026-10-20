import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('use -I -S without optimization')
sys.dont_write_bytecode = True

def expected(owner, masks):
    current=masks[owner] if owner<2 else 0
    base=[10,17,20,25,30]
    if current&1:base=[100,43,80,75,70]
    if current&2:base[:2]=[200,61]
    return base

def row(index, case):
    owner,root,composed,pres,m0,m1=case['setup']
    masks=[m0,m1];cache=expected(owner,masks);calls=requests=0;pending=False
    def snapshot():return ','.join(map(str,[*masks,calls,requests,int(pending),*cache]))
    output=[str(index),snapshot()]
    for tag,actor,name,error in case['actions']:
        if tag==3:
            if pending:
                values=expected(owner,masks)
                cache=[values[n] if name&(1<<n) else cache[n] for n in range(5)]
                if name==31:pending=False
        elif not error:
            before=masks[actor]
            if tag==0:masks[actor]|=1<<name
            if tag==1:masks[actor]&=~(1<<name)
            if tag==2:masks[actor]=0
            if masks[actor]!=before:
                calls+=1
                if owner==actor and root and composed and pres:
                    requests+=1;pending=True
        output.append(snapshot())
    return '|'.join(output)

def rows(cases):return ''.join(row(i,c)+'\n' for i,c in enumerate(cases))
