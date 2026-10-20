import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import copy

def rejections(core):
    result=[]
    def add(name,edit,reason):
        c=core.case(name,[core.frame()]);edit(c);result.append((name,c,reason))
    add("unknown-field",lambda c:c.update(extra=1),"case schema")
    add("boolean-action",lambda c:c.update(action=True),"action")
    add("float-coordinate",lambda c:c["frames"][0]["normal"].__setitem__(0,0.5),"signed32")
    add("bool-coordinate",lambda c:c["frames"][0]["normal"].__setitem__(0,True),"signed32")
    add("out-of-range-coordinate",lambda c:c["frames"][0]["normal"].__setitem__(0,core.MAX+1),"signed32")
    add("next-cycle",lambda c:c["frames"][0].update(next=0),"cycle")
    add("parent-cycle",lambda c:c["frames"][0].update(parent=0),"cycle")
    add("wrong-parent-depth",lambda c:c["frames"][0].update(depth=1),"identity")
    add("duplicate-primary",lambda c:c.update(primaries=[0,0]),"primary")
    add("boolean-primary",lambda c:c.update(primaries=[True]),"primary")
    add("bad-rect-sum",lambda c:c["frames"][0]["ignore"].__setitem__(0,[core.MAX,0,1,0]),"signed32")
    add("bad-rect-extent",lambda c:c["frames"][0]["ignore"].__setitem__(0,[core.MIN,0,4294967295,0]),"signed32")
    add("inactive-limit-changed",lambda c:c["frames"][0]["ignore"][0].__setitem__(0,0),"inactive edge provider")
    add("containment-space-changed",lambda c:c["frames"][0]["ignore"][1].__setitem__(0,0),"containment space invariance")
    add("missing-reached-geometry",lambda c:c["frames"][0].update(geometryAvailable=False),"geometry provider unavailable")
    c=core.case("wrong-scroll-relation",[core.frame(15)]);c["scroll"]=[0,0]
    result.append((c["id"],c,"scroll space provider"))
    c=core.case("translation-overflow",[core.frame(8,core.MIN)],2)
    c["frames"][0]["ignore"][0]=core.rect(200,core.HIGH,core.LOW,core.HIGH)
    c["frames"][0]["current_limits"][0]=core.rect(207,core.HIGH,core.LOW,core.HIGH)
    result.append((c["id"],c,"signed32"))
    fs=[core.frame(8,-100),core.frame(8,core.MAX-5)]
    fs[0]["next"]=1;fs[1]["first"]=0
    c=core.case("continuation-add-overflow",fs,3);result.append((c["id"],c,"signed32"))
    c=copy.deepcopy(next(c for c in core.cases() if c["id"]=="nested-update-0-False"));c["id"]="reversed-depth-order";c["primaries"]=[2,0]
    result.append((c["id"],c,"depth order"))
    c=copy.deepcopy(next(c for c in core.cases() if c["id"]=="nested-update-0-False"));c["id"]="individual-continuation-direct";c.update(action=0,target=1)
    result.append((c["id"],c,"first precondition"))
    return result
