inline uint32_t operator&(TextFlags a,TextFlags b){return uint16_t(a)&uint16_t(b);}
struct TextRunMappedFlow{nsTextFrame*mStartFrame;int32_t mDOMOffsetToBeforeTransformOffset;uint32_t mContentLength;};
struct TextRunUserData{uint32_t mMappedFlowCount=0,mLastFlowIndex=0;};
inline TextRunUserData*CreateUserData(size_t n){auto*p=static_cast<TextRunUserData*>(::operator new(sizeof(TextRunUserData)+n*sizeof(TextRunMappedFlow)));new(p)TextRunUserData;p->mMappedFlowCount=n;return p;}
inline void DestroyUserData(TextRunUserData*p){::operator delete(p);}
struct TextEditor{bool IsAllMasked()const{return true;}uint32_t UnmaskedStart()const{return 0;}uint32_t UnmaskedEnd()const{return 0;}};
struct nsContentUtils{static const TextEditor*GetExtantTextEditorFromAnonymousNode(nsIContent*){return nullptr;}};
namespace StaticPrefs{inline bool layout_css_text_transform_uppercase_eszett_enabled(){return false;}}
struct nsTransformedCharStyle{bool mForceNonFullWidth=false,mMaskPassword=false;nsTransformedCharStyle(ComputedStyle*,nsPresContext*){}};
template<class T,class...A>RefPtr<T>MakeRefPtr(A&&...a){return new T(std::forward<A>(a)...);}
struct gfxTextRunFactory{struct Parameters{DrawTarget*draw;void*data;gfxSkipChars*skip;uint32_t*breaks;uint32_t breakCount;int32_t appUnits;};};
struct gfxFont{bool HasCharacter(uint32_t)const{return true;}};
struct gfxFontGroup{
 gfxFont*GetFirstValidFont(uint32_t){static gfxFont f;return &f;}
 template<class C>gfxTextRun*MakeTextRun(const C*text,uint32_t n,gfxTextRunFactory::Parameters*p,gfx::ShapedTextFlags flags,TextFlags flags2,gfxMissingFontRecorder*){
  auto*r=new nsTransformedTextRun;r->SetLength(n);r->shapeFlags=flags;r->flags=uint16_t(flags2);r->userData=p->data;r->skip=std::move(*p->skip);
  for(size_t i=0;i<n;i++)if(text[i]==32)r->glyphs[i].mValue|=gfxTextRun::CompressedGlyph::FLAG_CHAR_IS_SPACE;
  return r;
 }
};
inline gfxFontGroup*GetFontGroupForFrame(nsTextFrame*,float){static gfxFontGroup f;return &f;}
inline gfxFontGroup*GetInflatedFontGroupForFrame(nsTextFrame*f){return GetFontGroupForFrame(f,1);}
namespace nsLayoutUtils{
inline float FontSizeInflationFor(nsTextFrame*){return 1;}
inline gfx::ShapedTextFlags GetTextRunFlagsForStyle(ComputedStyle*,nsPresContext*,const nsStyleFont*,const nsStyleText*,nscoord){return {};}
}
inline nscoord ResolveLetterSpacing(nsTextFrame*,const nsStyleText&){return 0;}
inline bool NeedsToMaskPassword(nsTextFrame*){return false;}
struct nsTransformingTextRunFactory{
 virtual~nsTransformingTextRunFactory()=default;
 template<class C>gfxTextRun*MakeTextRun(const C*text,uint32_t n,gfxTextRunFactory::Parameters*p,gfxFontGroup*font,gfx::ShapedTextFlags flags,TextFlags flags2,nsTArray<RefPtr<nsTransformedCharStyle>>styles,bool){
  assert(styles.Length()==n);return font->MakeTextRun(text,n,p,flags,flags2,nullptr);
 }
};
struct nsCaseTransformTextRunFactory:nsTransformingTextRunFactory{nsCaseTransformTextRunFactory(std::unique_ptr<nsTransformingTextRunFactory>,bool,bool,char16_t){}};
enum class MathMLPresentationFlag{Dtls};
struct MathFlags{bool contains(MathMLPresentationFlag)const{return false;}};
struct nsPresentationData{MathFlags flags;};
struct nsIMathMLFrame{void GetPresentationData(nsPresentationData&){}uint8_t ScriptIncrement(nsIFrame*){return 0;}};
inline nsIMathMLFrame*do_QueryFrame(nsIFrame*){return nullptr;}
struct MathMLTextRunFactory:nsTransformingTextRunFactory{enum{MATH_FONT_FEATURE_DTLS=1};MathMLTextRunFactory(std::unique_ptr<nsTransformingTextRunFactory>,uint32_t,uint8_t,float){}};
