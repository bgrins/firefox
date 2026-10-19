from pathlib import Path

root = Path(__file__).resolve().parent


def edit(name, replacements):
    text = (root / "original" / name).read_text()
    for before, after in replacements:
        assert text.count(before) == 1, (name, before)
        text = text.replace(before, after)
    target = root / "candidate" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


signature = """  already_AddRefed<gfxFontEntry> CloneUserFontEntry(
      WeightRange aWeight, WidthRange aWidth,
      SlantStyleRange aStyle) const override;
"""
edit("gfx/thebes/gfxFontEntry.h", [
    ("  virtual gfxFontEntry* Clone() const = 0;\n", """  virtual gfxFontEntry* Clone() const = 0;

  // Retains the user font's native resource with fresh entry caches. The caller
  // must initialize CSS descriptors and user font metadata; feature settings
  // contain only platform defaults.
  virtual already_AddRefed<gfxFontEntry> CloneUserFontEntry(
      WeightRange aWeight, WidthRange aWidth, SlantStyleRange aStyle) const;
"""),
    ("  virtual ~gfxFontEntry();\n", """  virtual ~gfxFontEntry();

  void CopyUserFontResourceFlagsTo(gfxFontEntry& aClone) const;
""")])
edit("gfx/thebes/gfxFontEntry.cpp", [
    ("gfxFontEntry::~gfxFontEntry() {", """already_AddRefed<gfxFontEntry> gfxFontEntry::CloneUserFontEntry(
    WeightRange aWeight, WidthRange aWidth, SlantStyleRange aStyle) const {
  MOZ_ASSERT_UNREACHABLE("only platform user font entries can be cloned");
  return nullptr;
}

void gfxFontEntry::CopyUserFontResourceFlagsTo(gfxFontEntry& aClone) const {
  MOZ_ASSERT(IsUserFont());
  aClone.mIsDataUserFont = mIsDataUserFont;
  aClone.mIsLocalUserFont = mIsLocalUserFont;
  aClone.mFixedPitch = mFixedPitch;
  aClone.mIsBadUnderlineFont = mIsBadUnderlineFont;
  aClone.mStandardFace = mStandardFace;
  aClone.mIgnoreGDEF = mIgnoreGDEF;
  aClone.mIgnoreGSUB = mIgnoreGSUB;
  aClone.mSkipDefaultFeatureSpaceCheck = mSkipDefaultFeatureSpaceCheck;
}

gfxFontEntry::~gfxFontEntry() {""")])
for name in ["CoreTextFontList.h", "gfxFT2FontList.h"]:
    edit("gfx/thebes/" + name, [
        ("  gfxFontEntry* Clone() const override;\n",
         "  gfxFontEntry* Clone() const override;\n" + signature)])
edit("gfx/thebes/CoreTextFontList.cpp", [
    ("gfxFontEntry* CTFontEntry::Clone() const {", """already_AddRefed<gfxFontEntry> CTFontEntry::CloneUserFontEntry(
    WeightRange aWeight, WidthRange aWidth, SlantStyleRange aStyle) const {
  MOZ_ASSERT(IsUserFont());
  AutoReadLock lock(mLock);
  MOZ_ASSERT(mFontRefInitialized && mFontRef);
  RefPtr fe = MakeRefPtr<CTFontEntry>(Name(), mFontRef, aWeight, aWidth, aStyle,
                                    mIsDataUserFont, mIsLocalUserFont);
  CopyUserFontResourceFlagsTo(*fe);
  return fe.forget();
}

gfxFontEntry* CTFontEntry::Clone() const {""")])
edit("gfx/thebes/gfxDWriteFontList.h", [
    ("  gfxFontEntry* Clone() const override;\n",
     "  gfxFontEntry* Clone() const override;\n" + signature),
    ("                     gfxDWriteFontFileStream* aFontFileStream,\n",
     "                     IDWriteFontFileStream* aFontFileStream,\n")])
edit("gfx/thebes/gfxDWriteFontList.cpp", [
    ("gfxFontEntry* gfxDWriteFontEntry::Clone() const {", """already_AddRefed<gfxFontEntry> gfxDWriteFontEntry::CloneUserFontEntry(
    WeightRange aWeight, WidthRange aWidth, SlantStyleRange aStyle) const {
  MOZ_ASSERT(IsUserFont());
  AutoReadLock lock(mLock);
  RefPtr<gfxDWriteFontEntry> fe;
  if (mFont) {
    fe = MakeRefPtr<gfxDWriteFontEntry>(Name(), mFont.get(), aWeight, aWidth,
                                      aStyle);
  } else {
    MOZ_ASSERT(mFontFile && mFontFileStream);
    fe = MakeRefPtr<gfxDWriteFontEntry>(Name(), mFontFile.get(),
                                      mFontFileStream.get(), aWeight, aWidth,
                                      aStyle);
    fe->mFaceType = mFaceType;
  }
  fe->mIsSystemFont = mIsSystemFont;
  fe->mForceGDIClassic = mForceGDIClassic;
  fe->mMayUseGDIAccess = mMayUseGDIAccess;
  CopyUserFontResourceFlagsTo(*fe);
  return fe.forget();
}

gfxFontEntry* gfxDWriteFontEntry::Clone() const {""")])
edit("gfx/thebes/gfxFT2FontList.cpp", [
    ("gfxFontEntry* FT2FontEntry::Clone() const {", """already_AddRefed<gfxFontEntry> FT2FontEntry::CloneUserFontEntry(
    WeightRange aWeight, WidthRange aWidth, SlantStyleRange aStyle) const {
  MOZ_ASSERT(IsUserFont());
  RefPtr fe = MakeRefPtr<FT2FontEntry>(Name());
  fe->mFilename = mFilename;
  fe->mFTFontIndex = mFTFontIndex;
  RefPtr<SharedFTFace> face(mFTFace);
  fe->mFTFace = face.forget().take();
  fe->mWeightRange = aWeight;
  fe->mWidthRange = aWidth;
  fe->mStyleRange = aStyle;
  CopyUserFontResourceFlagsTo(*fe);
  return fe.forget();
}

gfxFontEntry* FT2FontEntry::Clone() const {""")])
edit("gfx/thebes/gfxFcPlatformFontList.h", [
    ("  gfxFontEntry* Clone() const override;\n",
     "  gfxFontEntry* Clone() const override;\n" + signature),
    ("  virtual ~gfxFontconfigFontEntry();\n", """  virtual ~gfxFontconfigFontEntry();

  gfxFontconfigFontEntry(const gfxFontconfigFontEntry& aEntry,
                        WeightRange aWeight, WidthRange aWidth,
                        SlantStyleRange aStyle);
"""),
    ("  void InitSkrifaFont(FcPattern* aPattern);\n", """  void InitSkrifaFont(FcPattern* aPattern);
  void InitSkrifaFontFace() override;
  bool mIsUserFontClone = false;
""")])
edit("gfx/thebes/gfxFcPlatformFontList.cpp", [
    ("gfxFontEntry* gfxFontconfigFontEntry::Clone() const {", """gfxFontconfigFontEntry::gfxFontconfigFontEntry(
    const gfxFontconfigFontEntry& aEntry, WeightRange aWeight, WidthRange aWidth,
    SlantStyleRange aStyle)
    : gfxFT2FontEntryBase(aEntry.Name()),
      mFontPattern(aEntry.mFontPattern),
      mFTFaceInitialized(false) {
#ifdef MOZ_FONTATIONS
  mIsUserFontClone = true;
#endif
  RefPtr<SharedFTFace> face(aEntry.mFTFace);
  if (face) {
    mFTFace = face.forget().take();
    mFTFaceInitialized = true;
  }
  mWeightRange = aWeight;
  mWidthRange = aWidth;
  mStyleRange = aStyle;
  if (aEntry.IsLocalUserFont()) {
    GetUserFontFeatures(mFontPattern);
  }
}

already_AddRefed<gfxFontEntry> gfxFontconfigFontEntry::CloneUserFontEntry(
    WeightRange aWeight, WidthRange aWidth, SlantStyleRange aStyle) const {
  MOZ_ASSERT(IsUserFont());
  RefPtr<gfxFontconfigFontEntry> fe =
      new gfxFontconfigFontEntry(*this, aWeight, aWidth, aStyle);
  CopyUserFontResourceFlagsTo(*fe);
  return fe.forget();
}

gfxFontEntry* gfxFontconfigFontEntry::Clone() const {"""),
    ("void gfxFontconfigFontEntry::InitSkrifaFont(FcPattern* aPattern) {", """void gfxFontconfigFontEntry::InitSkrifaFontFace() {
  if (mIsUserFontClone && mFTFaceInitialized) {
    InitSkrifaFont(mFontPattern);
  }
}

void gfxFontconfigFontEntry::InitSkrifaFont(FcPattern* aPattern) {""")])
