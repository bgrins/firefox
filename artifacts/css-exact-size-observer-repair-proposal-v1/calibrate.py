import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def extract(text, signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


helper = extract((ROOT / 'candidate/nsLayoutUtils.cpp').read_text(),
                 'static Maybe<nsRect> GetUntransformedRectToAncestor(')
dom = extract((ROOT / 'candidate/DOMRect.cpp').read_text(),
              'void DOMRect::SetLayoutRect(const nsRect& aLayoutRect)')
prefix = '''#include <cstdint>
#include <optional>
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include "mozilla/CheckedInt.h"
using mozilla::CheckedInt;
using nscoord = int32_t;
constexpr nscoord nscoord_MAX = (1<<30)-1;
constexpr nscoord nscoord_MIN = -nscoord_MAX;
constexpr unsigned NS_FRAME_SVG_LAYOUT = 1;
template<typename T> using Maybe=std::optional<T>;
auto Nothing() { return std::nullopt; }
template<typename T> auto Some(T value) { return Maybe<T>(value); }
struct nsRect {
 nscoord x,y,width,height;
 nsRect(nscoord a,nscoord b,nscoord c,nscoord d):x(a),y(b),width(c),height(d){}
 nscoord XMost() const { return x+width; }
 nscoord YMost() const { return y+height; }
};
struct Point {nscoord x,y;};
struct nsIFrame {
 const nsIFrame* parent=nullptr;
 int context=1;
 bool transformed=false,svgText=false;
 unsigned states=0;
 Point position{0,0};
 const nsIFrame* GetParent() const { return parent; }
 int PresContext() const { return context; }
 bool IsTransformed() const { return transformed; }
 bool IsInSVGTextSubtree() const { return svgText; }
 bool HasAnyStateBits(unsigned bits) const { return states&bits; }
 Point GetPosition() const { return position; }
};
static int AppUnitsPerCSSPixel() { return 60; }
static double RoundFloat(double value) { return floor(value+0.5); }
struct DOMRect {
 double x,y,width,height;
 void SetX(double v){x=v;} void SetY(double v){y=v;}
 void SetWidth(double v){width=v;} void SetHeight(double v){height=v;}
 void SetRect(float a,float b,float c,float d){x=a;y=b;width=c;height=d;}
 void SetLayoutRect(const nsRect&);
};
static void require(bool value, int id) { if(!value) {printf("FAIL %d\\n",id);exit(1);} }
'''
main = '''
int main(){
 nsIFrame root,mid,leaf;
 mid.parent=&root; mid.position={700,1100};
 leaf.parent=&mid; leaf.position={-8383188,-1100};
 nsRect box(0,0,8388488,600);
 auto result=GetUntransformedRectToAncestor(&leaf,box,&root);
 require(result && result->x==-8382488 && result->y==0 && result->XMost()==6000,1);
 DOMRect observed;
 observed.SetLayoutRect(*result);
 require(observed.x+observed.width==100,2);
 leaf.transformed=true;require(!GetUntransformedRectToAncestor(&leaf,box,&root),3);leaf.transformed=false;
 mid.transformed=true;require(!GetUntransformedRectToAncestor(&leaf,box,&root),4);mid.transformed=false;
 leaf.svgText=true;require(!GetUntransformedRectToAncestor(&leaf,box,&root),5);leaf.svgText=false;
 mid.states=NS_FRAME_SVG_LAYOUT;require(!GetUntransformedRectToAncestor(&leaf,box,&root),6);mid.states=0;
 mid.context=2;require(!GetUntransformedRectToAncestor(&leaf,box,&root),7);mid.context=1;
 mid.parent=nullptr;require(!GetUntransformedRectToAncestor(&leaf,box,&root),8);mid.parent=&root;
 leaf.position={INT32_MAX,0};require(!GetUntransformedRectToAncestor(&leaf,box,&root),9);
 leaf.parent=&root;leaf.position={INT32_MAX-10,0};require(!GetUntransformedRectToAncestor(&leaf,nsRect(0,0,20,1),&root),10);
 leaf.position={nscoord_MAX,0};require(!GetUntransformedRectToAncestor(&leaf,nsRect(0,0,1,1),&root),11);
 leaf.position={nscoord_MIN-1,0};require(!GetUntransformedRectToAncestor(&leaf,nsRect(0,0,1,1),&root),12);
 leaf.position={0,0};require(!GetUntransformedRectToAncestor(&leaf,nsRect(0,0,-1,1),&root),13);
 result=GetUntransformedRectToAncestor(&leaf,nsRect(0,0,0,0),&root);require(result && result->x==0,14);
 require(!GetUntransformedRectToAncestor(&leaf,nsRect(nscoord_MIN,0,2*nscoord_MAX,1),&root),17);
 require(!GetUntransformedRectToAncestor(&leaf,box,nullptr),18);
 leaf.parent=&mid;leaf.position={nscoord_MAX+100,0};mid.position={-nscoord_MAX-100,0};
 result=GetUntransformedRectToAncestor(&leaf,nsRect(0,0,1,1),&root);require(result && result->x==0,19);
 observed.SetLayoutRect(nsRect(-7858324,0,7864324,1));
 require(observed.x+observed.width==100,16);
 observed.SetLayoutRect(nsRect(-8382482,0,8388488,1));
 require(fabs(observed.x+observed.width-100.1)<0.00001,15);
 printf("PASS 19 checks\\n");
}
'''


def run(output):
    output.mkdir(exist_ok=False)
    variants = {'candidate': helper,
                'mutant-transform': helper.replace('frame->IsTransformed()', 'false'),
                'mutant-svg': helper.replace('frame->IsInSVGTextSubtree()', 'false'),
                'mutant-context': helper.replace('frame->PresContext() != aAncestor->PresContext()', 'false'),
                'mutant-position': helper.replace('x += frame->GetPosition().x;', 'x += 0;'),
                'mutant-dom-float': helper,
                'mutant-extent': helper.replace('aRect.width > nscoord_MAX || aRect.height > nscoord_MAX', 'false')}
    rows = []
    with tempfile.TemporaryDirectory(prefix='css-observer-candidate-') as temporary:
        for name, variant in variants.items():
            source = output / (name+'.cpp')
            selected_dom = extract((ROOT / 'original/DOMRect.cpp').read_text(),
                                   'void DOMRect::SetLayoutRect(const nsRect& aLayoutRect)') if name == 'mutant-dom-float' else dom
            source.write_text(prefix + variant + '\n' + selected_dom + main)
            for optimization in ['-O0', '-O2']:
                executable = Path(temporary) / 'program'
                command = ['/usr/bin/clang++', '-std=c++20', '-DNDEBUG', optimization,
                           '-fsanitize=undefined', '-fno-sanitize-recover=all',
                           '-I', str(ROOT / 'include'),
                           str(source), '-o', str(executable)]
                compiled = subprocess.run(command, capture_output=True, text=True)
                (output / (name+optimization+'-compile.log')).write_text(compiled.stdout+compiled.stderr)
                if compiled.returncode:
                    raise RuntimeError(compiled.stderr)
                result = subprocess.run([str(executable)], capture_output=True, text=True)
                (output / (name+optimization+'-run.log')).write_text(result.stdout+result.stderr)
                assert (result.returncode == 0) == (name == 'candidate')
                rows.append({'variant':name,'optimization':optimization,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    (output/'RESULT.json').write_text(json.dumps({'rows':rows,'scope':'Exact proposed helper and DOMRect method; provider frame facade, actual Mozilla CheckedInt header. No full Gecko build or matrix execution.'},indent=2)+'\n')
    print(json.dumps(rows))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    run(parser.parse_args().output.resolve())
