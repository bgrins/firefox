import copy
import itertools

UNKNOWN=1073741823
FIELDS=['block','selfEmpty','empty','hidden','marginRoot','intersect','start','end','paddingStart','paddingEnd','preferred','minimum','clear','parent','descend','next','hasOverflow']
LINE_FIELDS=['owner','overflow','inline','empty','clearance','child']


def node(**kw):
    n=dict(block=1,selfEmpty=1,empty=1,hidden=0,marginRoot=0,intersect=1,start=0,end=0,paddingStart=0,paddingEnd=0,preferred=UNKNOWN,minimum=0,clear=0,parent=-1,descend=-1,next=-1,hasOverflow=0)
    n.update(kw)
    return n


def line(owner,child=-1,**kw):
    x=dict(owner=owner,overflow=0,inline=int(child<0),empty=1,clearance=0,child=child)
    x.update(kw)
    return x


def fixture(name,nodes,lines,domain,**kw):
    f=dict(name=name,nodes=nodes,lines=lines,domain=domain,clearance=-1,output=1,initialEmpty=1,initialRetry=0)
    f.update(kw)
    f['input']=' '.join(map(str,[len(nodes),len(lines),f['clearance'],f['output'],f['initialEmpty'],f['initialRetry']]+[n[k] for n in nodes for k in FIELDS]+[l[k] for l in lines for k in LINE_FIELDS]))
    return f


def oracle(f,candidate):
    nodes=f['nodes']
    lineStates=[[l['clearance'],0] for l in f['lines']]
    state=dict(retry=bool(f['initialRetry']),constructed=0,trace=[],margins=[])
    def edge(kind,idx):
        state['trace'].append(f'{kind}{idx}')
        state['margins'].append(nodes[idx]['start' if kind=='S' else 'end'])
    def visit(idx,hasOutput=True,initial=True):
        n=nodes[idx]
        edge('S',idx)
        descend=n['descend'] if n['descend']>=0 else idx
        eligible=not n['paddingStart'] and nodes[descend]['block'] and not nodes[descend]['marginRoot']
        initialized=False
        output=initial
        dirty=False
        stop=False
        if eligible:
            current=descend
            while current>=0 and not stop:
                for overflow in [0,1]:
                    group=[(i,l) for i,l in enumerate(f['lines']) if l['owner']==current and l['overflow']==overflow and (not overflow or nodes[current]['hasOverflow'])]
                    for i,l in group:
                        if f['clearance']<0 and lineStates[i][0]:
                            lineStates[i]=[0,lineStates[i][1]+1]
                            dirty=True
                        state['trace'].append(f'L{i}')
                        if l['inline']:
                            through=bool(l['empty'])
                        elif l['child']==f['clearance']:
                            lineStates[i]=[1,lineStates[i][1]+1]
                            dirty=True
                            through=False
                        else:
                            child=l['child']
                            state['constructed']+=1+int(descend!=idx)
                            cn=nodes[child]
                            state['retry'] |= bool(cn['clear'] or not cn['intersect'])
                            through,childDirty=visit(child)
                            if childDirty:
                                lineStates[i][1]+=1
                                dirty=True
                            if through:
                                edge('E',child)
                        if not through:
                            if hasOutput and not initialized:
                                output=False
                                initialized=True
                            stop=True
                            break
                    if stop:
                        break
                    if hasOutput and not initialized:
                        state['trace'].append(f'I{idx}')
                        output=bool(n['selfEmpty'])
                        initialized=True
                current=nodes[current]['next']
        if hasOutput and not initialized:
            state['trace'].append(f'F{idx}')
            output=bool(n['empty'])
        separate=n['paddingStart']!=0 or n['paddingEnd']!=0 or any(n[k]!=UNKNOWN and n[k]>0 for k in ['preferred','minimum'])
        if candidate and hasOutput and output and not n['hidden'] and separate:
            output=False
        return output,dirty
    empty,dirty=visit(0,bool(f['output']),bool(f['initialEmpty']))
    pos=max([0]+state['margins'])
    neg=min([0]+state['margins'])
    nums=[pos+neg,pos,neg,int(pos==0 and neg==0),int(empty),int(state['retry']),int(dirty),state['constructed'],state['constructed']]+[x for ls in lineStates for x in ls]
    return ' '.join(map(str,nums))+' |'+''.join(' '+s for s in state['trace'])


def fixtures():
    out=[]
    dimensions=list(itertools.product([0,1,UNKNOWN-1,UNKNOWN],[0,1,UNKNOWN],[0,1],[0,1],[0,1]))
    for i,(preferred,minimum,ps,pe,hidden) in enumerate(dimensions):
        for old,block,root,output in itertools.product([0,1],[0,1],[0,1],[0,1]):
            n=node(start=[-10,0,10][i%3],end=-20,preferred=preferred,minimum=minimum,paddingStart=ps,paddingEnd=pe,hidden=hidden,selfEmpty=old,empty=old,block=block,marginRoot=root)
            out.append(fixture(f'leaf-{i}-{old}{block}{root}{output}',[n],[],'provider-classification',output=output,initialEmpty=i%2))
        for start,end,later in [(10,20,80),(-10,-20,-80),(10,-20,80),(-10,20,-80),(0,0,0)]:
            nodes=[node(),node(start=start,end=end,parent=0,preferred=preferred,minimum=minimum,paddingStart=ps,paddingEnd=pe,hidden=hidden),node(start=later,parent=0,preferred=1)]
            out.append(fixture(f'siblings-{i}-{start}-{end}-{later}',nodes,[line(0,1),line(0,2)],'ordinary-sibling-membership'))
    for positive in ['preferred','minimum','paddingEnd']:
        for margin in [-40,40]:
            nodes=[node(),node(start=10,end=20,parent=0,**{positive:1}),node(start=margin,parent=1),node(start=80,parent=0,preferred=1)]
            out.append(fixture('late-'+positive+str(margin),nodes,[line(0,1),line(1,2),line(0,3)],'late-guard-start-preservation'))
    for inlineEmpty,clearance,output,retry in itertools.product([0,1],[0,1],[0,1],[0,1]):
        out.append(fixture(f'inline-{inlineEmpty}{clearance}{output}{retry}',[node(start=10),node(start=80,parent=0)], [line(0,empty=inlineEmpty,clearance=clearance),line(0,1)],'inline-clearance-tags',output=output,initialRetry=retry))
    for case in ['normal','overflow','next']:
        for clearanceTarget,oldClearance,initialOutput,positive,hidden in itertools.product([0,1],[0,1],[0,1],[0,1],[0,1]):
            nodes=[node(start=10,preferred=positive,hidden=hidden),node(start=80,parent=0,clear=1,intersect=0),node(start=999,next=-1)]
            if case=='normal':
                lines=[line(0,1,clearance=oldClearance)]
                if not clearanceTarget: nodes[1]['selfEmpty']=0
            elif case=='overflow':
                nodes[0]['hasOverflow']=1
                lines=[line(0,1,overflow=1,clearance=oldClearance)]
                if not clearanceTarget: nodes[1]['selfEmpty']=0
            else:
                nodes[0]['next']=2
                lines=[line(2,1,clearance=oldClearance)]
                if not clearanceTarget: nodes[1]['selfEmpty']=0
            out.append(fixture(f'fragment-{case}-{clearanceTarget}{oldClearance}{initialOutput}{positive}{hidden}',nodes,lines,'fragment-output-initialization',clearance=1 if clearanceTarget else -1,initialEmpty=initialOutput))
    for wrapperBlock,wrapperRoot,old,positive,output in itertools.product([0,1],[0,1],[0,1],[0,1],[0,1]):
        nodes=[node(block=0,descend=1,empty=old,selfEmpty=old,preferred=positive),node(parent=0,block=wrapperBlock,marginRoot=wrapperRoot),node(start=40,end=-8,parent=1)]
        out.append(fixture(f'wrapper-{wrapperBlock}{wrapperRoot}{old}{positive}{output}',nodes,[line(1,2,clearance=1)],'wrapper-fallback',output=output))
    for oldSelf,oldFallback,ps in itertools.product([0,1],[0,1],[0,1]):
        out.append(fixture(f'old-output-selection-{oldSelf}{oldFallback}{ps}',[node(selfEmpty=oldSelf,empty=oldFallback,paddingStart=ps)],[],'self-versus-fallback'))
    for domain,withClear in [('dirty-propagation',False),('clearance-stop-propagation',True)]:
        nodes=[node(),node(start=10,parent=0),node(start=-20,parent=1,clear=1),node(start=80,parent=0)]
        out.append(fixture(domain,nodes,[line(0,1),line(1,2,clearance=1),line(0,3)],domain,clearance=2 if withClear else -1))
    for a,b,c,d in [(10,-8,5,0),(-10,8,-5,0),(10,-8,5,-2),(0,-10,0,-5)]:
        out.append(fixture(f'signed-extrema-{a}-{b}-{c}-{d}',[node(),node(start=a,end=b,parent=0),node(start=c,end=d,parent=0)],[line(0,1),line(0,2)],'signed-extrema-retention'))
    for f in out:
        f['original_expected']=oracle(f,False)
        f['candidate_expected']=oracle(f,True)
    return out
