import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "development-build/full"
TARGET = OUT / "metric-providers"
TARGET.mkdir(parents=True, exist_ok=True)
helper = runpy.run_path(str(ROOT / "native/extract-full.py"))
full = helper["full"]
font = ROOT / "provider-bridge-v1/source/providers/gfx/thebes/gfxFont.h"
header = ROOT / "source/providers/gfx/thebes/gfxTextRun.h"
source = ROOT / "source/providers/gfx/thebes/gfxTextRun.cpp"
runpy.run_path(str(ROOT / "native/extract-measurement.py"))
runpy.run_path(str(ROOT / "native/extract-hyphen-consumer.py"))

def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old,new)

types = (OUT / "measurement-declarations.hpp").read_text()
types = replace_once(types,"namespace gfx=mozilla::gfx;", "namespace gfx=mozilla::gfx;\nnamespace mozilla::gfx { struct Point {float x,y;}; }")
types = replace_once(types, "inline bool operator!(gfx::ShapedTextFlags a){return uint16_t(a)==0;}", "inline bool operator!(gfx::ShapedTextFlags a){return uint16_t(a)==0;}\ninline bool operator&&(bool a,gfx::ShapedTextFlags b){return a&&uint16_t(b)!=0;}")
types = replace_once(types,"struct Range{uint32_t start,end;Range(uint32_t a,uint32_t b)", "struct Range{uint32_t start,end;Range():start(0),end(0){} Range(uint32_t a,uint32_t b)")
methods = "\n".join(full(font,name) for name in ["uint32_t GetSimpleAdvance() const", "uint32_t GetGlyphCount() const", "bool ApplyLetterSpacingBetweenDetailedGlyphs() const"])
types = replace_once(types,"uint32_t mValue=0;", "uint32_t mValue=0;\n"+methods)
old = " double GetAdvanceForGlyph(uint32_t i,nscoord)const{return advances.at(i);}\n double ComputePartialLigatureWidth(Range r,const PropertyProvider*)const{double n=0;for(auto i=r.start;i<r.end;i++)n+=advances.at(i);return n;}"
new = full(font,"struct DetailedGlyph {",True)+"\n"+full(header,"struct LigatureData {",True)+"\n"+"""
 std::vector<std::vector<DetailedGlyph>> details;
 const DetailedGlyph*GetDetailedGlyphs(uint32_t index,uint32_t count)const{
  assert(index<details.size()&&count<=details[index].size());return details[index].data();
 }
 void SetFixtureAdvance(uint32_t index,double advance){
  assert(advance>=INT32_MIN&&advance<=INT32_MAX&&advance==int32_t(advance));
  details.resize(glyphs.size());details.at(index)={{0,int32_t(advance),{0,0}}};
  glyphs.at(index).mValue=(glyphs.at(index).mValue&~CompressedGlyph::GLYPH_COUNT_MASK)|1;
 }
 int32_t GetAdvanceForGlyphs(Range,nscoord)const;
 LigatureData ComputeLigatureData(Range,const PropertyProvider*)const;
 gfxFloat ComputePartialLigatureWidth(Range,const PropertyProvider*)const;
"""+full(header,"nscoord GetAdvanceForGlyph(")
types = replace_once(types,old,new)
(TARGET / "metric-declarations.hpp").write_text(types)
prefix = (OUT / "measurement-types.hpp").read_text().removesuffix((OUT / "measurement-declarations.hpp").read_text())
assert prefix+(OUT / "measurement-declarations.hpp").read_text()==(OUT / "measurement-types.hpp").read_text()
(TARGET / "metric-types.hpp").write_text(prefix+types)
body = "\n".join(full(source,name) for name in ["gfxTextRun::LigatureData gfxTextRun::ComputeLigatureData(","gfxFloat gfxTextRun::ComputePartialLigatureWidth(","int32_t gfxTextRun::GetAdvanceForGlyphs("])
old_runner = (ROOT / "native/measurement-runner.cpp").read_text()
old_body = (OUT / "measurement.cpp").read_text().removesuffix(old_runner).removeprefix('#include "measurement-types.hpp"\n')
runner = replace_once(old_runner,"g.SetCanBreakBefore(kind);", "g.SetCanBreakBefore(kind);run.SetFixtureAdvance(i,run.advances[i]);")
(TARGET / "measurement.cpp").write_text('#include "metric-types.hpp"\n'+body+'\n'+old_body+'\n'+runner)
consumer = (OUT / "hyphen-consumer.hpp").read_text()
consumer = replace_once(consumer,'#include "measurement-declarations.hpp"','#include "metric-declarations.hpp"')
consumer = replace_once(consumer,old_body,body+'\n'+old_body)
(TARGET / "hyphen-consumer.hpp").write_text(consumer)
consumer_runner = (ROOT / "native/hyphen-consumer-runner.cpp").read_text()
consumer_runner = replace_once(consumer_runner, 'g.SetCanBreakBefore(mask=="-"?0:mask.at(i)-\'0\');', 'g.SetCanBreakBefore(mask=="-"?0:mask.at(i)-\'0\');run.SetFixtureAdvance(i,1);')
(TARGET / "hyphen-consumer.cpp").write_text('#include "hyphen-consumer.hpp"\n'+consumer_runner)
(TARGET / "EXTRACTION.json").write_text(json.dumps({"definitions":helper["records"],"scope":"Complete native simple/detailed glyph advance, detailed letter spacing, whole ligature partition and partial width. Valid detailed storage is an explicit fixture provider. MeasureText/spacing/font/shaping remain adapters; no whole-provider acceptance.","generated":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in TARGET.glob("*.hpp")}},indent=2)+"\n")
print("extracted",len(helper["records"]),"complete metric provider definitions")
