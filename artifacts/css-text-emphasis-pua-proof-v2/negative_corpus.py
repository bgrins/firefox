import itertools
from corpus import case_for


def negative_corpus():
    cases=[]
    for width,direction,vertical,request,runs in itertools.product(
            [-1501,-1500,-1,0,1,1500,1501],[-1,1],[False,True],
            [[0,3],[1,3],[0,1],[1,2],[2,3],[1,1],[3,3]],[[0],[0,2]]):
        case=case_for([0xE000,0xE001,0xE002])
        case.update(glyphs=[[0x10001,[[65,width,0,0]]],[0x50000,[]],[0x800A0043,[]]],
                    range=request,runs=runs,spacing=[[0,0]]*3,vertical=vertical,
                    direction=direction,provider=False,provider_enabled=False,
                    spacing_enabled=False,allocation_failure=False,letter=0,
                    mark_advance=2,point=[0,0])
        cases.append(case)
    return cases + [{**case,"text":[65,66,67]} for case in cases]
