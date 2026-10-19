int main() {
  int id, operation, target, allow, presentation, count;
  while (std::cin >> id >> operation >> target >> allow >> presentation >> count) {
    assert(count >= 0 && count <= 16);
    events.clear();
    gfxFontStyle style;
    style.style = target == 30000 ? StyleFontStyle::OBLIQUE : StyleFontStyle::FromRaw(target);
    style.synthesisStyle = allow ? StyleFontSynthesisStyle::Auto : StyleFontSynthesisStyle::ObliqueOnly;
    int targetWeight, targetWidth, flags;
    std::cin >> targetWeight >> targetWidth >> flags;
    style.weight = StyleFontWeight::FromRaw(targetWeight);
    style.width = StyleFontWidth::FromRaw(targetWidth);
    std::array<gfxFontEntry, 16> entries;
    std::array<mozilla::fontlist::Face, 16> sharedFaces;
    std::array<BitSet, 16> maps;
    gfxFontFamily family;
    family.id = 100;
    family.mFamilyCharacterMap.id = 100;
    mozilla::fontlist::FontList list;
    list.families.resize(1);
    auto& shared = list.families[0];
    shared.id = 100;
    BitSet familyMap{100, true};
    shared.mCharacterMap = {&familyMap, 100};
    shared.initializedMap = shared.mCharacterMap;
    std::vector<int> scores;
    for (int i = 0; i < count; ++i) {
      int lo, hi, wl, wh, xl, xh, coverage, skip, ready, color, known, valid, present, size;
      std::cin >> lo >> hi >> wl >> wh >> xl >> xh >> coverage >> skip >> ready >> color >> known >> valid >> present >> size;
      assert((-23040 <= lo && lo <= hi && hi <= 23040) || (lo == 25600 && hi == 25600));
      assert(64 <= wl && wl <= wh && wh <= 64000);
      assert(0 <= xl && xl <= xh && xh <= 64000);
      auto& e = entries[i];
      e.id = i;
      e.name = nsCString(std::string(1, char('A' + i)).c_str());
      e.mStyle = SlantStyleRange(StyleFontStyle::FromRaw(lo), StyleFontStyle::FromRaw(hi));
      e.mWeight = WeightRange(StyleFontWeight::FromRaw(wl), StyleFontWeight::FromRaw(wh));
      e.mWidth = WidthRange(StyleFontWidth::FromRaw(xl), StyleFontWidth::FromRaw(xh));
      e.covered = coverage;
      e.skip = skip;
      e.fontReady = ready;
      e.font = {i, bool(color)};
      family.mAvailableFonts.AppendElement(&e);
      auto& f = sharedFaces[i];
      f.id = i;
      f.mStyle = e.mStyle;
      f.mWeight = e.mWeight;
      f.mWidth = e.mWidth;
      f.mSize = size;
      f.valid = valid;
      f.entry = present ? &e : nullptr;
      maps[i] = {i, bool(coverage)};
      f.mCharacterMap = {known ? &maps[i] : nullptr, i};
      shared.faces.push_back({present == 2 ? nullptr : &f, i});
      double distance = StyleDistance(e.mStyle, style.style, allow);
      assert(std::isfinite(distance) && distance * 256 == std::trunc(distance * 256));
      scores.push_back(int(distance * 256));
    }
    if (flags & 128) for (int i=0; i<count; ++i) entries[i].name = nsCString(std::string(1, char('Z'-i)).c_str());
    if ((flags & 256) && count > 1) {
      family.mAvailableFonts.back() = &entries[0];
      shared.faces.back() = shared.faces.front();
    }
    shared.initialized = !(flags & 1);
    shared.facesAvailable = !(flags & 2);
    if (flags & 4) shared.mCharacterMap = {nullptr, 100};
    if (flags & 16384) shared.initializedMap = {nullptr, 100};
    shared.initializationSucceeds = !(flags & 8);
    family.mFamilyCharacterMap.covered = familyMap.covered = !(flags & 16);
    family.mFamilyCharacterMapInitialized = !(flags & 32);
    shared.mIsSimple = flags & 64;
    events.clear();
    std::vector<int> selected;
    uint32_t globalCmaps = 0;
    GlobalFontMatch match(88, 0, style, FontPresentation(presentation));
    auto* platform = gfxPlatformFontList::PlatformFontList();
    platform->shared = nullptr;
    platform->whitelist = !(flags & 512);
    platform->platformFace = count ? &entries[0] : nullptr;
    platform->platformFamily = FontFamily(&family);
    useCmapsPolicy = !(flags & 512);
    parentProcess = !(flags & 2048);
    asyncFallback = flags & 2048;
    platform->mFontFamilies.families.clear();
    platform->mFontFamilies.families.push_back(&family);
    if (operation == 13) {
      selected = {int(sizeof(mozilla::fontlist::Pointer)), int(sizeof(mozilla::fontlist::Face))};
    } else if (operation == 1) {
      nsTArray<gfxFontEntry*> result;
      family.FindAllFontsForStyle(style, result, true);
      for (auto* e : result) selected.push_back(e->id);
    } else if (operation == 2) {
      nsTArray<mozilla::fontlist::Face*> result;
      shared.FindAllFacesForStyle(&list, style, result, false);
      for (auto* f : result) selected.push_back(f->id);
    } else if (operation == 3) {
      family.SearchAllFontsForChar(&match);
    } else if (operation == 4) {
      shared.SearchAllFontsForChar(&list, &match);
    } else if (operation == 5) {
      family.FindFontForChar(&match);
    } else if (operation == 6 || operation == 7 || operation == 10 || operation == 11) {
      std::array<gfxFontFamily,16> singleFamilies;
      if (operation >= 10) {
        platform->mFontFamilies.families.clear();
        list.families.clear();
        list.families.resize(count);
        for (int i=0; i<count; ++i) {
          auto& uf = singleFamilies[i];
          uf.id = 100+i;
          uf.mFamilyCharacterMap.id = 100+i;
          uf.mAvailableFonts.AppendElement(&entries[i]);
          uf.visible = !(i == 0 && (flags & 1024));
          platform->mFontFamilies.families.push_back(&uf);
          auto& sf = list.families[i];
          sf.id = 100+i;
          sf.faces.push_back({&sharedFaces[i],i});
          sf.mCharacterMap = sf.initializedMap = {&maps[i],i};
          sf.visible = uf.visible;
          sf.fullyInitialized = !(i == 0 && (flags & 2048));
        }
      }
      list.available = !(flags & 4096);
      if (operation == 7 || operation == 11) platform->shared = &list;
      FontFamily chosen;
      uint32_t cmapCount = 0;
      auto* font = platform->GlobalFontFallback(nullptr, 88, 0, Script::Common,
          FontPresentation(presentation), &style, cmapCount, chosen);
      globalCmaps = cmapCount;
      if (font) selected.push_back(font->id);
    } else if (operation == 8) {
      for (int raw = -23040; raw <= 23040; ++raw) {
        auto value = StyleFontStyle::FromRaw(raw);
        assert(value.Raw() == raw);
        assert(value.ToFloat() * 256 == raw);
        assert(StyleFontStyle::FromFloat(value.ToFloat()).Raw() == raw);
        SlantStyleRange range(value);
        assert(SlantStyleRange::FromScalar(range.AsScalar()) == range);
      }
      for (unsigned raw=0; raw<=64000; ++raw) {
        auto width = StyleFontWidth::FromRaw(raw);
        assert(width.Raw() == raw && width.ToFloat() * 64 == raw);
        assert(StyleFontWidth::FromFloat(width.ToFloat()).Raw() == raw);
        WidthRange range(width);
        assert(WidthRange::FromScalar(range.AsScalar()) == range);
        if (raw >= 64) {
          auto weight = StyleFontWeight::FromRaw(raw);
          assert(weight.Raw() == raw && weight.ToFloat() * 64 == raw);
          assert(StyleFontWeight::FromFloat(weight.ToFloat()).Raw() == raw);
          WeightRange weights(weight);
          assert(WeightRange::FromScalar(weights.AsScalar()) == weights);
        }
      }
      assert(StyleFontStyle::ITALIC.Raw() == 25600);
      assert(StyleFontStyle::OBLIQUE.Raw() == StyleFontStyle::DEFAULT_OBLIQUE_DEGREES * 256);
      selected.push_back(StyleFontStyle::OBLIQUE.Raw());
      selected.push_back(StyleFontStyle::DEFAULT_OBLIQUE_DEGREES);
    } else if (operation == 12) {
      nsTArray<mozilla::fontlist::Face::InitData> init;
      for (int i=0; i<count; ++i) init.AppendElement({i,entries[i].mWeight,entries[i].mWidth,entries[i].mStyle,&maps[i],entries[i].name,0,&entries[i]});
      shared.AddFaces(&list,init);
      selected.push_back(shared.mIsSimple);
      nsTArray<mozilla::fontlist::Face*> result;
      shared.FindAllFacesForStyle(&list,style,result,false);
      for (auto* f : result) selected.push_back(f->id);
    } else if (operation == 9) {
      family.CheckForSimpleFamily();
      selected.push_back(family.mIsSimpleFamily);
      nsTArray<gfxFontEntry*> result;
      family.FindAllFontsForStyle(style, result, true);
      for (auto* e : result) selected.push_back(e->id);
    }
    if (operation >= 3 && operation <= 5 && match.mBestMatch)
      selected.push_back(match.mBestMatch->id);
    std::cout << id << '|';
    for (size_t i = 0; i < scores.size(); ++i) std::cout << (i ? "," : "") << scores[i];
    std::cout << '|';
    for (size_t i = 0; i < selected.size(); ++i) std::cout << (i ? "," : "") << selected[i];
    std::cout << '|' << match.mCount << ',' << match.mCmapsTested << ',' << globalCmaps << '|';
    for (size_t i = 0; i < events.size(); ++i) std::cout << (i ? "," : "") << events[i];
    std::cout << '\n';
    for (auto* p : allocations) std::free(p);
    allocations.clear();
  }
}
