import json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
h=runpy.run_path(str(ROOT/'native/extract-full.py'));full=h['full'];changes=[]
font=ROOT/'provider-bridge-v1/source/providers/gfx/thebes/gfxFont.h'
header=ROOT/'source/providers/gfx/thebes/gfxTextRun.h';source=ROOT/'source/providers/gfx/thebes/gfxTextRun.cpp'
prefix=(ROOT/'native/facade.hpp').read_text().split('template<class T> class RefPtr')[0]
prefix='#include <utility>\n#define DEBUG 1\n'+prefix
types=(ROOT/'native/measurement-types.hpp').read_text()
fields={
 '__SHAPED_FLAGS__':'namespace mozilla::gfx{'+full(font,'enum class ShapedTextFlags : uint16_t',True)+'}',
 '__BREAK_PRIORITY__':full(ROOT/'source/providers/gfx/thebes/gfxTypes.h','enum class gfxBreakPriority',True),
 '__SPACING__':full(font,'struct Spacing {',True),
 '__HYPHEN_TYPE__':full(header,'enum class HyphenType',True),
 '__HYPHEN_STATE__':full(header,'struct HyphenationState {',True),
 '__SUPPRESS_BREAK__':full(header,'enum SuppressBreak {',True),
 '__TRIMMABLE__':full(header,'struct TrimmableWS {',True),
 '__PROPERTY_PROVIDER__':full(header,'class PropertyProvider {',True),
 '__GLYPH_FLAGS__':full(font,'enum Flags : uint32_t',True),
 '__GLYPH_METHODS__':'\n'.join(full(font,m)for m in ['bool IsSimpleGlyph() const','bool IsClusterStart() const','bool IsLigatureGroupStart() const','bool CharIsSpace() const','bool CharIsTab() const','bool CharIsNewline() const','uint8_t CanBreakBefore() const','uint32_t SetCanBreakBefore(uint8_t aCanBreakBefore)']),
 '__CAN_BREAK__':full(header,'uint8_t CanBreakBefore(uint32_t aPos) const'),
 '__CAN_HYPHENATE__':full(header,'bool CanHyphenateBefore(uint32_t aPos) const'),
 '__OPTIONAL_HYPHEN__':full(header,'static bool IsOptionalHyphenBreak('),
}
for key,value in fields.items():assert types.count(key)==1;types=types.replace(key,value)
body='\n'.join(full(source,m)for m in ['static bool GetAdjustedSpacing(','bool gfxTextRun::ShrinkToLigatureBoundaries(','void gfxTextRun::ClassifyAutoHyphenations(','uint32_t gfxTextRun::BreakAndMeasureText('])
(OUT/'measurement-types.hpp').write_text(prefix+types)
(OUT/'measurement-declarations.hpp').write_text(types)
(OUT/'measurement.cpp').write_text('#include "measurement-types.hpp"\n'+body+'\n'+(ROOT/'native/measurement-runner.cpp').read_text())
(OUT/'measurement-extraction.json').write_text(json.dumps({'functions':h['records'],'scope':'Complete measurement and classification/control flow, spacing adjustment and shrink-to-ligature algorithm; native compressed glyph fields/accessors. Advance/partial-ligature/MeasureText metrics and property inputs are explicit fixture providers, not actual shaping/font allocation or complete nsTextFrame PropertyProvider yet.'},indent=2)+'\n')
