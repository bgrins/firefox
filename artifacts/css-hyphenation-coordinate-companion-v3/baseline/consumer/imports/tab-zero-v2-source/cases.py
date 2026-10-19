import itertools
import math
import struct


def bits(x):
    return struct.unpack('Q',struct.pack('d',float(x)))[0]


def cases():
    result=[]
    def add(**kw):
        result.append(dict(id=len(result),**kw))
    for x,w,m in itertools.product([-100.0,-0.0,0.0,3.0,20.0,1073741800.0],[-20.0,-0.0,0.0,0.5,2.0,20.0],[0.0,0.5,10.0]):
        add(mode=0,bits=[bits(x),bits(w),bits(m)],domain='helper')
    for x,w,m in [(-0.0,0.0,5e-324),(0.0,-0.0,5e-324),(5e-324,5e-324,0),(1e-300,1e-300,1e-300),(-1e-300,-1e-300,1e-300),(1.5,0.25,0.125)]:
        add(mode=0,bits=[bits(x),bits(w),bits(m)],domain='helper')
    sequences=[list(xs) for n in range(5) for xs in itertools.product([-1,0,20],repeat=n)]
    sequences += [[20]+[-1]*7+[20],[-1]*12,[3,5,-1,7,-1,11]]
    for tokens,width,minimum,mode in itertools.product(sequences,[0,20],[0,10],[1,2,3]):
        add(mode=mode,tokens=tokens,begin=0,end=len(tokens),kind=0,width=width,minimum=minimum,
            initial=0,letter=0,model=0,flags=0,split=-1,domain='simple')
    selected=[[],[-1],[-1,20],[20,-1],[-1,-1,20],[20,-1,20],[3,5,-1,7,-1,11]]
    for tokens in selected:
        for width,kind,initial,mode in itertools.product([0,20],[0,1],[0,3,20],[1,2,3,4,5]):
            add(mode=mode,tokens=tokens,begin=0,end=len(tokens),kind=kind,width=width,minimum=10,
                initial=initial,letter=0,model=0,flags=0,split=-1,domain='simple')
    for tokens in [[20,-1,20],[-1,-1],[],[20,20]]:
        for split,width,mode in itertools.product(range(len(tokens)+1),[0,20],[1,2]):
            add(mode=mode,tokens=tokens,begin=0,end=len(tokens),kind=0,width=width,minimum=10,
                initial=3,letter=0,model=0,flags=0,split=split,domain='simple')
    for begin,end,width,mode in itertools.product(range(5),range(5),[0,20],[1,2,3,4,5]):
        if begin<=end:
            add(mode=mode,tokens=[20,-1,3,-1,20],begin=begin,end=end,kind=0,width=width,minimum=10,
                initial=3,letter=0,model=0,flags=0,split=-1,domain='simple')
    for tokens,width,letter,model,mode,flags in itertools.product([[-1,20,-1],[20,-1,20],[-1]],[0,20],[2,3],[0,2],[1,2,3],[0,8]):
        add(mode=mode,tokens=tokens,begin=0,end=len(tokens),kind=0,width=width,minimum=10,
            initial=3,letter=letter,model=model,flags=flags,split=-1,domain='spacing')
    for mode,flags,width in itertools.product([1,2],[1,2,4,16],[0,20]):
        add(mode=mode,tokens=[20,-1,20],begin=0,end=3,kind=0,width=width,minimum=10,
            initial=3,letter=0,model=0,flags=flags,split=-1,domain='early')
    for mode in [6,7,8]:
        add(mode=mode,tokens=[20,3],begin=0,end=2,kind=0,width=20,minimum=10,
            initial=3,letter=0,model=0,flags=0,split=-1,domain='cache')
    for tokens,letter,initial,minimum,mode,split in itertools.product(
            [[-1],[-1,-1],[40,-1,40],[40,-1,-1,40]],[-21,-30,-40],
            [0,3,100],[0,10],[1,2],[-1,0,1]):
        add(mode=mode,tokens=tokens,begin=0,end=len(tokens),kind=1,width=20,
            minimum=minimum,initial=initial,letter=letter,model=0,flags=0,
            split=split,domain='negative-intrinsic')
    maximum=(1<<30)-1
    for tokens,width,initial,mode,split in itertools.product(
            [[20],[20,40],[-1,20],[-1,20,40]], [0,20],
            [maximum-13,maximum-5,maximum], [1,2],[-1,0,1]):
        if width and -1 in tokens and initial != maximum-13:continue
        if initial == maximum-13 and sum(max(0,t) for t in tokens)<=13 and not (width and -1 in tokens):continue
        add(mode=mode,tokens=tokens,begin=0,end=len(tokens),kind=0,width=width,
            minimum=0,initial=initial,letter=0,model=0,flags=0,
            split=split,domain='saturation')
    return result


def encode(rows):
    lines=[]
    for c in rows:
        values=[c['id'],c['mode']]
        if c['mode']==0:values+=c['bits']
        else:
            values += [len(c['tokens'])]+[c[k] for k in ['begin','end','kind','width','minimum','initial','letter','model','flags','split']]+c['tokens']
        lines.append(' '.join(map(str,values)))
    return '\n'.join(lines)+'\n'
