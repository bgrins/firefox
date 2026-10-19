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
 struct CompressedGlyph {
enum Flags : uint32_t {
      // Indicates that a cluster and ligature group starts at this
      // character; this character has a single glyph with a reasonable
      // advance and zero offsets. A "reasonable" advance
      // is one that fits in the available bits (currently 12) (specified
      // in appunits).
      FLAG_IS_SIMPLE_GLYPH = 0x80000000U,

      // These flags are applicable to both "simple" and "complex" records.
      COMMON_FLAGS_MASK = 0x70000000U,

      // Indicates whether a linebreak is allowed before this character;
      // this is a two-bit field that holds a FLAG_BREAK_TYPE_xxx value
      // indicating the kind of linebreak (if any) allowed here.
      FLAGS_CAN_BREAK_BEFORE = 0x60000000U,

      FLAGS_CAN_BREAK_SHIFT = 29U,
      FLAG_BREAK_TYPE_NONE = 0U,
      FLAG_BREAK_TYPE_NORMAL = 1U,
      FLAG_BREAK_TYPE_HYPHEN = 2U,
      // Allow break before this position if needed to avoid overflow:
      FLAG_BREAK_TYPE_EMERGENCY_WRAP = 3U,

      FLAG_CHAR_IS_SPACE = 0x10000000U,

      // Fields present only when FLAG_IS_SIMPLE_GLYPH is /true/.
      // The advance is stored in appunits as a 12-bit field:
      ADVANCE_MASK = 0x0FFF0000U,
      ADVANCE_SHIFT = 16,
      // and the glyph ID is stored in the low 16 bits.
      GLYPH_MASK = 0x0000FFFFU,

      // Fields present only when FLAG_IS_SIMPLE_GLYPH is /false/.
      // Non-simple glyphs may or may not have glyph data in the
      // corresponding mDetailedGlyphs entry. They have a glyph count
      // stored in the low 16 bits, and the following flag bits:
      GLYPH_COUNT_MASK = 0x0000FFFFU,

      // When NOT set, indicates that this character corresponds to a
      // missing glyph and should be skipped (or possibly, render the character
      // Unicode value in some special way). If there are glyphs,
      // the mGlyphID is actually the UTF16 character code. The bit is
      // inverted so we can memset the array to zero to indicate all missing.
      FLAG_NOT_MISSING = 0x010000U,
      FLAG_NOT_CLUSTER_START = 0x020000U,
      FLAG_NOT_LIGATURE_GROUP_START = 0x040000U,

      // This is a "merged glyph" representing multiple characters that result
      // from text-run transformation; if there is letter-spacing, it should be
      // applied between the detailed-glyph components.
      // Currently the only use of this is when es-zet is uppercased as SS.
      //
      // Note that in general, letter-spacing does not depend on this flag; it
      // is applied *between* CompressedGlyph records by textrun drawing and
      // measuring code. This flag only refers to letter-spacing between the
      // individual DetailedGlyph components of a single CompressedGlyph.
      FLAG_APPLY_LETTER_SPACING_BETWEEN_DETAILED_GLYPHS = 0x080000U,

      // Certain types of characters are marked so that they can be given
      // special treatment in rendering. This may require use of a "complex"
      // CompressedGlyph record even for a character that would otherwise be
      // treated as "simple".
      CHAR_TYPE_FLAGS_MASK = 0xF00000U,
      FLAG_CHAR_IS_TAB = 0x100000U,
      FLAG_CHAR_IS_NEWLINE = 0x200000U,
      // Per CSS Text Decoration Module Level 3, emphasis marks are not
      // drawn for any character in Unicode categories Z*, Cc, Cf, and Cn
      // which is not combined with any combining characters. This flag is
      // set for all those characters except 0x20 whitespace.
      FLAG_CHAR_NO_EMPHASIS_MARK = 0x400000U,
      // Per CSS Text, letter-spacing is not applied to formatting chars
      // (category Cf). We mark those in the textrun so as to be able to
      // skip them when setting up spacing in nsTextFrame.
      FLAG_CHAR_IS_FORMATTING_CONTROL = 0x800000U,

      // The bits 0x0F000000 are currently unused in non-simple glyphs.
    };
uint32_t mValue=0;
bool IsSimpleGlyph() const { return mValue & FLAG_IS_SIMPLE_GLYPH; }
bool IsClusterStart() const {
      return IsSimpleGlyph() || !(mValue & FLAG_NOT_CLUSTER_START);
    }
bool CharIsSpace() const { return mValue & FLAG_CHAR_IS_SPACE; }
uint8_t CanBreakBefore() const {
      return (mValue & FLAGS_CAN_BREAK_BEFORE) >> FLAGS_CAN_BREAK_SHIFT;
    }
uint32_t SetCanBreakBefore(uint8_t aCanBreakBefore) {
      MOZ_ASSERT(aCanBreakBefore <= 3, "Bogus break-flags value!");
      // Shift the input value to the relevant bit positions.
      uint32_t breakMask = uint32_t(aCanBreakBefore) << FLAGS_CAN_BREAK_SHIFT;
      // Determine which bits in the break field are changing (if any).
      uint32_t toggle = (breakMask ^ mValue) & FLAGS_CAN_BREAK_BEFORE;
      // Update the value, and return the bits that changed.
      mValue ^= toggle;
      return toggle;
    }
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
struct CharacterDataBuffer{std::u16string units;bool wide=true;bool Is2b()const{return wide;}int32_t GetLength()const{return units.size();}};
struct nsTextFrame:nsIFrame{
 enum class TextRunType{Inflated};
 nsIFrame* GetParent(){return nullptr;}gfxTextRun*GetTextRun(TextRunType){return nullptr;}
 int32_t GetContentLength()const{return std::max(0,std::min(next?next->offset:buffer->GetLength(),buffer->GetLength())-std::min(offset,buffer->GetLength()));}
 int32_t offset=0;nsTextFrame*next=nullptr;struct CharacterDataBuffer*buffer=nullptr;nsStyleFont font;
 int32_t GetContentOffset()const{return offset;}nsTextFrame*GetNextContinuation()const{return next;}
 const struct CharacterDataBuffer&CharacterDataBuffer()const{return *buffer;}const nsStyleFont*StyleFont()const{return &font;}
};
inline bool IsTrimmableSpace(const CharacterDataBuffer&b,int32_t i,const nsStyleText*){auto c=b.units.at(i);return c==32||c==9||c==10||c==13;}

bool gfxTextRun::SetPotentialLineBreaks(Range aRange,
                                        const uint8_t* aBreakBefore) {
  NS_ASSERTION(aRange.end <= GetLength(), "Overflow");

  uint32_t changed = 0;
  CompressedGlyph* cg = mCharacterGlyphs + aRange.start;
  const CompressedGlyph* const end = cg + aRange.Length();
  while (cg < end) {
    uint8_t canBreak = *aBreakBefore++;
    if (canBreak && !cg->IsClusterStart()) {
      // XXX If we replace the line-breaker with one based more closely
      // on UAX#14 (e.g. using ICU), this may not be needed any more.
      // Avoid possible breaks inside a cluster, EXCEPT when the previous
      // character was a space (compare UAX#14 rules LB9, LB10).
      if (cg == mCharacterGlyphs || !(cg - 1)->CharIsSpace()) {
        canBreak = CompressedGlyph::FLAG_BREAK_TYPE_NONE;
      }
    }
    // If a break is allowed here, set the break flag, but don't clear a
    // possible pre-existing emergency-break flag already in the run.
    if (canBreak) {
      changed |= cg->SetCanBreakBefore(canBreak);
    }
    ++cg;
  }
  return changed != 0;
}
