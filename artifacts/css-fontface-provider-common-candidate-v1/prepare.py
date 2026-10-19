from pathlib import Path
import difflib

root = Path(__file__).resolve().parent


def edit(name, replacements):
    text = (root / 'original' / name).read_text()
    for before, after in replacements:
        assert text.count(before) == 1, (name, before)
        text = text.replace(before, after)
    target = root / 'candidate' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


edit('gfx/thebes/gfxUserFontSet.h', [(
    '  ~gfxUserFontEntry() override;\n',
    '''  ~gfxUserFontEntry() override;

  // Initializes a detached wrapper without notifying FontFace owners.
  void InitializeFromLoadedEntry(const gfxUserFontEntry& aEntry);
''')])

edit('gfx/thebes/gfxUserFontSet.cpp', [(
    'void gfxUserFontEntry::UpdateAttributes(gfxUserFontAttributes&& aAttr) {',
    '''void gfxUserFontEntry::InitializeFromLoadedEntry(
    const gfxUserFontEntry& aEntry) {
  MOZ_ASSERT(NS_IsMainThread());
  MOZ_ASSERT(mUserFontLoadState == STATUS_NOT_LOADED);
  MOZ_ASSERT(!mPlatformFontEntry && !mLoader);
  MOZ_RELEASE_ASSERT(aEntry.mUserFontLoadState == STATUS_LOADED);
  MOZ_RELEASE_ASSERT(aEntry.mPlatformFontEntry);

  RefPtr<gfxFontEntry> platform =
      aEntry.mPlatformFontEntry->CloneUserFontEntry(Weight(), Width(),
                                                  SlantStyle());
  MOZ_RELEASE_ASSERT(platform);
  platform->mFeatureSettings.AppendElements(mFeatureSettings);
  platform->mVariationSettings.AppendElements(mVariationSettings);
  platform->mLanguageOverride = mLanguageOverride;
  platform->SetFamilyName(FamilyName());
  platform->mRangeFlags = mRangeFlags;
  platform->mAscentOverride = mAscentOverride;
  platform->mDescentOverride = mDescentOverride;
  platform->mLineGapOverride = mLineGapOverride;
  platform->mSizeAdjust = mSizeAdjust;

  const gfxUserFontData* oldData =
      aEntry.mPlatformFontEntry->mUserFontData.get();
  MOZ_RELEASE_ASSERT(oldData);
  auto data = MakeUnique<gfxUserFontData>();
  data->mFontData = oldData->mFontData;
  data->mMetadata.AppendElements(oldData->mMetadata);
  data->mURI = oldData->mURI;
  data->mPrincipal = oldData->mPrincipal;
  data->mLocalName = oldData->mLocalName;
  data->mRealName = oldData->mRealName;
  data->mSrcIndex = oldData->mSrcIndex;
  data->mMetaOrigLen = oldData->mMetaOrigLen;
  data->mTechFlags = oldData->mTechFlags;
  data->mFormatHint = oldData->mFormatHint;
  data->mCompression = oldData->mCompression;
  data->mPrivate = oldData->mPrivate;
  data->mIsBuffer = oldData->mIsBuffer;

#if MOZ_FONTATIONS
  if (data->mFontData &&
      StaticPrefs::gfx_font_rendering_fontations_enabled_AtStartup()) {
    if (SkrifaFontRef* font = skrifa_font_new(data->mFontData->Data(),
                                            data->mFontData->Length())) {
      platform->SetSkrifaFont(font);
    }
  }
#endif
  platform->mUserFontData = std::move(data);
  mCurrentSrcIndex = aEntry.mCurrentSrcIndex;
  mPrincipal = aEntry.mPrincipal;
  mSeenLocalSource = aEntry.mSeenLocalSource;
  mUnsupportedFormat = aEntry.mUnsupportedFormat;
  mFontDataLoadingState = aEntry.mFontDataLoadingState;
  mPlatformFontEntry = std::move(platform);
  mUserFontLoadState = STATUS_LOADED;
}

void gfxUserFontEntry::UpdateAttributes(gfxUserFontAttributes&& aAttr) {''')])

edit('layout/style/FontFaceSetImpl.h', [(
    '  virtual void MarkUserFontSetDirty() {}\n',
    '''  virtual void MarkUserFontSetDirty() {}

  void NonRuleFontFaceChanged();

  already_AddRefed<gfxUserFontEntry> UpdateFontFaceDescriptor(
      gfxUserFontEntry* aEntry, gfxUserFontAttributes&& aAttr,
      ErrorResult& aRv);
'''), (
    '  class UpdateUserFontEntryRunnable;\n',
    '''  class UpdateUserFontEntryRunnable;
  class UpdateFontFaceDescriptorRunnable;
  already_AddRefed<gfxUserFontEntry> UpdateFontFaceDescriptorOnMainThread(
      gfxUserFontEntry* aEntry, gfxUserFontAttributes&& aAttr);
''')])

edit('layout/style/FontFaceSetImpl.cpp', [(
    'void FontFaceSetImpl::UpdateUserFontEntry(gfxUserFontEntry* aEntry,',
    '''void FontFaceSetImpl::NonRuleFontFaceChanged() {
  AssertIsOnOwningThread();
  {
    RecursiveMutexAutoLock lock(mMutex);
    mNonRuleFacesDirty = true;
  }
  MarkUserFontSetDirty();
}

already_AddRefed<gfxUserFontEntry>
FontFaceSetImpl::UpdateFontFaceDescriptorOnMainThread(
    gfxUserFontEntry* aEntry, gfxUserFontAttributes&& aAttr) {
  MOZ_ASSERT(NS_IsMainThread());
  if (aEntry->LoadState() != gfxUserFontEntry::STATUS_LOADED) {
    UpdateUserFontEntry(aEntry, std::move(aAttr));
    return do_AddRef(aEntry);
  }

  RefPtr<gfxUserFontEntry> entry =
      CreateUserFontEntry(aEntry->SourceList().Clone(), std::move(aAttr));
  entry->InitializeFromLoadedEntry(*aEntry);
  return entry.forget();
}

class FontFaceSetImpl::UpdateFontFaceDescriptorRunnable final
    : public WorkerMainThreadRunnable {
 public:
  UpdateFontFaceDescriptorRunnable(FontFaceSetImpl* aSet,
                                   gfxUserFontEntry* aEntry,
                                   gfxUserFontAttributes&& aAttr)
      : WorkerMainThreadRunnable(
            GetCurrentThreadWorkerPrivate(),
            "FontFaceSetImpl :: UpdateFontFaceDescriptor"_ns),
        mSet(aSet),
        mEntry(aEntry),
        mAttr(std::move(aAttr)) {}

  bool MainThreadRun() override {
    mResult = mSet->UpdateFontFaceDescriptorOnMainThread(mEntry,
                                                       std::move(mAttr));
    return true;
  }

  already_AddRefed<gfxUserFontEntry> TakeResult() { return mResult.forget(); }

 private:
  RefPtr<FontFaceSetImpl> mSet;
  RefPtr<gfxUserFontEntry> mEntry;
  gfxUserFontAttributes mAttr;
  RefPtr<gfxUserFontEntry> mResult;
};

already_AddRefed<gfxUserFontEntry> FontFaceSetImpl::UpdateFontFaceDescriptor(
    gfxUserFontEntry* aEntry, gfxUserFontAttributes&& aAttr, ErrorResult& aRv) {
  AssertIsOnOwningThread();
  if (NS_IsMainThread()) {
    return UpdateFontFaceDescriptorOnMainThread(aEntry, std::move(aAttr));
  }
  auto task = MakeRefPtr<UpdateFontFaceDescriptorRunnable>(
      this, aEntry, std::move(aAttr));
  task->Dispatch(GetCurrentThreadWorkerPrivate(), Canceling, aRv);
  if (aRv.Failed()) {
    return nullptr;
  }
  return task->TakeResult();
}

void FontFaceSetImpl::UpdateUserFontEntry(gfxUserFontEntry* aEntry,''')])

edit('layout/style/FontFaceImpl.h', [(
    '  void SetUserFontEntry(gfxUserFontEntry* aEntry);',
    '''  void SetUserFontEntry(gfxUserFontEntry* aEntry,
                        bool aUpdateStatus = true);''')])

original = (root / 'original/layout/style/FontFaceImpl.cpp').read_text()
start = original.index('void FontFaceImpl::DescriptorUpdated() {')
end = original.index('\nFontFaceLoadStatus FontFaceImpl::Status()', start)
edit('layout/style/FontFaceImpl.cpp', [(
    original[start:end],
    '''void FontFaceImpl::DescriptorUpdated() {
  if (!mUserFontEntry) {
    return;
  }
  if (mInFontFaceSet) {
    mFontFaceSet->NonRuleFontFaceChanged();
  }
  for (auto& set : mOtherFontFaceSets) {
    set->NonRuleFontFaceChanged();
  }
}
'''), (
    '  bool changed = false;\n  const bool valid = [&] {',
    '''  // Parse without publishing descriptors until provider preparation succeeds.
  RefPtr<StyleLockedFontFaceRule> previousDescriptors = mDescriptors;
  RefPtr<Entry> previousEntry = mUserFontEntry;
  RefPtr<StyleLockedFontFaceRule> descriptors =
      Servo_FontFaceRule_Clone(GetData()).Consume();
  bool changed = false;
  const bool valid = [&] {'''), (
    'Servo_FontFaceRule_SetDescriptor(GetData(), aFontDesc, &aValue, url,',
    'Servo_FontFaceRule_SetDescriptor(descriptors, aFontDesc, &aValue, url,'), (
    'Servo_FontFaceRule_SetDescriptor(GetData(), aFontDesc, &quoted, url,',
    'Servo_FontFaceRule_SetDescriptor(descriptors, aFontDesc, &quoted, url,'), (
    '''  if (aFontDesc == FontFaceDescriptorId::UnicodeRange) {
    mUnicodeRangeDirty = true;
  }

  return true;
}''',
    '''  RefPtr<gfxUserFontEntry> entry;
  if (previousEntry) {
    gfxUserFontAttributes attr;
    MOZ_RELEASE_ASSERT(GetAttributesFromRule(descriptors, attr));
    entry = mFontFaceSet->UpdateFontFaceDescriptor(
        previousEntry, std::move(attr), aRv);
    if (aRv.Failed()) {
      return false;
    }
    if (!mOwner || mDescriptors != previousDescriptors ||
        mUserFontEntry != previousEntry) {
      aRv.ThrowUncatchableException();
      return false;
    }
  }

  mDescriptors = std::move(descriptors);
  if (aFontDesc == FontFaceDescriptorId::UnicodeRange) {
    mUnicodeRangeDirty = true;
  }
  if (entry) {
    // Keep a queued native-load completion from settling the promise early.
    SetUserFontEntry(entry, false);
  }
  return true;
}'''), (
    'void FontFaceImpl::SetUserFontEntry(gfxUserFontEntry* aEntry) {',
    '''void FontFaceImpl::SetUserFontEntry(gfxUserFontEntry* aEntry,
                                    bool aUpdateStatus) {'''), (
    '  if (newStatus > mStatus) {',
    '  if (aUpdateStatus && newStatus > mStatus) {')])

patch = ''
for source in sorted((root / 'original').rglob('*')):
    if source.is_file():
        name = source.relative_to(root / 'original').as_posix()
        patch += ''.join(difflib.unified_diff(
            source.read_text().splitlines(True),
            (root / 'candidate' / name).read_text().splitlines(True),
            fromfile='a/' + name, tofile='b/' + name))
(root / 'common.patch').write_text(patch)
