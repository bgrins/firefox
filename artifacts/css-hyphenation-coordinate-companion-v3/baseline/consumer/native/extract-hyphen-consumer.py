import json,re,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
h=runpy.run_path(str(ROOT/'native/extract-full.py'));full=h['full']
src=ROOT/'source/providers';frame=ROOT/'source/candidate/layout/generic/nsTextFrame.cpp'
prefix='#include <utility>\n#include <limits>\n#define DEBUG 1\n#include "transform-native.hpp"\n#include "measurement-declarations.hpp"\n'
types=(ROOT/'native/hyphen-consumer-types.hpp').read_text()
for key,value in {'__WRAP_STYLE__':full(src/'layout/style/nsStyleStruct.h','bool WhiteSpaceCanWrapStyle() const'),'__CHAR_AT__':full(src/'dom/base/CharacterDataBuffer.h','[[nodiscard]] char16_t CharAt(')}.items():assert types.count(key)==1;types=types.replace(key,value)
bit=re.search(r'FRAME_STATE_BIT\(Text,\s*(\d+),\s*TEXT_START_OF_LINE\)',(src/'layout/generic/nsFrameStateBits.h').read_text())[1]
types='constexpr uint64_t TEXT_START_OF_LINE=uint64_t(1)<<'+bit+';\n'+types
body=full(src/'layout/generic/nsTextFrameUtils.h','class nsSkipCharsRunIterator {',True)+'\n'+full(src/'layout/generic/nsTextFrameUtils.cpp','bool nsSkipCharsRunIterator::NextRun(')+'\n'
body+=full(src/'layout/style/nsStyleStructInlines.h','bool nsStyleText::WhiteSpaceCanWrap(')+'\n'
for marker in ['static bool IsInBounds(','static inline bool IS_HYPHEN(','void nsTextFrame::PropertyProvider::GetHyphenationBreaks(']:
 unit=full(frame,marker)
 for variant in ['original','standalone']:assert full(ROOT/f'source/{variant}/layout/generic/nsTextFrame.cpp',marker)==unit,(marker,variant)
 body+=unit+'\n'
measurement=(OUT/'measurement.cpp').read_text();measurement=measurement.split((ROOT/'native/measurement-runner.cpp').read_text())[0].removeprefix('#include "measurement-types.hpp"\n')
(OUT/'hyphen-consumer.hpp').write_text(prefix+types+'\n'+body+measurement)
(OUT/'hyphen-consumer.cpp').write_text('#include "hyphen-consumer.hpp"\n'+(ROOT/'native/hyphen-consumer-runner.cpp').read_text())
(OUT/'hyphen-consumer-extraction.json').write_text(json.dumps({'functions':h['records'],'scope':'Complete native TransformText/skip storage/skip-run iterator, CanHyphenateBefore, GetHyphenationBreaks, classification/measurement; exact getter/body identity checked across frozen source variants. PropertyProvider constructor fields, glyph metrics, spacing array, frame/style storage and shaping remain explicit adapters. This does not yet join upstream scanner outputs.'},indent=2)+'\n')
