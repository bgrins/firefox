import json
import runpy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'development-build/provider'
helper=runpy.run_path(str(ROOT/'native/extract-unicode.py'))
full=helper['full']
source='gfx/thebes/gfxFont.h'
flags=full(source,'enum Flags : uint32_t',True)
methods='\n'.join(full(source,name) for name in [
    'bool IsSimpleGlyph() const','bool IsClusterStart() const',
    'bool CharIsSpace() const','uint8_t CanBreakBefore() const',
    'uint32_t SetCanBreakBefore(uint8_t aCanBreakBefore)'])
body=full('../candidate/gfx/thebes/gfxTextRun.cpp','bool gfxTextRun::SetPotentialLineBreaks(')
types=(ROOT/'native/hyphen-producer-input/range-types.hpp').read_text()
a=types.index(' struct CompressedGlyph{');b=types.index('\n gfxSkipChars skip;',a)
types=types[:a]+' struct CompressedGlyph {\n'+flags+'\nuint32_t mValue=0;\n'+methods+'\n};\n'+types[b:]
(OUT/'range-types-native.hpp').write_text(types+'\n'+body+'\n')
(OUT/'break-sink-native.hpp').write_text(full('../candidate/layout/generic/nsTextFrame.cpp','class BreakSink final',True)+'\n')
(OUT/'glyph-extraction.json').write_text(json.dumps(helper['units'],indent=2)+'\n')

ref=full('xpcom/base/StaticPtr.h','template <class T>\nclass MOZ_ONLY_USED_TO_AVOID_STATIC_CONSTRUCTORS StaticRefPtr',True)
(OUT/'static-ref-native.h').write_text('namespace mozilla {\n'+ref+'\n}\n')
