import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import hashlib,itertools,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
AUTO=1073741823
LOW=-1073741823
SIGNATURE="static nscoord ComputeStickySideOffset("
def sha(data):return hashlib.sha256(data).hexdigest()
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

def cases():
    values=[LOW,-100,-1,0,1,100,AUTO-2,AUTO-1,AUTO]
    result=[{"side":side,"auto":automatic,"resolved":value,"basis":basis}
       for side,automatic,value,basis in itertools.product(range(4),[False,True],values,[0,60,6000])]
    result += [{"side":side,"auto":False,"resolved":value,"basis":AUTO}
       for side,value in itertools.product(range(4),[LOW,LOW+1,AUTO-3,AUTO])]
    result += [{"side":side,"auto":True,"resolved":AUTO,"basis":AUTO} for side in range(4)]
    return result

def validate(c):
    if type(c)!=dict or set(c)!={"side","auto","resolved","basis"}:raise ValueError("schema")
    if type(c["side"])!=int or c["side"] not in range(4):raise ValueError("side")
    if type(c["auto"])!=bool:raise ValueError("auto")
    if type(c["resolved"])!=int or not LOW<=c["resolved"]<=AUTO:raise ValueError("resolved numeric provider")
    if type(c["basis"])!=int or not 0<=c["basis"]<=AUTO:raise ValueError("percentage basis provider")

def oracle(c,old=False):
    if c["auto"]:return [AUTO,c["side"],1,0,-1]
    n=c["resolved"]
    if not old and n==AUTO:n-=1
    return [n,c["side"],1,1,c["basis"]]

def native(variant):
    bodies={};bindings=[]
    for name in ["before","candidate","candidate-formatted"]:
        text=(ROOT/"inputs"/(name+".cpp")).read_text();body,a,b=extract(text,SIGNATURE);bodies[name]=body
        bindings.append({"path":"inputs/"+name+".cpp","start_byte":a,"end_byte":b,"sha256":sha(body.encode())})
    old_return="return nsLayoutUtils::ComputeCBDependentValue(aPercentBasis,\n                                                side->AsLengthPercentage());"
    new_return="return std::min(\n      NS_AUTOOFFSET - 1,\n      nsLayoutUtils::ComputeCBDependentValue(aPercentBasis,\n                                            side->AsLengthPercentage()));"
    old,new,formatted=[bodies[n] for n in ["before","candidate","candidate-formatted"]]
    if old.count(old_return)!=1 or new.count(new_return)!=1:raise ValueError("expected source return")
    if old.replace(old_return,"// Reserve NS_AUTOOFFSET for actual auto insets.\n  "+new_return)!=new:raise ValueError("producer-only body delta")
    before=(ROOT/"inputs/before.cpp").read_text();candidate=(ROOT/"inputs/candidate.cpp").read_text();final=(ROOT/"inputs/candidate-formatted.cpp").read_text()
    if before.replace(old,new)!=candidate or candidate.replace(new,formatted)!=final:raise ValueError("whole-file delta")
    if re.sub(r'\s+','',new)!=re.sub(r'\s+','',formatted):raise ValueError("format-only transfer")
    mutations={
      "auto_reserved_too":new.replace("return NS_AUTOOFFSET;","return NS_AUTOOFFSET - 1;"),
      "maximum_instead_of_minimum":new.replace("std::min(","std::max("),
      "reserve_two_units":new.replace("NS_AUTOOFFSET - 1","NS_AUTOOFFSET - 2"),
      "negative_values_lost":new.replace(new_return,"return std::max(nscoord(0), "+new_return.removeprefix("return ").removesuffix(";")+");"),
      "wrong_side":new.replace("      aSide, AnchorPosOffsetResolutionParams","      static_cast<Side>((aSide + 1) % 4), AnchorPosOffsetResolutionParams"),
    }
    if any(v==new for v in mutations.values()):raise ValueError("mutant unchanged")
    body=bodies[variant] if variant in bodies else mutations[variant]
    prefix=(ROOT/"native/prefix.cpp").read_text()
    coord=(ROOT/"inputs/nsCoord.h").read_text();layout=(ROOT/"inputs/LayoutConstants.h").read_text()
    constants=[]
    for file,text,pattern in [("nsCoord.h",coord,r'using nscoord = int32_t;'),("nsCoord.h",coord,r'inline constexpr nscoord nscoord_MAX = [^;]+;'),("nsCoord.h",coord,r'inline constexpr nscoord nscoord_MIN = [^;]+;'),("LayoutConstants.h",layout,r'inline constexpr nscoord NS_UNCONSTRAINEDSIZE = [^;]+;'),("LayoutConstants.h",layout,r'inline constexpr nscoord NS_AUTOOFFSET = [^;]+;')]:
        matches=list(re.finditer(pattern,text))
        if len(matches)!=1:raise ValueError("constant uniqueness")
        m=matches[0];constants.append(m[0]);bindings.append({"path":"inputs/"+file,"start_byte":len(text[:m.start()].encode()),"end_byte":len(text[:m.end()].encode()),"sha256":sha(m[0].encode())})
    prefix=prefix.replace("using nscoord = int32_t;\ninline constexpr nscoord nscoord_MAX = (1 << 30) - 1;\ninline constexpr nscoord NS_AUTOOFFSET = nscoord_MAX;","\n".join(constants)+"\nstatic_assert(nscoord_MAX == 1073741823 && nscoord_MIN == -1073741823 && NS_AUTOOFFSET == nscoord_MAX);")
    return prefix+body+(ROOT/"native/suffix.cpp").read_text(),bindings

def negative_cases():
    base={"side":0,"auto":False,"resolved":0,"basis":0}
    return [(key+"-"+str(v),{**base,key:v},reason) for key,v,reason in [
      ("side",4,"side"),("side",-1,"side"),("side",True,"side"),
      ("auto",1,"auto"),("resolved",AUTO+1,"resolved numeric provider"),
      ("resolved",LOW-1,"resolved numeric provider"),("resolved",True,"resolved numeric provider"),
      ("basis",-1,"percentage basis provider"),("basis",AUTO+1,"percentage basis provider"),
      ("basis",True,"percentage basis provider"),("extra",0,"schema")]]

def provider():
    text=(ROOT/"inputs/nsLayoutUtils.h").read_text()
    body,a,b=extract(text,"static nscoord ComputeCBDependentValue(nscoord aPercentBasis,\n                                         const LengthPercentage& aCoord)")
    return {"path":"inputs/nsLayoutUtils.h","start_byte":a,"end_byte":b,"sha256":sha(body.encode()),"body":body,"executed":False,"admission":"Numeric Resolve and the unconstrained-basis/HasPercent precondition remain provider obligations."}
