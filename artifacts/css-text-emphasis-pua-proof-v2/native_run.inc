struct GlyphRun { gfxFont* mFont; uint32_t mCharacterOffset; };
nsTArray<GlyphRun> mGlyphRuns;
CompressedGlyph* mCharacterGlyphs=nullptr;
bool vertical=false;
int direction=1;
gfxFloat GetDirection() const { return direction; }
bool IsVertical() const { return vertical; }
struct PropertyProvider {
  using Spacing=gfxFont::Spacing;
  std::vector<Spacing> spacing;
  nscoord letterSpacing=0;
  bool enabled=true;
  nscoord LetterSpacing() const { providerTrace.push_back("letter-spacing:"+std::to_string(letterSpacing)); return letterSpacing; }
  bool GetSpacing(Range range,Spacing* out) const {
    providerTrace.push_back("spacing:"+std::to_string(range.start)+":"+std::to_string(range.end)+":"+std::to_string(enabled));
    for(auto i=range.start;i<range.end;++i) out[i-range.start]=spacing.at(i);
    return enabled;
  }
};
struct DrawParams { DrawParams(gfxContext*,gfx::PaletteCache&){} };
std::vector<gfx::Point> emissions;
void Draw(Range range,gfx::Point pt,const DrawParams&,imgDrawingParams&) {
  providerTrace.push_back("draw:"+std::to_string(range.start)+":"+std::to_string(range.end));
  emissions.push_back(pt);
}
void Initialize(uint32_t length) { mLength=length;storage.resize(length);mCharacterGlyphs=storage.data(); }
const GlyphRun* FindFirstGlyphRunContaining(uint32_t) const;
LigatureData ComputeLigatureData(Range,const PropertyProvider*) const;
gfxFloat ComputePartialLigatureWidth(Range,const PropertyProvider*) const;
int32_t GetAdvanceForGlyphs(Range,nscoord) const;
bool GetAdjustedSpacingArray(Range,const PropertyProvider*,Range,nsTArray<PropertyProvider::Spacing>*) const;
bool ShrinkToLigatureBoundaries(Range*) const;
void DrawEmphasisMarks(gfxContext*,gfxTextRun*,gfxFloat,gfx::Point,Range,const PropertyProvider*,gfx::PaletteCache&,imgDrawingParams&) const;
