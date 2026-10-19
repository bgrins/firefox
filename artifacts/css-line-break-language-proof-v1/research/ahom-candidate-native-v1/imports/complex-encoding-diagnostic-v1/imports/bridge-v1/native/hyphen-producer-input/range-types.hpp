struct DrawTarget{};
struct gfxMissingFontRecorder{};
namespace nsTextFrameUtils{struct Flags{enum{NoBreaks=1,IsTransformed=2,HasTrailingBreak=4};};}
struct gfxSkipChars { std::vector<bool> skipped; };
class gfxSkipCharsIterator{
 const gfxSkipChars* data;size_t original=0;
 public:explicit gfxSkipCharsIterator(const gfxSkipChars& d):data(&d){}
 bool IsOriginalCharSkipped()const{return original<data->skipped.size()&&data->skipped[original];}
 uint32_t GetSkippedOffset()const{uint32_t out=0;for(size_t i=0;i<original;i++)out+=!data->skipped.at(i);return out;}
 void AdvanceOriginal(int32_t n){assert(n>=0&&original+size_t(n)<=data->skipped.size());original+=n;}
};
struct gfxTextRun{
 struct Range{uint32_t start,end;Range(uint32_t a,uint32_t b):start(a),end(b){assert(a<=b);}uint32_t Length()const{return end-start;}};
 struct CompressedGlyph{
  enum{FLAG_BREAK_TYPE_NONE=0,FLAG_BREAK_TYPE_NORMAL=1,FLAG_BREAK_TYPE_HYPHEN=2,FLAG_BREAK_TYPE_EMERGENCY=3};
  uint8_t kind=0;bool cluster=true,space=false;
  bool IsClusterStart()const{return cluster;}bool CharIsSpace()const{return space;}
  uint32_t SetCanBreakBefore(uint8_t value){uint32_t changed=kind!=value;kind=value;return changed;}
 };
 gfxSkipChars skip;std::vector<CompressedGlyph> glyphs;CompressedGlyph* mCharacterGlyphs=nullptr;uint32_t flags=2;
 void SetLength(size_t n){glyphs.resize(n);mCharacterGlyphs=glyphs.data();}
 uint32_t GetLength()const{return glyphs.size();}const gfxSkipChars& GetSkipChars()const{return skip;}
 uint32_t GetFlags2()const{return flags;}void ClearFlagBits(uint32_t f){flags&=~f;}void SetFlagBits(uint32_t f){flags|=f;}
 bool SetPotentialLineBreaks(Range,const uint8_t*);
};
struct nsTransformedTextRun:gfxTextRun{
 bool needsRebuild=true;size_t finishes=0;std::vector<bool> capitalization;
 void SetCapitalization(uint32_t start,uint32_t n,const bool*p){assert(start+n<=GetLength());if(capitalization.size()!=GetLength())capitalization.resize(GetLength());for(size_t i=0;i<n;i++)capitalization[start+i]=p[i];needsRebuild=true;}
 void FinishSettingProperties(DrawTarget*,gfxMissingFontRecorder*){needsRebuild=false;finishes++;}
};
struct AutoNumber{int value=-1;bool IsAuto()const{return value<0;}int AsNumber()const{return value;}bool operator==(const AutoNumber&)const=default;};
struct LimitChars{AutoNumber total_word_length,pre_hyphen_length,post_hyphen_length;bool operator==(const LimitChars&)const=default;};
enum class StyleWordBreak{Normal,BreakAll,KeepAll};
enum class StyleLineBreak{Auto,Normal,Loose,Strict,Anywhere};
enum class StyleHyphens{None,Manual,Auto};
struct StyleTextTransform{enum{CAPITALIZE=1};};
struct nsStyleText{
 LimitChars mHyphenateLimitChars;StyleWordBreak wordBreak=StyleWordBreak::Normal;StyleLineBreak mLineBreak=StyleLineBreak::Auto;StyleHyphens mHyphens=StyleHyphens::Auto;int mTextTransform=0;bool wrap=true;
 StyleWordBreak EffectiveWordBreak()const{return wordBreak;}template<class T>bool WhiteSpaceCanWrap(T*)const{return wrap;}
};
struct nsStyleFont{bool mExplicitLanguage=true;nsAtom* language=nullptr;nsAtom*GetLangAtom()const{return language;}};
struct nsIFrame{nsStyleText style;const nsStyleText*StyleText()const{return &style;}};
struct CharacterDataBuffer{std::u16string units;int32_t GetLength()const{return units.size();}};
struct nsTextFrame:nsIFrame{
 int32_t offset=0;nsTextFrame*next=nullptr;struct CharacterDataBuffer*buffer=nullptr;nsStyleFont font;
 int32_t GetContentOffset()const{return offset;}nsTextFrame*GetNextContinuation()const{return next;}
 const struct CharacterDataBuffer&CharacterDataBuffer()const{return *buffer;}const nsStyleFont*StyleFont()const{return &font;}
};
inline bool IsTrimmableSpace(const CharacterDataBuffer&b,int32_t i,const nsStyleText*){auto c=b.units.at(i);return c==32||c==9||c==10||c==13;}
