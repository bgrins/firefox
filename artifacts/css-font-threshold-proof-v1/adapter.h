enum class StyleFontSynthesisStyle { Auto, ObliqueOnly };
PRESENTATION_DECLARATIONS
struct gfxFontStyle {
  StyleFontStyle style = StyleFontStyle::NORMAL;
  StyleFontWeight weight = StyleFontWeight::NORMAL;
  StyleFontWidth width = StyleFontWidth::NORMAL;
  StyleFontSynthesisStyle synthesisStyle = StyleFontSynthesisStyle::Auto;
  double size = 20;
  NORMAL_STYLE_PROVIDER
};
struct gfxFont {
  int id = 0;
  bool color = false;
  bool HasColorGlyphFor(uint32_t, uint32_t) { note("color:", id); return color; }
};
struct RangeFlags { static constexpr int eAutoWeight = 1; };
struct gfxFontEntry {
  int id = 0;
  nsCString name;
  WidthRange mWidth{StyleFontWidth::NORMAL};
  WeightRange mWeight{StyleFontWeight::NORMAL};
  SlantStyleRange mStyle{StyleFontStyle::NORMAL};
  bool covered = true, skip = false, fontReady = true;
  gfxFont font;
  WidthRange Width() const { note("width:", id); return mWidth; }
  WeightRange Weight() const { note("weight:", id); return mWeight; }
  SlantStyleRange SlantStyle() const { note("style:", id); return mStyle; }
  const nsCString& Name() const { note("name:", id); return name; }
  bool IsItalic() const { return mStyle.Min().IsItalic(); }
  bool IsOblique() const { return !mStyle.Min().IsItalic() && !mStyle.Min().IsNormal(); }
  int mRangeFlags = 0;
  bool variableBold = false;
  bool HasBoldVariableWeight() { note("variable-bold:",id); return variableBold; }
  bool SupportsBold();
  bool SkipDuringSystemFallback() const { note("skip:", id); return skip; }
  bool HasCharacter(uint32_t) const { note("char:", id); return covered; }
  gfxFont* FindOrMakeFont(const gfxFontStyle*) { note("font:", id); return fontReady ? &font : nullptr; }
};
struct gfxFontFamily;
namespace mozilla::fontlist { struct Family; struct FontList; }
GLOBAL_MATCH_DECLARATION
struct BitSet {
  int id = 0;
  bool covered = true;
  bool test(uint32_t) const { note("map:", id); return covered; }
};
struct gfxFontFamily {
  int id = 0;
  bool mHasStyles = true, mIsSimpleFamily = false;
  bool mFamilyCharacterMapInitialized = true, visible = true;
  nsCString mName;
  Lock mLock;
  BitSet mFamilyCharacterMap;
  nsTArray<RefPtr<gfxFontEntry>> mAvailableFonts;
  void FindStyleVariations() { note("variations:", id); mHasStyles = true; }
  bool TestCharacterMap(uint32_t c) { return mFamilyCharacterMap.test(c); }
  void ReadAllCMAPs() { note("readmaps:", id); mFamilyCharacterMapInitialized = true; }
  void FindAllFontsForStyle(const gfxFontStyle&, nsTArray<gfxFontEntry*>&, bool);
  void CheckForSimpleFamily();
  void FindFontForChar(GlobalFontMatch*);
  void SearchAllFontsForChar(GlobalFontMatch*);
};
namespace mozilla::fontlist {
using SharedBitSet = BitSet;
struct Pointer {
  void* p = nullptr;
  int id = -1;
  static Pointer Null() { return {}; }
  bool IsNull() const { return !p; }
  template<class T> T* ToArray(FontList* l, size_t) const { return ToPtr<T>(l); }
  template<class T> T* ToPtr(FontList*) const { note("pointer:", id); return static_cast<T*>(p); }
};
struct Face {
  struct InitData {
    int id;
    WeightRange mWeight;
    WidthRange mWidth;
    SlantStyleRange mStyle;
    BitSet* mCharMap;
    nsCString mDescriptor;
    unsigned mIndex = 0;
    gfxFontEntry* entry;
  };
  Face() = default;
  Face(FontList*, const InitData& d) : id(d.id), mWidth(d.mWidth), mWeight(d.mWeight), mStyle(d.mStyle), entry(d.entry) { note("construct-face:", id); }
  void SetCharacterMap(FontList*, BitSet* map, Family*) { mCharacterMap = {map,id}; note("setmap:",id); }
  int id = 0;
  WidthRange mWidth{StyleFontWidth::NORMAL};
  WeightRange mWeight{StyleFontWeight::NORMAL};
  SlantStyleRange mStyle{StyleFontStyle::NORMAL};
  uint16_t mSize = 0;
  bool valid = true;
  Pointer mCharacterMap;
  gfxFontEntry* entry = nullptr;
  bool HasValidDescriptor() const { note("descriptor:", id); return valid; }
};
struct Count { uint32_t value=0; operator uint32_t() const { return value; } void store(uint32_t v) { value=v; } };
struct DisplayString { nsCString value; const nsCString& AsString(FontList*) const { return value; } };
struct Family {
  Count mFaceCount;
  Pointer mFaces;
  DisplayString display;
  const DisplayString& DisplayName() const { return display; }
  void AddFaces(FontList*, const nsTArray<Face::InitData>&);
  int id = 0;
  bool initialized = true, fullyInitialized = true, visible = true;
  bool mIsSimple = false, facesAvailable = true, initializationSucceeds = true;
  Pointer mCharacterMap;
  Pointer initializedMap;
  std::vector<Pointer> faces;
  bool IsInitialized() const { note("initialized:", id); return initialized; }
  bool IsFullyInitialized() const { return fullyInitialized; }
  uint32_t NumFaces() const { return mFaceCount ? uint32_t(mFaceCount) : faces.size(); }
  Pointer* Faces(FontList*) const { note("faces:", id); return !facesAvailable ? nullptr : mFaceCount ? mFaces.ToPtr<Pointer>(nullptr) : const_cast<Pointer*>(faces.data()); }
  void SetupFamilyCharMap(FontList*) { note("setupmap:", id); mCharacterMap = initializedMap; }
  bool FindAllFacesForStyleInternal(FontList*, const gfxFontStyle&, nsTArray<Face*>&) const;
  void FindAllFacesForStyle(FontList*, const gfxFontStyle&, nsTArray<Face*>&, bool) const;
  void SearchAllFontsForChar(FontList*, GlobalFontMatch*);
};
struct FontList {
  Pointer Alloc(size_t bytes) { auto* p = std::calloc(1, bytes); assert(p); allocations.push_back(p); note("allocate:", bytes); return {p,-1}; }
  std::vector<Family> families;
  bool available = true;
  Family* Families() { return available ? families.data() : nullptr; }
  uint32_t NumFamilies() const { return families.size(); }
};
}
enum class FontVisibility { User };
struct FontVisibilityProvider { FontVisibility GetFontVisibility() { return FontVisibility::User; } };
struct FontFamily {
  mozilla::fontlist::Family* mShared = nullptr;
  gfxFontFamily* mUnshared = nullptr;
  FontFamily() = default;
  FontFamily(mozilla::fontlist::Family* p) : mShared(p) {}
  FontFamily(gfxFontFamily* p) : mUnshared(p) {}
};
struct FamilyMap {
  std::vector<RefPtr<gfxFontFamily>> families;
  const auto& Values() const { return families; }
};
bool parentProcess = true, asyncFallback = false;
bool XRE_IsParentProcess() { return parentProcess; }
struct StaticPrefs { static bool gfx_font_rendering_fallback_async() { return asyncFallback; } };
constexpr int eGfxLog_textrun = 0;
bool useCmapsPolicy = true;
struct gfxPlatform {
  static gfxPlatform* GetPlatform() { static gfxPlatform p; return &p; }
  static LogModule* GetLog(int) { return nullptr; }
  bool UseCmapsDuringSystemFallback() const { return useCmapsPolicy; }
};
struct gfxPlatformFontList {
  Lock mLock;
  FamilyMap mFontFamilies;
  mozilla::fontlist::FontList* shared = nullptr;
  gfxFontEntry* platformFace = nullptr;
  FontFamily platformFamily;
  bool whitelist = true;
  static gfxPlatformFontList* PlatformFontList() { static gfxPlatformFontList p; return &p; }
  bool InitializeFamily(mozilla::fontlist::Family* f, bool) {
    note("initialize:", f->id);
    if (f->initializationSucceeds) f->mCharacterMap = f->initializedMap;
    return f->initializationSucceeds;
  }
  gfxFontEntry* GetOrCreateFontEntry(mozilla::fontlist::Face* f, mozilla::fontlist::Family*) {
    note("entry:", f->id); return f->entry;
  }
  bool IsFontFamilyWhitelistActive() const { return whitelist; }
  mozilla::fontlist::FontList* SharedFontList() { return shared; }
  bool IsVisibleToCSS(const gfxFontFamily& f, FontVisibility) { note("visible:", f.id); return f.visible; }
  bool IsVisibleToCSS(const mozilla::fontlist::Family& f, FontVisibility) { note("visible:", f.id); return f.visible; }
  void StartCmapLoadingFromFamily(uint32_t i) { note("async:", i); }
  gfxFontEntry* PlatformGlobalFontFallback(FontVisibilityProvider*, uint32_t, Script,
                                           const gfxFontStyle*, FontFamily& family) {
    note("platform:", 0); family = platformFamily; return platformFace;
  }
  already_AddRefed<gfxFont> GlobalFontFallback(FontVisibilityProvider*, uint32_t,
      uint32_t, Script, FontPresentation, const gfxFontStyle*, uint32_t&, FontFamily&);
};
