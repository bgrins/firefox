static std::string traceCase;
extern "C" void language_trace(const char* event){std::cout<<traceCase<<" EVENT "<<event<<"\n";}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 std::ifstream dict(argv[1],std::ios::binary);gHyphenator.mDict.bytes.assign(std::istreambuf_iterator<char>(dict),{});
 if(!mapped_hyph_is_valid_hyphenator(gHyphenator.mDict.bytes.data(),gHyphenator.mDict.bytes.size()))return 3;
 nsAtom language{"en-US"};std::string line;
 while(std::getline(std::cin,line)){
  std::istringstream in(line);std::string id;unsigned encoding,skip,nflows;in>>id>>encoding>>skip>>nflows;traceCase=id;
  nsIFrame container;BuildTextRunsScanner scanner;scanner.mLineContainer=&container;scanner.mSkipIncompleteTextRuns=skip;scanner.mDoubleByteText=encoding==16;
  nsTransformedTextRun run;std::vector<std::unique_ptr<CharacterDataBuffer>> buffers;std::vector<std::vector<nsTextFrame>> frames;std::vector<std::unique_ptr<nsIFrame>> ancestors;
  std::vector<char16_t> transformed;std::vector<uint8_t> bytes;uint8_t incoming=0;
  for(unsigned flow=0;flow<nflows;flow++){
   unsigned n,nframes,ancestorWrap,accumulate;in>>n>>nframes>>ancestorWrap>>accumulate;
   auto buffer=std::make_unique<CharacterDataBuffer>();buffer->wide=encoding==16;
   for(unsigned i=0;i<n;i++){unsigned unit;in>>unit;buffer->units.push_back(unit);}
   for(unsigned i=0;i<n;i++){unsigned skipped;in>>skipped;if(accumulate<2){if(skipped)run.skip.SkipChar();else run.skip.KeepChar();if(!skipped){transformed.push_back(buffer->units[i]);bytes.push_back(buffer->units[i]);}}}
   if(accumulate>=2){
    nsTextFrameUtils::Flags flags{};auto compression=nsTextFrameUtils::CompressionMode(accumulate-2);
    if(encoding==16){std::vector<char16_t> output(n+1);auto end=nsTextFrameUtils::TransformText(buffer->units.data(),n,output.data(),compression,&incoming,&run.skip,&flags,&language);transformed.insert(transformed.end(),output.data(),end);}
    else{std::vector<uint8_t> input(buffer->units.begin(),buffer->units.end()),output(n+1);auto end=nsTextFrameUtils::TransformText(input.data(),n,output.data(),compression,&incoming,&run.skip,&flags,&language);bytes.insert(bytes.end(),output.data(),end);for(auto p=output.data();p!=end;++p)transformed.push_back(*p);}
   }
   auto ancestor=std::make_unique<nsIFrame>();ancestor->style.wrap=ancestorWrap;ancestor->style.mTextWrapMode=ancestorWrap?StyleTextWrapMode::Wrap:StyleTextWrapMode::NoWrap;
   frames.emplace_back(nframes);auto& group=frames.back();
   for(unsigned i=0;i<nframes;i++){
    int offset,total,pre,post;unsigned flags;in>>offset>>total>>pre>>post>>flags;
    auto& f=group[i];f.offset=offset;f.buffer=buffer.get();f.font.language=&language;f.next=i+1<nframes?&group[i+1]:nullptr;
    f.style.mHyphenateLimitChars={{total},{pre},{post}};f.style.wrap=!(flags&1);f.style.mTextWrapMode=(flags&1)?StyleTextWrapMode::NoWrap:StyleTextWrapMode::Wrap;f.style.mTextTransform=(flags&2)?1:0;f.style.mHyphens=(flags&4)?StyleHyphens::None:(flags&8)?StyleHyphens::Manual:StyleHyphens::Auto;
    f.style.mLineBreak=(flags&16)?StyleLineBreak::Anywhere:StyleLineBreak::Auto;
    if(accumulate>=2){StyleWhiteSpaceCollapse modes[]={StyleWhiteSpaceCollapse::Preserve,StyleWhiteSpaceCollapse::PreserveBreaks,StyleWhiteSpaceCollapse::Collapse,StyleWhiteSpaceCollapse::PreserveSpaces};f.style.mWhiteSpaceCollapse=modes[accumulate-2];}
   }
   scanner.mMappedFlows.AppendElement({&group[0],nullptr,ancestor.get()});
   if(accumulate)for(auto& frame:group)scanner.AccumulateRunInfo(&frame);
   buffers.push_back(std::move(buffer));ancestors.push_back(std::move(ancestor));
  }
  assert(in);run.SetLength(transformed.size());
  for(size_t i=0;i<transformed.size();i++)if(transformed[i]==32)run.glyphs[i].mValue|=gfxTextRun::CompressedGlyph::FLAG_CHAR_IS_SPACE;
  scanner.SetupBreakSinksForTextRun(&run,encoding==16?static_cast<const void*>(transformed.data()):static_cast<const void*>(bytes.data()));
  std::vector<unsigned> offsets;for(auto&sink:scanner.mBreakSinks)offsets.push_back(sink->mOffsetIntoTextRun);
  scanner.FlushLineBreaks(&run);
  std::cout<<id<<" SINKS";for(auto offset:offsets)std::cout<<' '<<offset;
  std::cout<<" GLYPHS ";for(auto&glyph:run.glyphs)std::cout<<unsigned(glyph.CanBreakBefore());
  std::cout<<" FINISHES "<<run.finishes<<" NEEDS_REBUILD "<<run.needsRebuild<<" MAXLENGTH "<<scanner.mMaxTextLength<<"\n";
 }
 traceCase="shutdown";for(auto& action:shutdownActions)action();assert(language.refs==1);
}
