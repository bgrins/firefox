using gfxFloat=double;
using nscoord=int32_t;
struct DrawTarget{};
template<class T>struct already_AddRefed{T*value=nullptr;};
namespace mozilla {enum class StyleHyphens{None,Manual,Auto};namespace gfx{using Float=float;}}
using mozilla::StyleHyphens;
using mozilla::fallible;
namespace gfx=mozilla::gfx;
__SHAPED_FLAGS__
inline gfx::ShapedTextFlags operator&(gfx::ShapedTextFlags a,gfx::ShapedTextFlags b){return gfx::ShapedTextFlags(uint16_t(a)&uint16_t(b));}
inline bool operator!(gfx::ShapedTextFlags a){return uint16_t(a)==0;}
__BREAK_PRIORITY__
struct gfxFont{
 enum BoundingBoxType{LOOSE_INK_EXTENTS,TIGHT_INK_EXTENTS};
 __SPACING__
};
struct gfxTextRun{
 struct Range{uint32_t start,end;Range(uint32_t a,uint32_t b):start(a),end(b){assert(a<=b);}uint32_t Length()const{return end-start;}};
 __HYPHEN_TYPE__
 __HYPHEN_STATE__
 __SUPPRESS_BREAK__
 __TRIMMABLE__
 __PROPERTY_PROVIDER__
 struct CompressedGlyph{
  __GLYPH_FLAGS__
  uint32_t mValue=0;
  __GLYPH_METHODS__
 };
 std::vector<CompressedGlyph> glyphs;
 CompressedGlyph*mCharacterGlyphs=nullptr;
 std::vector<double> advances;
 gfx::ShapedTextFlags mFlags{};
 struct Metrics{double mAdvanceWidth=0;};
 uint32_t GetLength()const{return glyphs.size();}
 const CompressedGlyph*GetCharacterGlyphs()const{return mCharacterGlyphs;}
 __CAN_BREAK__
 __CAN_HYPHENATE__
 __OPTIONAL_HYPHEN__
 void ClassifyAutoHyphenations(uint32_t,Range,nsTArray<HyphenType>&,HyphenationState*);
 bool ShrinkToLigatureBoundaries(Range*)const;
 double GetAdvanceForGlyph(uint32_t i,nscoord)const{return advances.at(i);}
 double ComputePartialLigatureWidth(Range r,const PropertyProvider*)const{double n=0;for(auto i=r.start;i<r.end;i++)n+=advances.at(i);return n;}
 Metrics MeasureText(Range r,gfxFont::BoundingBoxType,DrawTarget*,const PropertyProvider*p)const{
  std::vector<PropertyProvider::Spacing>space(r.Length());if(!!(mFlags&gfx::ShapedTextFlags::TEXT_ENABLE_SPACING))p->GetSpacing(r,space.data());double w=0;for(auto i=r.start;i<r.end;i++)w+=advances.at(i)+space[i-r.start].mBefore+space[i-r.start].mAfter;return {w};
 }
 uint32_t BreakAndMeasureText(uint32_t,uint32_t,bool,gfxFloat,const PropertyProvider&,SuppressBreak,gfxFont::BoundingBoxType,DrawTarget*,bool,bool,bool,TrimmableWS*,Metrics&,bool&,uint32_t&,gfxBreakPriority&);
};
