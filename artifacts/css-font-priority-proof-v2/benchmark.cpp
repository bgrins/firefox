int main() {
  for (int count : {100, 1000, 10000}) {
    std::vector<gfxFontEntry> entries(count);
    std::vector<mozilla::fontlist::Face> faces(count);
    std::vector<BitSet> maps(count);
    gfxFontFamily family;
    family.mFamilyCharacterMap = {100,true};
    mozilla::fontlist::FontList list;
    list.families.resize(1);
    auto& shared = list.families[0];
    BitSet familyMap{100,true};
    shared.mCharacterMap = {&familyMap,100};
    gfxFontStyle style;
    style.style = StyleFontStyle::FromRaw(3072);
    for (int scenario=0; scenario<2; ++scenario) {
      family.mAvailableFonts.clear(); shared.faces.clear();
      for (int i=0; i<count; ++i) {
        auto& e=entries[i]; auto& f=faces[i];
        e.id=f.id=i; e.name=nsCString(std::to_string(i).c_str());
        int angle=scenario ? 3072 : 2816+(i%257);
        int weight=scenario ? 25600 : 64+(i*997)%63937;
        int width=scenario ? 6400 : 1+(i*137)%64000;
        e.mStyle=SlantStyleRange(StyleFontStyle::FromRaw(angle));
        e.mWeight=WeightRange(StyleFontWeight::FromRaw(weight));
        e.mWidth=WidthRange(StyleFontWidth::FromRaw(width));
        e.font={i,false};
        f.mStyle=e.mStyle;f.mWeight=e.mWeight;f.mWidth=e.mWidth;f.entry=&e;
        maps[i]={i,true};f.mCharacterMap={&maps[i],i};
        shared.faces.push_back({&f,i});family.mAvailableFonts.AppendElement(&e);
      }
      for (int op=1; op<=5; ++op) {
        int repeats=200000/count;
        for (int sample=0; sample<7; ++sample) {
          uint64_t checksum=0; providerCalls=0;
          auto start=std::chrono::steady_clock::now();
          auto cpuStart=std::clock();
          for(int repeat=0; repeat<repeats; ++repeat) {
            GlobalFontMatch match(88,0,style,FontPresentation::Any);
            if(op==1) {
              nsTArray<gfxFontEntry*> result;family.FindAllFontsForStyle(style,result,true);
              for(auto* e:result) checksum+=e->id+1;
            } else if(op==2) {
              nsTArray<mozilla::fontlist::Face*> result;shared.FindAllFacesForStyle(&list,style,result,false);
              for(auto* f:result) checksum+=f->id+1;
            } else {
              if(op==3)family.SearchAllFontsForChar(&match);
              if(op==4)shared.SearchAllFontsForChar(&list,&match);
              if(op==5)family.FindFontForChar(&match);
              if(match.mBestMatch)checksum+=match.mBestMatch->id+1;
            }
          }
          auto end=std::chrono::steady_clock::now();
          auto wallNs=std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count();
          auto ns=int64_t((std::clock()-cpuStart)*(1000000000.0/CLOCKS_PER_SEC));
          std::cout << count << ',' << scenario << ',' << op << ',' << sample << ',' << repeats << ',' << ns << ',' << providerCalls << ',' << checksum << ',' << wallNs << '\n';
        }
      }
    }
  }
}
