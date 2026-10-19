struct CaptureProperties:gfxTextRun::PropertyProvider{
 std::vector<gfxTextRun::HyphenType>hyphens;
 std::vector<Spacing>spacing;
 StyleHyphens option=StyleHyphens::Auto;
 double hyphenWidth=1;int letterSpacing=0;
 mutable std::vector<std::pair<unsigned,unsigned>>requests;
 void GetHyphenationBreaks(gfxTextRun::Range r,gfxTextRun::HyphenType*out)const override{assert(r.end<=hyphens.size());requests.push_back({r.start,r.end});std::copy(hyphens.begin()+r.start,hyphens.begin()+r.end,out);}
 StyleHyphens GetHyphensOption()const override{return option;}
 double GetHyphenWidth()const override{return hyphenWidth;}
 gfx::ShapedTextFlags GetShapedTextFlags()const override{return {};}
 bool GetSpacing(gfxTextRun::Range r,Spacing*out)const override{assert(r.end<=spacing.size());std::copy(spacing.begin()+r.start,spacing.begin()+r.end,out);return true;}
 already_AddRefed<DrawTarget>GetDrawTarget()const override{return {};}
 uint32_t GetAppUnitsPerDevUnit()const override{return 1;}
 nscoord LetterSpacing()const override{return letterSpacing;}
};
int main(){
 std::string line;while(std::getline(std::cin,line)){
  std::istringstream in(line);std::string id;unsigned start,length,option,suppress,lineBefore,wordWrap,whiteWrap,breakSpaces,trim,flags,n;double width;CaptureProperties p;
  if(!(in>>id>>start>>length>>width>>option>>suppress>>lineBefore>>wordWrap>>whiteWrap>>breakSpaces>>trim>>flags>>p.hyphenWidth>>p.letterSpacing>>n))return 2;
  gfxTextRun run;run.glyphs.resize(n);run.advances.resize(n);run.mCharacterGlyphs=run.glyphs.data();run.mFlags=gfx::ShapedTextFlags(flags);p.hyphens.resize(n);p.spacing.resize(n);p.option=StyleHyphens(option);
  for(unsigned i=0;i<n;i++){
   unsigned kind,space,tab,newline,cluster,ligature,hyphen;in>>kind>>space>>tab>>newline>>cluster>>ligature>>run.advances[i]>>p.spacing[i].mBefore>>p.spacing[i].mAfter>>hyphen;
   auto&g=run.glyphs[i];g.mValue=(cluster?0:gfxTextRun::CompressedGlyph::FLAG_NOT_CLUSTER_START)|(ligature?0:gfxTextRun::CompressedGlyph::FLAG_NOT_LIGATURE_GROUP_START)|(space?gfxTextRun::CompressedGlyph::FLAG_CHAR_IS_SPACE:0)|(tab?gfxTextRun::CompressedGlyph::FLAG_CHAR_IS_TAB:0)|(newline?gfxTextRun::CompressedGlyph::FLAG_CHAR_IS_NEWLINE:0);g.SetCanBreakBefore(kind);p.hyphens[i]=gfxTextRun::HyphenType(hyphen);
  }
  assert(in&&start<=n);gfxTextRun::Metrics metrics;gfxTextRun::TrimmableWS trailing;bool used=false;uint32_t last=UINT32_MAX;auto priority=gfxBreakPriority::eNoBreak;
  auto fit=run.BreakAndMeasureText(start,length,lineBefore,width,p,gfxTextRun::SuppressBreak(suppress),gfxFont::LOOSE_INK_EXTENTS,nullptr,wordWrap,whiteWrap,breakSpaces,trim?&trailing:nullptr,metrics,used,last,priority);
  std::cout<<id<<' '<<fit<<' '<<used<<' '<<last<<' '<<unsigned(priority)<<' '<<trailing.mCount<<' '<<trailing.mAdvance<<' '<<metrics.mAdvanceWidth<<' ';
  for(auto [a,b]:p.requests)std::cout<<a<<':'<<b<<',';std::cout<<'\n';
 }
}
