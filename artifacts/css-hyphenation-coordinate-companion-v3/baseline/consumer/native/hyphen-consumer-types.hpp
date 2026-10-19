namespace mozilla {enum class StyleTextWrapMode{Wrap,NoWrap};}
struct nsIFrame;
struct nsStyleText{
 mozilla::StyleTextWrapMode mTextWrapMode=mozilla::StyleTextWrapMode::Wrap;
 StyleHyphens mHyphens=StyleHyphens::Auto;
 __WRAP_STYLE__
 bool WhiteSpaceCanWrap(const nsIFrame*)const;
};
struct ComputedStyle{bool combined=false;bool IsTextCombined()const{return combined;}};
struct nsIFrame{
 nsStyleText style;ComputedStyle computed;bool svg=false;uint64_t state=0;
 bool IsInSVGTextSubtree()const{return svg;}const ComputedStyle*Style()const{return &computed;}
 const nsStyleText*StyleText()const{return &style;}bool HasAnyStateBits(uint64_t b)const{return state&b;}
};
struct CharacterDataBuffer{
 struct {bool mIs2b=true;uint32_t mLength=0;}mState;
 const char16_t*m2b=nullptr;const char*m1b=nullptr;
 const char16_t*Get2b()const{assert(mState.mIs2b);return m2b;}
 __CHAR_AT__
};
template<class A,class B>A AssertedCast(B x){assert(x>=0&&uint64_t(x)<=std::numeric_limits<A>::max());return A(x);}
struct nsTextFrame:nsIFrame{
 class PropertyProvider:public gfxTextRun::PropertyProvider{
  public:
  using Range=gfxTextRun::Range;using HyphenType=gfxTextRun::HyphenType;
  gfxTextRun*mTextRun;const nsStyleText*mTextStyle;const CharacterDataBuffer&mCharacterDataBuffer;nsTextFrame*mFrame;gfxSkipCharsIterator mStart;int32_t mLength;
  std::vector<Spacing>spacing;double hyphenWidth=1;int letterSpacing=0;mutable std::vector<std::pair<unsigned,unsigned>>requests;
  PropertyProvider(gfxTextRun*r,nsTextFrame*f,const CharacterDataBuffer&b,const gfxSkipCharsIterator&s,int32_t n):mTextRun(r),mTextStyle(f->StyleText()),mCharacterDataBuffer(b),mFrame(f),mStart(s),mLength(n),spacing(r->GetLength()){}
  void GetHyphenationBreaks(Range,HyphenType*)const override;
  StyleHyphens GetHyphensOption()const override{return mTextStyle->mHyphens;}
  double GetHyphenWidth()const override{return hyphenWidth;}
  gfx::ShapedTextFlags GetShapedTextFlags()const override{return {};}
  bool GetSpacing(Range r,Spacing*out)const override{std::copy(spacing.begin()+r.start,spacing.begin()+r.end,out);return true;}
  already_AddRefed<DrawTarget>GetDrawTarget()const override{return {};}
  uint32_t GetAppUnitsPerDevUnit()const override{return 1;}
  nscoord LetterSpacing()const override{return letterSpacing;}
 };
};
