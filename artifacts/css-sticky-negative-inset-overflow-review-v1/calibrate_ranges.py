import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("require Python -I -S without optimization")
sys.dont_write_bytecode=True
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def extract(text,signature):
    start=text.index(signature);opening=text.index("{",start);depth=0
    for i in range(opening,len(text)):
        depth+=(text[i]=="{")-(text[i]=="}")
        if depth==0:return text[start:i+1]
    raise ValueError("unclosed selected body")
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/"range-calibration"
    out.mkdir();bindings=[];commands=[];results=[]
    upstream=(ROOT/"upstream/RectAbsolute.h").read_text()
    template=extract(upstream,"template <class T, class Sub, class Point, class Rect>\nstruct BaseRectAbsolute")+";\n"
    bindings.append({"path":"upstream/RectAbsolute.h","signature":"BaseRectAbsolute","sha256":sha(template[:-2].encode())})
    prefix='''#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <string>
#include <type_traits>
#define MOZ_ALWAYS_INLINE inline
using nscoord = int32_t;
static constexpr nscoord nscoord_MAX = 1073741823;
static constexpr nscoord nscoord_MIN = -1073741823;
static constexpr nscoord gUnboundedNegative = nscoord_MIN / 2;
static constexpr nscoord gUnboundedExtent = nscoord_MAX;
static constexpr nscoord gUnboundedPositive = gUnboundedNegative + gUnboundedExtent;
struct nsPoint { nscoord x=0,y=0; };
struct nsRect {
 nscoord x,y,width,height;
 nscoord X() const {return x;} nscoord Y() const {return y;}
 nscoord XMost() const {return x+width;} nscoord YMost() const {return y+height;}
 bool Overflows() const {auto a=int64_t(x)+width,b=int64_t(y)+height;return a<INT32_MIN||a>INT32_MAX||b<INT32_MIN||b>INT32_MAX;}
 void SetLeftEdge(nscoord a) {width=XMost()-a;x=a;}
 void SetRightEdge(nscoord a) {width=a-x;}
 void SetTopEdge(nscoord a) {height=YMost()-a;y=a;}
 void SetBottomEdge(nscoord a) {height=a-y;}
};
'''
    prefix+=template+'''struct nsRectAbsolute : BaseRectAbsolute<nscoord,nsRectAbsolute,nsPoint,nsRect> {
 using BaseRectAbsolute::BaseRectAbsolute;
};
struct nsIFrame {nsPoint normal;nsPoint GetNormalPosition() const{return normal;}};
namespace nsLayoutUtils {nsIFrame* FirstContinuationOrIBSplitSibling(nsIFrame* f){return f;}}
'''
    for role,file,recttype in [("before","before-StickyScrollContainer.cpp","nsRect"),("after","combined-final-StickyScrollContainer.cpp","nsRectAbsolute")]:
        text=(ROOT/"native"/file).read_text();body=extract(text,"void StickyScrollContainer::GetScrollRanges(")
        bindings.append({"path":"native/"+file,"signature":"GetScrollRanges","sha256":sha(body.encode())})
        source=prefix+f'''struct StickyScrollContainer {{
 struct Limits {{{recttype} mStick;nsRect mContain;}};
 Limits limits;
 Limits ComputeStickyLimits(nsIFrame*) const {{return limits;}}
 void GetScrollRanges(nsIFrame*,nsRectAbsolute*,nsRectAbsolute*) const;
}};
'''+body+'''
int main(int argc,char** argv) {
 const bool clamp=argc>1 && std::string(argv[1])=="clamp";
 StickyScrollContainer s;
 nsRect initial{gUnboundedNegative,gUnboundedNegative,gUnboundedExtent,gUnboundedExtent};
'''+('s.limits.mStick=initial;\n' if role=='before' else 's.limits.mStick=nsRectAbsolute::FromRect(initial);\n')+'''
 s.limits.mContain={0,0,6000,59400};
 s.limits.mStick.SetTopEdge(-1073741823);
 s.limits.mStick.SetBottomEdge(clamp ? 1073740223 : 1073747223);
 if(clamp){s.limits.mStick.SetLeftEdge(0);s.limits.mStick.SetRightEdge(0);}
 nsIFrame frame{{0,12000}};
 nsRectAbsolute outer,inner;s.GetScrollRanges(&frame,&outer,&inner);
 std::cout<<outer<<" "<<inner<<"\\n";
}
'''
        cpp=out/(role+".cpp");cpp.write_text(source)
        for mode,flag in [("debug","-O0"),("optimized","-O2")]:
            binary=out/(role+"-"+mode);cmd=["/usr/bin/clang++","-std=c++17",flag,"-fsanitize=undefined","-fno-sanitize-recover=all",str(cpp),"-o",str(binary)]
            proc=subprocess.run(cmd,capture_output=True,text=True);(out/(binary.name+"-compile.log")).write_text(proc.stdout+proc.stderr);commands.append({"command":cmd,"exit":proc.returncode});assert proc.returncode==0
            for case in ["wide","clamp"]:
                cmd=[str(binary),case];proc=subprocess.run(cmd,capture_output=True,text=True);(out/(binary.name+"-"+case+".log")).write_text(proc.stdout+proc.stderr);commands.append({"command":cmd,"exit":proc.returncode})
                expected=(role=="after" and case=="wide")
                assert (proc.returncode==0)==expected
                if not expected:assert "signed integer overflow" in proc.stderr
                results.append({"role":role,"mode":mode,"case":case,"exit":proc.returncode,"expected_success":expected})
    (out/"BINDINGS.json").write_text(json.dumps(bindings,indent=2)+"\n")
    (out/"COMMANDS.json").write_text(json.dumps(commands,indent=2)+"\n")
    (out/"RESULT.json").write_text(json.dumps({"status":"pass","runs":results,"admissions":"Whole frozen GetScrollRanges and actual BaseRectAbsolute template; stable frame/limit inputs, hand-written nsRect facade checked against setters and Overflows. Concrete extracted calibration, not browser or full compiler semantics proof.","clamp_witness":"Preexisting: old and new both overflow outer.Height() inside MoveInsideAndClamp; old stick extent and normalization inputs can all be signed32-defined before this call."},indent=2)+"\n")
    cleanup=[]
    for p in out.iterdir():
        if p.name in [x+"-"+y for x in ["before","after"] for y in ["debug","optimized"]]:
            cleanup.append({"path":p.name,"sha256":sha(p.read_bytes()),"bytes":p.stat().st_size});p.unlink()
    (out/"CLEANUP.json").write_text(json.dumps(cleanup,indent=2)+"\n")
    print(json.dumps({"status":"pass","runs":len(results)}))
if __name__=="__main__":main()
