import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S without optimization")
import itertools
import json

def physical(mode, point, container, size):
    vertical, reverse_inline, reverse_block = mode
    i, b = point
    w, h = container[0] - size[0], container[1] - size[1]
    if vertical:
        return (w-b if reverse_block else b, h-i if reverse_inline else i)
    return (w-i if reverse_inline else i, b)

def logical(mode, point, container, size):
    vertical, reverse_inline, reverse_block = mode
    x, y = point
    w, h = container[0] - size[0], container[1] - size[1]
    if vertical:
        return (h-y if reverse_inline else y, w-x if reverse_block else x)
    return (w-x if reverse_inline else x, y)

def add(a,b): return (a[0]+b[0],a[1]+b[1])

rows=[]
mutants={"used_predecessor_plus_current_offset":0,"current_conversion_using_predecessor_size":0,
         "normal_without_relative_finish":0,"absent_predecessor_property":0}
modes=[(False,False,False),(False,True,False),(True,False,False),
       (True,True,False),(True,False,True),(True,True,True)]
for mode, oldsize, size, oldoff, offset in itertools.product(modes,[(73,91),(117,0)],[(43,0),(81,29)],[(0,0),(17,-11)],[(-13,7),(0,0),(23,-5)]):
    container=(251,317)
    normal=physical(mode,(31,19),container,oldsize)
    used=add(normal,oldoff)
    i=logical(mode,normal,container,oldsize)[0]
    stored=physical(mode,(i,0),container,size)
    changed=add(stored,offset)
    result=physical(mode,logical(mode,changed,container,size),container,size)
    # Independent per-axis signed origin equations, before the visual offset.
    if mode[0]:
        expected=(container[0]-size[0] if mode[2] else 0,
                  container[1]-size[1]-31 if mode[1] else 31)
    else:
        expected=(container[0]-size[0]-31 if mode[1] else 31,0)
    assert stored==expected
    assert result==add(expected,offset)
    assert add(stored,(0,0))==expected
    wrong_i=logical(mode,used,container,oldsize)[0]
    mutant=add(physical(mode,(wrong_i,0),container,size),offset)
    mutants['used_predecessor_plus_current_offset']+=mutant!=result
    mutants['absent_predecessor_property']+=mutant!=result
    mutants['current_conversion_using_predecessor_size']+=add(physical(mode,(i,0),container,oldsize),offset)!=result
    mutants['normal_without_relative_finish']+=stored!=result
    rows.append({'mode':mode,'previous_size':oldsize,'current_size':size,'previous_offset':oldoff,'current_offset':offset,'normal':stored,'used':result})
assert all(v>0 for v in mutants.values())
print(json.dumps({'kind':'finite independent integer-coordinate model, not native execution or universal proof','rows':len(rows),'distinguished_mutants':mutants,'results':rows},indent=2))
