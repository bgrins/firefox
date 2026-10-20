import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def body(file, anchor):
    s = (ROOT / 'source' / file).read_text()
    start = s.index(anchor)
    opening = s.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (s[end] == '{') - (s[end] == '}')
        end += 1
    value = s[start:end]
    return value, {'file': file, 'anchor': anchor, 'sha256': hashlib.sha256(value.encode()).hexdigest()}

def generate():
    items = [
      ('nsCoord.h', 'inline float NSAppUnitsToFloatPixels('),
      ('nsCoord.h', 'inline nscoord NSToCoordRound(double'),
      ('nsCoord.h', 'inline nscoord NSToCoordRoundWithClamp(double'),
      ('nsLayoutUtils.cpp', 'static void ConstrainToCoordValues(double& aVal)'),
      ('nsLayoutUtils.cpp', '/* static */ void nsLayoutUtils::ConstrainToCoordValues('),
      ('nsLayoutUtils.h', 'template <typename T>\nnsRect nsLayoutUtils::ScaleThenRoundGfxRectToAppRect('),
      ('DOMRect.cpp', 'static double RoundFloat('),
      ('DOMRect.cpp', 'void DOMRect::SetLayoutRect('),
      ('DOMRect.h', 'void SetRect(float'),
      ('DOMRect.h', 'double Right() const'),
      ('BaseRect.h', 'void Scale(T aXScale, T aYScale)')]
    extracted = [body(*item) for item in items]
    code = [a for a,b in extracted]
    header = r'''
#include <algorithm>
#include <cassert>
#include <cfenv>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#define MOZ_ASSERT assert
#define MOZ_UNLIKELY(x) (x)
using nscoord=int32_t;
constexpr nscoord nscoord_MAX=1073741823, nscoord_MIN=-1073741823;
struct nsRect {
 nscoord x=0,y=0,width=0,height=0;
 nscoord XMost() const { return x+width; }
 nscoord YMost() const { return y+height; }
 void SetWidth(nscoord v) { width=v; }
 void SetHeight(nscoord v) { height=v; }
};
struct Rect {
 using T=float;
 float x,y,width,height;
 float Width() const { return width; }
 float Height() const { return height; }
 void Scale(float v) { Scale(v,v); }
'''
    header += code[10] + '\n};\n'
    header += r'''
struct nsLayoutUtils {
 static void ConstrainToCoordValues(double&,double&);
 template<typename T> static nsRect ScaleThenRoundGfxRectToAppRect(const T&,float);
};
int AppUnitsPerCSSPixel() { return 60; }
struct DOMRect {
 double mX=0,mY=0,mWidth=0,mHeight=0;
 double X() const { return mX; }
 double Width() const { return mWidth; }
 static double NaNSafeMax(double a,double b) { return std::max(a,b); }
 void SetLayoutRect(const nsRect&);
'''
    header += code[8] + '\n' + code[9] + '\n};\n'
    header += '\n'.join(code[:8])
    header += r'''
int main() {
 static_assert(sizeof(float)==4 && sizeof(double)==8);
 static_assert(std::numeric_limits<float>::is_iec559 && std::numeric_limits<float>::digits==24);
 static_assert(std::numeric_limits<double>::is_iec559 && std::numeric_limits<double>::digits==53);
 assert(std::fegetround()==FE_TONEAREST);
 int32_t x,w,f,r;
 std::cout<<std::setprecision(17);
 while(std::cin>>x>>w>>f>>r) {
   Rect input{NSAppUnitsToFloatPixels(x,float(f)),0,
              NSAppUnitsToFloatPixels(w,float(f)),0};
   nsRect a=r ? nsLayoutUtils::ScaleThenRoundGfxRectToAppRect(input,float(f))
              : nsRect{x,0,w,0};
   DOMRect dom;dom.SetLayoutRect(a);
   double b=RoundFloat(a.x*(65536.0/60))* (1.0/65536);
   double e=RoundFloat(a.XMost()*(65536.0/60))* (1.0/65536);
   std::cout<<a.x<<' '<<a.width<<' '<<input.x<<' '<<input.width<<' '
     <<b<<' '<<e<<' '<<dom.mX<<' '<<dom.mWidth<<' '<<dom.Right()<<'\n';
 }
}
'''
    return header, [b for a,b in extracted]

def run(out, reference):
    out.mkdir()
    cpp, bindings = generate()
    (out/'BINDINGS.json').write_text(json.dumps(bindings,indent=2)+'\n')
    variants={'original':cpp,
              'double-dom':cpp.replace('void SetRect(float aX, float aY, float aWidth, float aHeight)',
                                      'void SetRect(double aX, double aY, double aWidth, double aHeight)'),
              'omit-gfx-roundtrip':cpp.replace('nsRect a=r ?', 'nsRect a=false ?'),
              'truncate-appunit':cpp.replace('return nscoord(floor(aValue + 0.5f));', 'return nscoord(aValue);')}
    expected=[reference.pipeline(*row) for row in reference.CASES]
    (out/'CASES.json').write_text(json.dumps(reference.CASES)+'\n')
    (out/'EXPECTED.json').write_text(json.dumps(expected,indent=2)+'\n')
    receipt={}
    for name,text in variants.items():
      if name!='original' and text==cpp: raise RuntimeError('no-op mutant')
      source=out/(name+'.cpp');source.write_text(text)
      for opt in ['0','2']:
        binary=out/(name+'-O'+opt)
        c=subprocess.run(['/usr/bin/clang++','-std=c++17','-O'+opt,'-fsanitize=undefined',
                          '-fno-sanitize-recover=all',str(source),'-o',str(binary)],capture_output=True,text=True)
        (out/(binary.name+'.build.log')).write_text(c.stdout+c.stderr)
        if c.returncode: raise RuntimeError('compile failure')
        r=subprocess.run([str(binary)],input=''.join(' '.join(map(str,c))+'\n' for c in reference.CASES),capture_output=True,text=True)
        (out/(binary.name+'.log')).write_text(r.stdout+r.stderr)
        if r.returncode: raise RuntimeError('native failed')
        rows=[[float(v) for v in line.split()] for line in r.stdout.splitlines()]
        if len(rows)!=len(expected) or any(len(row)!=9 for row in rows): raise RuntimeError('bad rows')
        differences=[i for i,(a,b) in enumerate(zip(rows,expected)) if a!=b]
        if (name=='original') != (not differences): raise RuntimeError('comparison failure '+name+str(differences))
        receipt[binary.name]={'rows':len(rows),'differences':differences}
        binary.unlink()
    return receipt
