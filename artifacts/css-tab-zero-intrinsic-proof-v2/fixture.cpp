static uint64_t bits(double x){uint64_t out;std::memcpy(&out,&x,8);return out;}
static double fromBits(uint64_t x){double out;std::memcpy(&out,&x,8);return out;}
static void printEvents(){
 std::cout<<'[';bool first=true;for(auto& row:events){if(!first)std::cout<<',';first=false;std::cout<<'['<<row[0]<<','<<row[1]<<','<<row[2]<<']';}std::cout<<']';
}
int main(){
 static_assert(sizeof(gfxFloat)==8&&sizeof(nscoord)==4);
 std::cout<<std::setprecision(17);
 int id,mode;
 while(std::cin>>id>>mode){
  events.clear();
  if(mode==0){uint64_t x,w,m;std::cin>>x>>w>>m;double result=AdvanceToNextTab(fromBits(x),fromBits(w),fromBits(m));
   std::cout<<"{\"id\":"<<id<<",\"mode\":0,\"bits\":"<<bits(result)<<"}\n";continue;}
  uint32_t n,begin,end;int kind,width,minimum,initial,letter,model,flags,split;
  std::cin>>n>>begin>>end>>kind>>width>>minimum>>initial>>letter>>model>>flags>>split;
  assert(n<=1000&&begin<=end&&end<=n);
  nsTextFrame frame;frame.start=begin;frame.end=end;frame.run.logicalLength=n;
  frame.run.glyphs.resize(n+1);frame.buffer.chars.resize(n);
  for(uint32_t i=0;i<n;i++){int advance;std::cin>>advance;assert(advance>=-1);frame.run.glyphs[i]={advance==-1,advance==-1?0u:uint32_t(advance)};frame.buffer.chars[i]=advance==-1?'\t':'A';}
  frame.run.fm=&frame.fm;frame.fm.group.font.metrics.zero=2*minimum;
  frame.text.mTabSize.isLength=kind==0;
  frame.text.mTabSize.length._0.value=width;frame.text.mTabSize.number._0=double(width)/20;
  frame.text.mLetterSpacing.value=letter;frame.style.combined=flags&2;frame.text.wrap=flags&4;
  frame.text.overflow=(flags&4)?StyleOverflowWrap::Anywhere:StyleOverflowWrap::Normal;
  failRun=flags&1;firstLetter=flags&16;letterModel=model;
  gfxContext context;InlineData data;data.mCurrentLine=initial;data.mAtStartOfLine=!(flags&8);data.mLineIsEmpty=!(flags&8);
  if(mode==1||mode==2){
   auto call=[&](){if(mode==1)frame.AddInlineMinISizeForFlow(&context,&data,nsTextFrame::eInflated);else frame.AddInlinePrefISizeForFlow(&context,&data,nsTextFrame::eInflated);};
   if(split>=int(begin)&&split<=int(end)){frame.end=split;call();frame.start=split;frame.end=end;call();}else call();
   std::cout<<"{\"id\":"<<id<<",\"mode\":"<<mode<<",\"state\":["<<data.mCurrentLine<<','<<data.mTrailingWhitespace<<','<<data.mAtStartOfLine<<','<<data.mLineIsEmpty<<','<<data.mSkipWhitespace<<"],\"events\":";printEvents();std::cout<<"}\n";
  }else{
   assert(mode>=3&&mode<=8);gfxSkipCharsIterator iter{begin};
   if(mode==8){frame.property=new nsTextFrame::TabWidthStore(0);frame.property->mLimit=n;}
   nsTextFrame::PropertyProvider provider(&frame.run,&frame.text,frame.buffer,&frame,iter,end-begin,mode==6?nullptr:&frame,initial,nsTextFrame::eInflated,!(flags&8));
   std::vector<gfxTextRun::PropertyProvider::Spacing> spacing(end-begin+1);
   bool present=false;
   if(mode==6||mode==7||mode==8){assert(width>0);provider.CalcTabWidths(Range(begin,end),width);}
   else{
    if(mode==4){auto middle=begin+(end-begin)/2;provider.GetSpacing(Range(begin,middle),spacing.data());}
    present=provider.GetSpacing(Range(begin,end),spacing.data());
    if(mode==4)present=provider.GetSpacing(Range(begin,end),spacing.data());
    if(mode==5){nsTextFrame::PropertyProvider display(&frame,iter,nsTextFrame::eInflated,&frame.fm);present=display.GetSpacing(Range(begin,end),spacing.data());}
   }
   double value=initial;
   for(uint32_t i=begin;i<end;i++)value+=frame.run.glyphs[i].advance+spacing[i-begin].mBefore+spacing[i-begin].mAfter;
   std::cout<<"{\"id\":"<<id<<",\"mode\":"<<mode<<",\"value\":"<<value<<",\"state\":["<<provider.mOffsetFromBlockOriginForTabs<<','<<provider.mTabWidthsAnalyzedLimit<<','<<provider.mMinTabAdvance<<','<<present<<"],\"spacing\":[";
   for(uint32_t i=begin;i<end;i++){if(i>begin)std::cout<<',';std::cout<<'['<<spacing[i-begin].mBefore<<','<<spacing[i-begin].mAfter<<']';}
   std::cout<<"],\"cache\":[";
   if(frame.property){std::cout<<frame.property->mLimit<<','<<frame.property->mValidForContentOffset;for(auto& w:frame.property->mWidths)std::cout<<",["<<w.mOffset<<','<<w.mWidth<<']';}
   std::cout<<"],\"events\":";printEvents();std::cout<<"}\n";
  }
  delete frame.property;
 }
 assert(std::cin.eof());
}
