uint32_t rawGlyph(const gfxShapedText::CompressedGlyph& g) {
  uint32_t word; static_assert(sizeof(g)==sizeof(word)); memcpy(&word,&g,sizeof(word)); return word;
}
void printGlyphs(const gfxTextRun& text) {
  std::cout << '[';
  for(uint32_t i=0;i<text.GetLength();++i) {
    if(i) std::cout << ',';
    const auto& g=text.storage[i];
    std::cout << "[" << rawGlyph(g) << "," << text.GetAdvanceForGlyph(i) << ",[";
    if(!g.IsSimpleGlyph() && g.GetGlyphCount()) {
      auto d=text.GetDetailedGlyphs(i,g.GetGlyphCount());
      for(uint32_t j=0;j<g.GetGlyphCount();++j) {
        if(j)std::cout << ',';
        std::cout << '[' << d[j].mGlyphID << ',' << d[j].mAdvance << ',' << d[j].mOffset.x.value << ',' << d[j].mOffset.y.value << ']';
      }
    }
    std::cout << "]]";
  }
  std::cout << ']';
}
int main(int argc,char** argv) {
  std::cout << std::setprecision(17);
  if(argc==2 && std::string(argv[1])=="unicode") {
    for(uint32_t cp=0;cp<0x110000;++cp) {
      uint8_t row[4]={uint8_t(u_charType(cp)),unicode::GetGeneralCategory(cp),uint8_t(unicode::GetGenCategory(cp)),uint8_t(MayCharacterHaveEmphasisMark(cp))};
      std::cout.write(reinterpret_cast<char*>(row),4);
    }
    return 0;
  }
  if(argc==2 && std::string(argv[1])=="units") {
    for(uint32_t domain=0;domain<3;++domain) {
      uint32_t count=domain==0?256:domain==1?65536:0x100000;
      for(uint32_t cp=0;cp<count;++cp) {
        providerTrace.clear();
        gfxTextRun text;text.Initialize(domain==2?2:1);
        text.storage[0]=gfxShapedText::CompressedGlyph::MakeSimpleGlyph(123,456);
        text.storage[0].SetCanBreakBefore(3);
        char16_t units[2]={char16_t(cp),0};uint8_t byte=cp;
        if(domain==2) {
          units[0]=0xD800+cp/1024;units[1]=0xDC00+cp%1024;
          text.storage[1]=gfxShapedText::CompressedGlyph::MakeComplex(false,false);
          text.storage[1].SetIsFormattingControl();
        }
        BuildTextRunsScanner scanner{domain!=0};
        scanner.SetupTextEmphasisForTextRun(&text,domain==0?static_cast<const void*>(&byte):static_cast<const void*>(units));
        uint32_t words[3]={rawGlyph(text.storage[0]),domain==2?rawGlyph(text.storage[1]):0,0};
        const auto& g=text.storage[0];
        if(g.IsSimpleGlyph()) words[2]=g.GetSimpleAdvance()==123 && g.GetSimpleGlyph()==456;
        else {
          auto d=text.GetDetailedGlyphs(0,g.GetGlyphCount());
          words[2]=g.GetGlyphCount()==1 && d[0].mAdvance==123 && d[0].mGlyphID==456 && d[0].mOffset.x.value==0 && d[0].mOffset.y.value==0;
        }
        std::cout.write(reinterpret_cast<char*>(words),sizeof(words));
      }
    }
    return 0;
  }
  if(argc==2 && std::string(argv[1])=="arithmetic") {
    int32_t width;uint32_t total,index,count;bool final;
    while(std::cin >> width >> total >> index >> count >> final) {
      if(!total || index>total || count>total-index) return 2;
      auto data=ArithmeticFragment(width,total,index,count,final);
      std::cout << '[' << data.mPartAdvance << ',' << data.mPartWidth << ','
                << int(data.mClipBeforePart) << ',' << int(data.mClipAfterPart) << "]\n";
    }
    return std::cin.eof()?0:2;
  }
  uint32_t n,latin,start,end,vertical,hasProvider,providerEnabled,enableSpacing,failAllocation,runCount;
  int direction,letterSpacing;
  double markAdvance,x,y;
  while(std::cin >> n >> latin >> start >> end >> vertical >> direction >> hasProvider >> providerEnabled >> enableSpacing >> failAllocation >> markAdvance >> x >> y >> runCount >> letterSpacing) {
    providerTrace.clear();
    if(n>1000000 || start>end || end>n || (direction!=1 && direction!=-1) || runCount>n || (!n && runCount)) return 2;
    gfxTextRun text,mark; text.Initialize(n);mark.Initialize(1);
    text.vertical=vertical;text.direction=direction;text.mFlags=enableSpacing?gfx::ShapedTextFlags::TEXT_ENABLE_SPACING:0;
    std::vector<char16_t> units(n);std::vector<uint8_t> bytes(n);
    gfxTextRun::PropertyProvider provider;provider.enabled=providerEnabled;provider.letterSpacing=letterSpacing;provider.spacing.resize(n);
    for(uint32_t i=0;i<n;++i) {
      uint32_t cp,word,count;std::cin >> cp >> word >> count;
      if(cp>(latin?255u:65535u) || count>65535) return 2;
      units[i]=cp;bytes[i]=cp;
      std::vector<gfxShapedText::DetailedGlyph> details(count);
      for(auto& d:details)std::cin >> d.mGlyphID >> d.mAdvance >> d.mOffset.x.value >> d.mOffset.y.value;
      auto& g=text.storage[i];memcpy(&g,&word,sizeof(word));
      if(g.IsSimpleGlyph() ? count!=0 : count!=g.GetGlyphCount()) return 2;
      if(count) {
        auto dst=text.AllocateDetailedGlyphs(i,count);memcpy(dst,details.data(),count*sizeof(details[0]));
      }
      std::cin >> provider.spacing[i].mBefore >> provider.spacing[i].mAfter;
    }
    std::vector<gfxFont> fonts(runCount);
    uint32_t previous=0;
    for(uint32_t i=0;i<runCount;++i) {
      uint32_t offset;std::cin >> offset;
      if(offset>=n || (i==0?offset!=0:offset<=previous) || !text.IsClusterStart(offset) || !text.IsLigatureGroupStart(offset)) return 2;
      text.mGlyphRuns.AppendElement({&fonts[i],offset});previous=offset;
    }
    if(n && (!runCount || !text.IsClusterStart(0) || !text.IsLigatureGroupStart(0))) return 2;
    if((start<n && !text.IsClusterStart(start)) || (end<n && !text.IsClusterStart(end))) return 2;
    for(uint32_t i=1;i<n;++i) {
      if(text.IsLigatureGroupStart(i) && !text.IsClusterStart(i)) return 2;
      if(!latin && IsSurrogatePair(units[i-1],units[i]) && (text.IsClusterStart(i) || text.IsLigatureGroupStart(i))) return 2;
      if(!text.IsLigatureGroupStart(i) && (provider.spacing[i].mBefore || provider.spacing[i-1].mAfter)) return 2;
    }
    if(!std::cin) return 2;
    std::cout << "{\"before\":";printGlyphs(text);
    providerTrace.clear();
    BuildTextRunsScanner scanner{!bool(latin)};
    scanner.SetupTextEmphasisForTextRun(&text,latin?static_cast<const void*>(bytes.data()):static_cast<const void*>(units.data()));
    std::cout << ",\"after\":";printGlyphs(text);
    gfxContext context;gfx::PaletteCache palette;imgDrawingParams image;
    failSpacingAllocation=failAllocation;
    drawUnits.clear();
    text.DrawEmphasisMarks(&context,&mark,markAdvance,gfx::Point(x,y),gfxTextRun::Range(start,end),hasProvider?&provider:nullptr,palette,image);
    std::cout << ",\"draws\":[";
    for(size_t i=0;i<mark.emissions.size();++i) {
      if(i)std::cout << ',';
      std::cout << '[' << mark.emissions[i].x.value << ',' << mark.emissions[i].y.value << ']';
    }
    std::cout << "],\"draw_units\":[";
    for(size_t i=0;i<drawUnits.size();++i) { if(i)std::cout << ',';std::cout << drawUnits[i]; }
    std::cout << "],\"trace\":[";
    for(size_t i=0;i<providerTrace.size();++i) { if(i)std::cout << ',';std::cout << '"' << providerTrace[i] << '"'; }
    std::cout << "]}\n";
  }
  return 0;
}
