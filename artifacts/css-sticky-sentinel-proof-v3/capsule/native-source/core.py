import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import copy, hashlib, itertools, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
AUTO=1073741823
LOW=-536870911
HIGH=536870912
MIN=-2147483648
MAX=2147483647
SIGNATURES=[
 "nsPoint StickyScrollContainer::ComputePosition(nsIFrame* aFrame) const",
 "nsPoint StickyScrollContainer::ComputePositionIgnoringScrolling(",
 "nsPoint StickyScrollContainer::DoComputePosition(",
 "nsPoint StickyScrollContainer::ComputeTranslationIgnoringScrolling(",
 "bool StickyScrollContainer::IsStuckInYDirection(nsIFrame* aFrame) const",
 "void StickyScrollContainer::PositionContinuations(nsIFrame* aFrame)",
 "void StickyScrollContainer::UpdatePositions(nsPoint aScrollPosition,",
]
def sha(data): return hashlib.sha256(data).hexdigest()
def extract(text,signature):
    if text.count(signature)!=1: raise ValueError("signature uniqueness: "+signature)
    start=text.index(signature)
    scrub=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:" "*len(m[0]),text)
    opening=scrub.index("{",start);depth=0
    for end in range(opening,len(scrub)):
        if scrub[end]=="{":depth+=1
        elif scrub[end]=="}":
            depth-=1
            if depth==0:
                result=text[start:end+1]
                if 'R"' in result:raise ValueError("unsupported raw string")
                return result,len(text[:start].encode()),len(text[:end+1].encode())
    raise ValueError("unclosed function")

def translation(variant):
    version="before.cpp" if variant=="old" else "candidate.cpp"
    source=(ROOT/"inputs"/version).read_text()
    bodies=[];bindings=[]
    for signature in SIGNATURES:
        body,start,end=extract(source,signature)
        bodies.append(body)
        bindings.append({"file":"inputs/"+version,"signature":signature,"start_byte":start,"end_byte":end,"sha256":sha(body.encode())})
    original=bodies[2]
    if variant=="restored":bodies[2]=extract((ROOT/"inputs/before.cpp").read_text(),SIGNATURES[2])[0]
    elif variant=="all_auto_only":
        s=original
        for edge in ["top","bottom","left","right"]:
            pattern=r'  if \(computedOffsets->'+edge+r' != NS_AUTOOFFSET\) \{\n(    position\.[xy] = [^\n]+\n)  \}'
            s,n=re.subn(pattern,lambda m:m[1][2:].rstrip(),s);assert n==1
        marker="  // For each sticky direction"
        s=s.replace(marker,"  if (computedOffsets->top == NS_AUTOOFFSET && computedOffsets->bottom == NS_AUTOOFFSET && computedOffsets->left == NS_AUTOOFFSET && computedOffsets->right == NS_AUTOOFFSET) return position;\n\n"+marker)
        bodies[2]=s
    elif variant=="numeric_edges":
        s=original
        for edge,expr in [("top","stick.y != gUnboundedNegative"),("bottom","stick.YMost() != gUnboundedPositive"),("left","stick.x != gUnboundedNegative"),("right","stick.XMost() != gUnboundedPositive")]:s=s.replace("computedOffsets->"+edge+" != NS_AUTOOFFSET",expr)
        bodies[2]=s
    elif variant=="swapped_masks":
        bodies[2]=re.sub(r'computedOffsets->(top|bottom|left|right)(?= != NS_AUTOOFFSET)',lambda m:"computedOffsets->"+{"top":"bottom","bottom":"top","left":"right","right":"left"}[m[1]],original)
    elif variant=="effective_activation":
        bodies[2]=re.sub(r'computedOffsets->(top|bottom|left|right)(?= != NS_AUTOOFFSET)',lambda m:"(computedOffsets->"+m[1]+" == NS_AUTOOFFSET ? 0 : computedOffsets->"+m[1]+")",original)
    elif variant=="missing_finite_clamp":
        oldbody=extract((ROOT/"inputs/before.cpp").read_text(),SIGNATURES[2])[0]
        assignments="\n".join("  "+s for s in oldbody.splitlines() if s.startswith("  position."))
        bodies[2]=original.replace("  if (!computedOffsets) {\n    return position;\n  }","  if (!computedOffsets) {\n"+assignments+"\n    return position;\n  }")
    elif variant=="reordered":
        s=original
        for near,far in [("top","bottom"),("left","right")]:
            a=re.search(r'  if \(computedOffsets->'+near+r' != NS_AUTOOFFSET\) \{\n[^\n]+\n  \}',s)[0]
            b=re.search(r'  if \(computedOffsets->'+far+r' != NS_AUTOOFFSET\) \{\n[^\n]+\n  \}',s)[0]
            assert a+"\n"+b in s;s=s.replace(a+"\n"+b,b+"\n"+a)
        bodies[2]=s
    elif variant not in ["old","new"]:raise ValueError("variant")
    if variant not in ["old","new"]:assert bodies[2]!=original
    facade=(ROOT/"native/facade.hpp").read_text()
    coord=(ROOT/"inputs/nsCoord.h").read_text()
    constants="\n".join(re.search(p,coord)[0] for p in [r'using nscoord = int32_t;',r'inline constexpr nscoord nscoord_MAX = [^;]+;',r'inline constexpr nscoord nscoord_MIN = [^;]+;'])
    layout=(ROOT/"inputs/LayoutConstants.h").read_text()
    constants+="\n"+"\n".join(re.search(r'inline constexpr nscoord '+n+r' = [^;]+;',layout)[0] for n in ["NS_UNCONSTRAINEDSIZE","NS_AUTOOFFSET"])
    facade=facade.replace("// EXTRACTED_CONSTANTS",constants)
    rect=(ROOT/"inputs/BaseRect.h").read_text()
    methods=[]
    for n in ["XMost","YMost"]:
        body,start,end=extract(rect,"MOZ_ALWAYS_INLINE T "+n+"() const")
        methods.append(body);bindings.append({"file":"inputs/BaseRect.h","signature":n,"start_byte":start,"end_byte":end,"sha256":sha(body.encode())})
    facade=facade.replace("// EXTRACTED_FAR_METHODS","\n".join(methods))
    limits_constants=re.search(r'static constexpr nscoord gUnboundedNegative =[\s\S]*?gUnboundedNegative \+ gUnboundedExtent;',source)[0]
    provider='''
StickyScrollContainer::StickyLimits StickyScrollContainer::ComputeStickyLimits(nsIFrame* f,StickyLimitSpace space) const {
  event("limits:"+std::to_string(f->id)+":"+(space==StickyLimitSpace::IgnoreCurrentScroll?"ignore":"current"));
  if(!f->geometryAvailable)throw std::runtime_error("unavailable geometry");
  MOZ_ASSERT(nsLayoutUtils::IsFirstContinuationOrIBSplitSibling(f));
  const nsMargin* offsets=f->GetProperty(nsIFrame::ComputedOffsetProperty());
  if(!offsets) {nsRect r(gUnboundedNegative,gUnboundedNegative,gUnboundedExtent,gUnboundedExtent);return {r,r};}
  if(space==StickyLimitSpace::IgnoreCurrentScroll)return {f->ignoreStick,f->ignoreContain};
  return {f->currentStick,f->currentContain};
}
'''
    extra=[]
    for file,sig in [("nsIFrameInlines.h","nsPoint nsIFrame::GetNormalPosition(bool* aHasProperty) const"),("nsIFrame.cpp","void nsIFrame::SetPosition(const nsPoint& aPt)"),("nsIFrame.cpp","nsPoint nsIFrame::GetPositionIgnoringScrollingAndSticky() const")]:
        body,start,end=extract((ROOT/"inputs"/file).read_text(),sig);extra.append(body)
        bindings.append({"file":"inputs/"+file,"signature":sig,"start_byte":start,"end_byte":end,"sha256":sha(body.encode())})
    result=facade+"\nnamespace mozilla {\n"+limits_constants+"\nstatic_assert(NS_AUTOOFFSET == 1073741823 && gUnboundedNegative == -536870911 && gUnboundedPositive == 536870912);\n"+provider+"\n\n".join(bodies)+"\n}\nusing mozilla::StickyScrollContainer;\n"+"\n".join(extra)+"\n"+(ROOT/"native/driver.cpp").read_text()
    return result,bindings

def rect(xlo,xhi,ylo,yhi):return [xlo,ylo,xhi-xlo,yhi-ylo]
def offsets(mask):return [0 if mask&(1<<i) else AUTO for i in range(4)]
def frame(mask=0,normal=0):
    o=offsets(mask)
    xlo=-50 if mask&8 else LOW;xhi=50 if mask&2 else HIGH
    ylo=-50 if mask&1 else LOW;yhi=50 if mask&4 else HIGH
    return {"first":0,"next":-1,"parent":-2,"depth":0,"hadNormal":True,"sticky":True,"hasContainer":True,"geometryAvailable":True,"normal":[normal,normal],"current":[normal+3,normal+5],"fallback":[17,19],"offsets":o,"recomputed":o.copy(),"ignore":[rect(xlo,xhi,ylo,yhi),rect(-900000000,900000000,-900000000,900000000)],"current_limits":[rect(xlo+7 if mask&8 else xlo,xhi+7 if mask&2 else xhi,ylo+11 if mask&1 else ylo,yhi+11 if mask&4 else yhi),rect(-900000000,900000000,-900000000,900000000)]}
def case(name,frames,action=0,target=0,reflow=False,primaries=None):
    return {"id":name,"action":action,"target":target,"reflow":reflow,"scroll":[7,11],"primaries":[0] if primaries is None else primaries,"frames":frames}
def cases():
    result=[]
    for mask,normal,action in itertools.product(range(16),[0,100,700000000,-700000000,LOW,HIGH],range(7)):
        result.append(case(f"mask{mask}-normal{normal}-action{action}",[frame(mask,normal)],action))
    for normal,action,had in itertools.product([0,700000000,-700000000],range(7),[False,True]):
        f=frame(0,normal);f["offsets"]=None;f["hadNormal"]=had
        result.append(case(f"missing-{normal}-{action}-{had}",[f],action))
    for mask in range(16):
        for reflow in [False,True]:
            fs=[frame(mask,700000000),frame(mask,700000040),frame(15-mask,-700000000),frame(15-mask,-699999960)]
            for i,f in enumerate(fs):f.update(first=i//2*2,next=i+1 if i%2==0 else -1,parent=-2 if i<2 else 0,depth=i//2)
            result.append(case(f"nested-update-{mask}-{reflow}",fs,4,reflow=reflow,primaries=[0,2]))
            result.append(case(f"continuation-translation-{mask}-{reflow}",copy.deepcopy(fs),2,target=3,primaries=[0,2]))
    for action in [0,1,2,3,4,5,6]:
        for had in [False,True]:
            f=frame(0,700000000);f["hadNormal"]=had
            if action in [3,4] and not had:f["geometryAvailable"]=False
            result.append(case(f"missing-normal-{action}-{had}",[f],action))
    for action in [0,1,2,3,4,5,6]:
        f=frame(4,700000000);f["offsets"][2]=-536870822
        f["ignore"][0]=rect(LOW,HIGH,LOW,HIGH);f["current_limits"][0]=rect(LOW,HIGH,LOW,HIGH)
        c=case(f"explicit-far-collision-{action}",[f],action);c["scroll"]=[0,0];result.append(c)
        f=frame(1,-700000000);f["offsets"][0]=LOW
        f["ignore"][0]=rect(LOW,HIGH,LOW,HIGH);f["current_limits"][0]=rect(LOW,HIGH,LOW,HIGH)
        c=case(f"explicit-near-collision-{action}",[f],action);c["scroll"]=[0,0];result.append(c)
        f=frame(15,0);f["ignore"][0]=rect(10,-10,10,-10);f["current_limits"][0]=rect(10,-10,10,-10)
        c=case(f"contradiction-{action}",[f],action);c["scroll"]=[0,0];result.append(c)
    for has_container,sticky in itertools.product([False,True],[False,True]):
        f=frame(15,100);f["hasContainer"]=has_container;f["sticky"]=sticky
        result.append(case(f"frame-fallback-{has_container}-{sticky}",[f],5))
    for mask in [0,1,2,4,8,15]:
        f=frame(mask,700000000);f["offsets"]=None
        result.append(case(f"reflow-installs-offsets-{mask}",[f],4,reflow=True))
    for action in range(7):
        for edge,mask,normal in [("left",8,-700000000),("right",2,700000000)]:
            f=frame(mask,normal)
            f["offsets"][3 if mask==8 else 1]=LOW if mask==8 else -536870822
            f["ignore"][0]=rect(LOW,HIGH,LOW,HIGH);f["current_limits"][0]=rect(LOW,HIGH,LOW,HIGH)
            c=case(f"explicit-{edge}-collision-{action}",[f],action);c["scroll"]=[0,0];result.append(c)
        for normal in [MIN,MAX-5]:
            result.append(case(f"signed-boundary-{normal}-{action}",[frame(0,normal)],action))
    for action in [3,4,5]:
        fs=[frame(15,100),frame(15,140)]
        fs[0]["next"]=1;fs[1]["first"]=0;fs[1]["hadNormal"]=False
        result.append(case(f"continuation-missing-normal-{action}",fs,action,target=1 if action==5 else 0))
    for had in [False,True]:
        f=frame(15,700000000);f["recomputed"]=None;f["hadNormal"]=had
        result.append(case(f"reflow-removes-offsets-{had}",[f],4,reflow=True))
    return result

def machine(v):
    if type(v)!=int or not MIN<=v<=MAX:raise ValueError("signed32")
    return v
def validate(c):
    if set(c)!={"id","action","target","reflow","scroll","primaries","frames"}:raise ValueError("case schema")
    if not isinstance(c["id"],str) or not re.fullmatch(r'[A-Za-z0-9_-]+',c["id"]):raise ValueError("id")
    if type(c["action"])!=int or c["action"] not in range(7) or type(c["reflow"])!=bool:raise ValueError("action")
    fs=c["frames"]
    if not isinstance(fs,list):raise ValueError("frames")
    n=len(fs)
    if not 1<=n<=8 or type(c["target"])!=int or c["target"] not in range(n):raise ValueError("target")
    def point(v):
        if not isinstance(v,list) or len(v)!=2:raise ValueError("point")
        for x in v:machine(x)
    point(c["scroll"])
    keys=set(frame())
    for i,f in enumerate(fs):
        if not isinstance(f,dict) or set(f)!=keys:raise ValueError("frame schema")
        for name in ["hadNormal","sticky","hasContainer","geometryAvailable"]:
            if type(f[name])!=bool:raise ValueError("bool")
        for name in ["normal","current","fallback"]:point(f[name])
        for name in ["offsets","recomputed"]:
            if f[name] is not None:
                if not isinstance(f[name],list) or len(f[name])!=4:raise ValueError("offset length")
                for v in f[name]:machine(v)
        for name in ["first","next","parent","depth"]:
            if type(f[name])!=int:raise ValueError("identity")
        if not 0<=f["first"]<n or f["next"] not in [-1,*range(n)] or f["parent"] not in [-2,*range(n)] or not 0<=f["depth"]<n:raise ValueError("identity")
        for name in ["ignore","current_limits"]:
            if not isinstance(f[name],list) or len(f[name])!=2:raise ValueError("limits")
            for r in f[name]:
                if not isinstance(r,list) or len(r)!=4:raise ValueError("rect")
                for x in r:machine(x)
                machine(r[0]+r[2]);machine(r[1]+r[3])
        if fs[f["first"]]["first"]!=f["first"]:raise ValueError("canonical")
        for link in ["next","parent"]:
            seen={i};j=f[link]
            while j>=0:
                if j in seen:raise ValueError("cycle")
                seen.add(j);j=fs[j][link]
        actual_depth=0;j=f["parent"]
        while j>=0:actual_depth+=1;j=fs[j]["parent"]
        if f["depth"]!=actual_depth:raise ValueError("actual parent depth")
        j=f["first"];chain=[]
        while j>=0:chain.append(j);j=fs[j]["next"]
        if i not in chain or any(fs[j]["first"]!=f["first"] for j in chain):raise ValueError("chain membership")
        if any(fs[j]["parent"]!=f["parent"] for j in chain):raise ValueError("continuation parent")
    ps=c["primaries"]
    if not isinstance(ps,list):raise ValueError("primaries")
    if any(type(i)!=int or i not in range(n) or fs[i]["first"]!=i for i in ps) or len(ps)!=len(set(ps)):raise ValueError("primary")
    if [fs[i]["depth"] for i in ps]!=sorted(fs[i]["depth"] for i in ps):raise ValueError("depth order")
    if c["action"] in [0,1,3,6] and fs[c["target"]]["first"]!=c["target"]:raise ValueError("first precondition")
    for i,f in enumerate(fs):
        o=f["recomputed"] if c["action"]==4 and c["reflow"] and i in ps else f["offsets"]
        if o is None:continue
        if f["ignore"][1]!=f["current_limits"][1]:raise ValueError("containment space invariance")
        for axis,near,far in [(0,3,1),(1,0,2)]:
            a,b=f["ignore"][0],f["current_limits"][0]
            for index,offset_index,sentinel in [(axis,near,LOW),(axis+2,far,HIGH)]:
                zero=a[axis] if index==axis else a[axis]+a[axis+2]
                current=b[axis] if index==axis else b[axis]+b[axis+2]
                if o[offset_index]==AUTO:
                    if zero!=sentinel or current!=sentinel:raise ValueError("inactive edge provider")
                elif current!=zero+c["scroll"][axis]:raise ValueError("scroll space provider")
    oracle(c,"old");oracle(c,"new")

def oracle(case,version):
    c=copy.deepcopy(case);fs=c["frames"];n=len(fs);trace=[]
    def normal(i):
        f=fs[i];trace.append(f"normal:{i}:{int(f['hadNormal'])}")
        return f["normal"][:] if f["hadNormal"] else f["current"][:]
    def prop(i):
        trace.append(f"offset:{i}:{int(fs[i]['offsets'] is not None)}");return fs[i]["offsets"]
    def canonical(i):
        j=fs[i]["first"];trace.append(f"first:{i}:{j}");return j
    def pos(i,space):
        f=fs[i];trace.append(f"limits:{i}:{space}")
        if not f["geometryAvailable"]:raise ValueError("geometry provider unavailable")
        o=prop(i)
        if o is None:r=[LOW,LOW,AUTO,AUTO];stick,contain=r,r
        else:stick,contain=f["ignore" if space=="ignore" else "current_limits"]
        v=normal(i)
        if version=="new":o=prop(i)
        if version=="new" and o is None:return v
        for axis,near,far in [(0,3,1),(1,0,2)]:
            active_near=version=="old" or o[near]!=AUTO
            active_far=version=="old" or o[far]!=AUTO
            # Independent interval projection, with the source's far-priority convention for contradictory intervals.
            lower=min(stick[axis],contain[axis]+contain[axis+2]) if active_near else MIN
            upper=max(stick[axis]+stick[axis+2],contain[axis]) if active_far else MAX
            v[axis]=upper if lower>upper or v[axis]>upper else lower if v[axis]<lower else v[axis]
            machine(v[axis])
        return v
    def translation(i):
        j=canonical(i);p=pos(j,"ignore");q=normal(j);return [machine(p[a]-q[a]) for a in range(2)]
    def continuation(i):
        q=normal(i)
        if not fs[i]["hadNormal"]:return
        p=pos(i,"current");delta=[machine(p[a]-q[a]) for a in range(2)]
        j=i
        while j>=0:
            z=normal(j);value=[machine(z[a]+delta[a]) for a in range(2)]
            if value!=fs[j]["current"]:fs[j]["current"]=value;trace.append(f"set:{j}:{value[0]}:{value[1]}")
            nxt=fs[j]["next"];trace.append(f"next:{j}:{nxt}");j=nxt
    action=c["action"];i=c["target"];value=None
    if action in [0,1]:value=pos(i,"current" if action==0 else "ignore")
    elif action==2:value=translation(i)
    elif action==3:continuation(i)
    elif action==4:
        subtree=n if c["reflow"] else -1;trace.append(f"subtree:{subtree}");trace.append("order"+"".join(":"+str(j) for j in c["primaries"]))
        for j in c["primaries"]:
            if c["reflow"]:trace.append(f"recompute:{j}");fs[j]["offsets"]=fs[j]["recomputed"]
            continuation(j)
            parent=fs[j]["parent"];parent=n if parent==-2 else parent
            if parent!=subtree:
                while parent>=0:
                    trace.append(f"overflow:{parent}")
                    nxt=-1 if parent==n else fs[parent]["next"]
                    trace.append(f"next:{parent}:{nxt}");parent=nxt
        trace.append("flush")
    elif action==5:
        f=fs[i]
        if f["sticky"]:trace.append(f"container:{i}")
        if f["sticky"] and f["hasContainer"]:
            q=normal(i);delta=translation(i);value=[machine(q[a]+delta[a]) for a in range(2)]
        else:trace.append(f"fallback:{i}");value=f["fallback"][:]
    elif action==6:
        p=pos(i,"current");q=normal(i);value=[int(p[1]!=q[1]),0]
    return {"value":value,"frames":[f["current"] for f in fs],"trace":trace}

def encode(cases):
    lines=[str(len(cases))]
    for c in cases:
        validate(c);fs=c["frames"]
        words=[c["action"],c["target"],int(c["reflow"]),len(fs),len(c["primaries"]),*c["scroll"]]
        for f in fs:
            words += [f[k] for k in ["first","next","parent","depth"]]+[int(f[k]) for k in ["hadNormal","sticky","hasContainer","geometryAvailable"]]
            for k in ["normal","current","fallback"]:words+=f[k]
            for k in ["offsets","recomputed"]:words += [int(f[k] is not None)]+(f[k] if f[k] is not None else [AUTO]*4)
            for k in ["current_limits","ignore"]:
                for r in f[k]:words+=r
        words+=c["primaries"];lines.append(" ".join(map(str,words)))
    return "\n".join(lines)+"\n"

def providers():
    selection=[
      ("candidate.cpp","StickyScrollContainer::StickyLimits StickyScrollContainer::ComputeStickyLimits("),
      ("candidate.cpp","void StickyScrollContainer::ComputeStickyOffsets(nsIFrame* aFrame)"),
      ("nsLayoutUtils.cpp","nsIFrame* nsLayoutUtils::FirstContinuationOrIBSplitSibling("),
      ("nsLayoutUtils.cpp","nsIFrame* nsLayoutUtils::GetNextContinuationOrIBSplitSibling("),
      ("nsLayoutUtils.cpp","bool nsLayoutUtils::IsFirstContinuationOrIBSplitSibling("),
      ("DepthOrderedFrameList.cpp","void DepthOrderedFrameList::BuildSortedList() const"),
      ("DepthOrderedFrameList.h","auto IterFromShallowest() const"),
      ("OverflowChangedTracker.h","void AddFrame(nsIFrame* aFrame, ChangeKind aChangeKind)"),
      ("OverflowChangedTracker.h","void SetSubtreeRoot(const nsIFrame* aSubtreeRoot)"),
      ("OverflowChangedTracker.h","void Flush()"),
    ]
    result=[]
    for file,signature in selection:
        body,start,end=extract((ROOT/"inputs"/file).read_text(),signature)
        result.append({"file":"inputs/"+file,"signature":signature,"start_byte":start,"end_byte":end,"sha256":sha(body.encode()),"body":body,"executed":False})
    return result
