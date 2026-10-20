import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def body(text, signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


def replay(output):
    header = (ROOT / 'source/DOMRect.h').read_text()
    implementation = (ROOT / 'source/DOMRect.cpp').read_text()
    setter = body(header, 'void SetRect(float aX, float aY, float aWidth, float aHeight)')
    conversion = body(implementation, 'void DOMRect::SetLayoutRect(const nsRect& aLayoutRect)')
    source = '''#include <cmath>
#include <cstdio>
#include <cassert>
#include <cstdint>
using std::floor;
struct nsRect {
  int32_t x,y,width,height;
  int32_t XMost() const { return x+width; }
  int32_t YMost() const { return y+height; }
};
static int AppUnitsPerCSSPixel() { return 60; }
static double RoundFloat(double aValue) { return floor(aValue + 0.5); }
struct DOMRect {
 double mX,mY,mWidth,mHeight;
 void SetLayoutRect(const nsRect&);
''' + setter + '\n};\n' + conversion + '''
int main() {
 for (int32_t width : {7208,8168,8388488,8389448}) {
  for (bool roundtrip : {false,true}) {
   int32_t x = 6000-width;
   int32_t observedX = x, observedWidth = width;
   if (roundtrip) {
    float px = float(x)/60.0f, pw = float(width)/60.0f;
    observedX = int32_t(floor(double(px*60.0f)+0.5));
    observedWidth = int32_t(floor(double(pw*60.0f)+0.5));
   }
   DOMRect rect;
   rect.SetLayoutRect({observedX,0,observedWidth,600});
   double end = rect.mX+rect.mWidth;
   printf("{\\"widthAU\\":%d,\\"xAU\\":%d,\\"floatRoundTrip\\":%s,\\"observedXAU\\":%d,\\"observedWidthAU\\":%d,\\"x\\":%.17g,\\"width\\":%.17g,\\"right\\":%.17g}\\n",width,x,roundtrip?"true":"false",observedX,observedWidth,rect.mX,rect.mWidth,end);
   if (width==8388488 && roundtrip) {
    assert(observedX==-8382488 && observedWidth==8388489);
    assert(end==100.015625);
   }
   if (!roundtrip || width==8389448) { assert(end==100); }
  }
 }
}
'''
    source = '#include <initializer_list>\n' + source
    output.mkdir(parents=True, exist_ok=False)
    (output / 'generated.cpp').write_text(source)
    results = []
    with tempfile.TemporaryDirectory(prefix='css-observer-replay-') as temporary:
        for optimization in ['-O0', '-O2']:
            executable = Path(temporary) / ('replay' + optimization)
            command = ['/usr/bin/clang++', '-std=c++17', optimization,
                       '-fsanitize=undefined', '-fno-sanitize-recover=all',
                       str(output / 'generated.cpp'), '-o', str(executable)]
            compiled = subprocess.run(command, capture_output=True, text=True)
            (output / (optimization + '-compile.log')).write_text(compiled.stdout + compiled.stderr)
            if compiled.returncode:
                raise RuntimeError(compiled.stderr)
            run = subprocess.run([str(executable)], capture_output=True, text=True)
            (output / (optimization + '-run.log')).write_text(run.stdout + run.stderr)
            if run.returncode:
                raise RuntimeError(run.stderr)
            results.append([json.loads(row) for row in run.stdout.splitlines()])
    assert results[0] == results[1]
    summary = {'casesPerOptimization': len(results[0]), 'optimizations': ['O0', 'O2'],
               'sourceSHA256': hashlib.sha256(source.encode()).hexdigest(), 'rows': results[0],
               'scope': 'Exact DOMRect methods; scalar float rectangle round-trip is a conditional model, not full matrix/frame extraction.'}
    (output / 'RESULT.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    replay(parser.parse_args().output.resolve())
