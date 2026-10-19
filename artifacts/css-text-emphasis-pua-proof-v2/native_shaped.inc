std::vector<CompressedGlyph> storage;
mozilla::UniquePtr<DetailedGlyphStore> mDetailedGlyphs;
uint32_t mLength=0;
uint32_t mFlags=0;
CompressedGlyph* GetCharacterGlyphs() { return storage.data(); }
const CompressedGlyph* GetCharacterGlyphs() const { return storage.data(); }
bool HasDetailedGlyphs() const { return mDetailedGlyphs!=nullptr; }
DetailedGlyph* AllocateDetailedGlyphs(uint32_t,uint32_t);
void SetDetailedGlyphs(uint32_t,uint32_t,const DetailedGlyph*);
