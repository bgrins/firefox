int main(){std::string line;while(std::getline(std::cin,line)){
 std::istringstream in(line);std::string id;unsigned encoding,compression,option,wrap,svg,combined,lineStart,startOriginal,lengthOriginal,start,length,n;double width;
 if(!(in>>id>>encoding>>compression>>option>>wrap>>svg>>combined>>lineStart>>startOriginal>>lengthOriginal>>start>>length>>width>>n))return 2;
 std::u16string units;std::string bytes;for(unsigned i=0;i<n;i++){unsigned c;in>>c;units.push_back(c);bytes.push_back(char(c));}std::string mask;in>>mask;assert(in);
 gfxSkipChars skip;std::vector<char16_t>wide(n+1);std::vector<uint8_t>narrow(n+1);uint8_t context=0;nsTextFrameUtils::Flags flags{};unsigned outLength;
 if(encoding==16)outLength=nsTextFrameUtils::TransformText(units.data(),n,wide.data(),nsTextFrameUtils::CompressionMode(compression),&context,&skip,&flags,nullptr)-wide.data();
 else {outLength=nsTextFrameUtils::TransformText(reinterpret_cast<const uint8_t*>(bytes.data()),n,narrow.data(),nsTextFrameUtils::CompressionMode(compression),&context,&skip,&flags,nullptr)-narrow.data();for(unsigned i=0;i<outLength;i++)wide[i]=narrow[i];}
 gfxTextRun run;run.glyphs.resize(outLength);run.advances.assign(outLength,1);run.mCharacterGlyphs=run.glyphs.data();
 for(unsigned i=0;i<outLength;i++){auto&g=run.glyphs[i];g.mValue=(wide[i]==' '?gfxTextRun::CompressedGlyph::FLAG_CHAR_IS_SPACE:0)|(wide[i]=='\t'?gfxTextRun::CompressedGlyph::FLAG_CHAR_IS_TAB:0)|(wide[i]=='\n'?gfxTextRun::CompressedGlyph::FLAG_CHAR_IS_NEWLINE:0);g.SetCanBreakBefore(mask=="-"?0:mask.at(i)-'0');}
 nsTextFrame frame;frame.state=lineStart?TEXT_START_OF_LINE:0;frame.style.mHyphens=StyleHyphens(option);frame.style.mTextWrapMode=wrap?mozilla::StyleTextWrapMode::Wrap:mozilla::StyleTextWrapMode::NoWrap;frame.svg=svg;frame.computed.combined=combined;
 CharacterDataBuffer data;data.mState={encoding==16,n};data.m2b=units.data();data.m1b=bytes.data();gfxSkipCharsIterator iter(skip,0,startOriginal);nsTextFrame::PropertyProvider provider(&run,&frame,data,iter,lengthOriginal);
 assert(start+length<=outLength);std::vector<gfxTextRun::HyphenType>hyphens(length);provider.GetHyphenationBreaks({start,start+length},hyphens.data());
 std::cout<<id<<' '<<outLength<<' ';for(unsigned i=0;i<outLength;i++)std::cout<<unsigned(wide[i])<<',';std::cout<<' ';gfxSkipCharsIterator pos(skip);for(unsigned i=0;i<outLength;i++)std::cout<<pos.ConvertSkippedToOriginal(i)<<',';std::cout<<' ';for(auto t:hyphens)std::cout<<unsigned(t);std::cout<<' ';
 gfxTextRun::Metrics metrics;bool used=false;uint32_t last=UINT32_MAX;auto priority=gfxBreakPriority::eNoBreak;auto fit=run.BreakAndMeasureText(start,length,lineStart,width,provider,gfxTextRun::eNoSuppressBreak,gfxFont::LOOSE_INK_EXTENTS,nullptr,false,false,false,nullptr,metrics,used,last,priority);
 std::cout<<fit<<' '<<used<<' '<<last<<' '<<unsigned(priority)<<' '<<metrics.mAdvanceWidth<<'\n';
}}
