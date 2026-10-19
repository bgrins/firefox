struct ErrorResult { int code=0; bool Failed()const{return code!=0;} void Throw(int c){code=c;event("error:"+std::to_string(c));} };
constexpr int NS_ERROR_OUT_OF_MEMORY=1, NS_ERROR_FAILURE=2, JSPROP_ENUMERATE=1;
struct JSContext {};
struct OffsetDictionary {
 Maybe<std::string> mRangeName;
 Maybe<double> mOffset;
};
struct OffsetUnion {
 bool ranged=false; double percentage=0; OffsetDictionary range;
 double& RawSetAsDouble(){ranged=false;return percentage;}
 OffsetDictionary& RawSetAsTimelineRangeOffset(){ranged=true;return range;}
};
struct NullableOffset {
 Maybe<OffsetUnion> value;
 OffsetUnion& SetValue(){value.emplace();return *value;}
};
struct BaseComputedKeyframe {
 NullableOffset mOffset;
 Maybe<double> mComputedOffset;
 nsAutoCString mEasing="linear";
 CompositeOperationOrAuto mComposite=CompositeOperationOrAuto::Auto;
};
struct JSObject {
 nsTArray<Keyframe> input;
 bool processingError=false;
 BaseComputedKeyframe dictionary;
 std::vector<std::pair<std::string,std::string>> properties;
};
namespace JS {
struct Value { JSObject* object=nullptr; std::string string; JSObject& toObject(){return *object;} };
template<class T> using Handle=T;
template<class T> class Rooted {
 public:
 T value{};
 Rooted(JSContext*){} Rooted(JSContext*,T x):value(x){}
 operator T()const{return value;}
 JSObject& toObject(){return value.toObject();}
};
}
static std::vector<std::unique_ptr<JSObject>> objectArena;
bool ToJSValue(JSContext*,const BaseComputedKeyframe& d,JS::Rooted<JS::Value>* out){
 event("dictionary");if(failure==2)return false;
 objectArena.push_back(std::make_unique<JSObject>());out->value.object=objectArena.back().get();out->value.object->dictionary=d;return true;
}
bool NonVoidUTF8StringToJsval(JSContext*,const nsAutoCString&s,JS::Rooted<JS::Value>*out){event("js-string");if(failure==3)return false;out->value.string=s;return true;}
bool JS_DefineProperty(JSContext*,JS::Rooted<JSObject*>obj,const char*name,JS::Rooted<JS::Value>value,int){event("define:"+std::string(name));if(failure==4)return false;obj.value->properties.emplace_back(name,value.value.string);return true;}
namespace StaticPrefs { bool layout_css_typed_om_enabled(){return true;} }
struct StyleNumericType {static int Percent(){return 0;}};
double MakeCSSUnitValue(void*,int,double value,nsAutoCString){event("percent-unit");return value;}
void Servo_SerializeTimelineRangeName(StyleTimelineRangeName r,nsAutoCString*out){event("range-name");out->Append(std::to_string(int(r)));}
void Servo_DeclarationBlock_SerializeOneValue(RefPtr<StyleLockedDeclarationBlock>d,const CSSPropertyId*,nsAutoCString*out,RefPtr<const ComputedStyle>,const StylePerDocumentStyleData*){event("serialize:"+std::to_string(d->allocation));out->Append(numeric(d->value));}
void Servo_AnimationValue_Serialize(const double*v,const CSSPropertyId*,const StylePerDocumentStyleData*,nsAutoCString*out){event("serialize-base");out->Append(numeric(*v));}
struct ProviderStyleSet { StylePerDocumentStyleData raw; const StylePerDocumentStyleData* RawData(){event("style-data");return &raw;} };
struct ProviderDocument { ProviderStyleSet styles; ProviderStyleSet& EnsureStyleSet(){return styles;} };
using StyleAnimationValue=double;
struct BaseValueStore {
 std::map<CSSPropertyId,double> values;
 const double* GetWeak(CSSPropertyId p)const{auto it=values.find(p);return it==values.end()?nullptr:&it->second;}
 const double* Get(CSSPropertyId p)const{return GetWeak(p);}
 void Clear(){values.clear();}
 void InsertOrUpdate(CSSPropertyId p,RefPtr<StyleAnimationValue> v){values[p]=*static_cast<double*>(v);}
 struct Iterator {
  using Inner=std::map<CSSPropertyId,double>::const_iterator; Inner at;
  struct Entry {Inner at;const double* GetData()const{return &at->second;} CSSPropertyId GetKey()const{return at->first;}};
  Entry operator*()const{return {at};} Iterator& operator++(){++at;return *this;} bool operator==(const Iterator&)const=default;
 };
 Iterator cbegin()const{return {values.cbegin()};} Iterator cend()const{return {values.cend()};}
};
using BaseValuesHashmap=BaseValueStore;
struct PropertyValue {CSSPropertyId mProperty;AnimationValue mValue;};
using ComputedKeyframeValues=nsTArray<PropertyValue>;
struct ProviderBaseStyleSet {nsTArray<ComputedKeyframeValues> GetComputedKeyframeValuesFor(const nsTArray<Keyframe>&,Element*,const PseudoStyleRequest&,const ComputedStyle*);const ComputedStyle* GetBaseContextForElement(Element*,const ComputedStyle*s){event("base-context");return s;}};
struct nsPresContext {ProviderBaseStyleSet styles;ProviderBaseStyleSet* StyleSet(){return &styles;}};
namespace nsContentUtils {nsPresContext* GetContextForContent(Element*){static nsPresContext c;event("pres-context");return &c;}}
struct BaseValueResult {double value;RefPtr<StyleAnimationValue> Consume(){static std::vector<std::unique_ptr<double>> values;values.push_back(std::make_unique<double>(value));return values.back().get();}};
BaseValueResult Servo_ComputedValues_ExtractAnimationValue(RefPtr<const ComputedStyle>s,const CSSPropertyId*p){event("base-value:"+std::to_string(int(p->mId)));return {s->base};}
struct TimeDuration {double value=0;bool operator>(const TimeDuration&b)const{return value>b.value;}};
struct TimingParams {double delay=0,endDelay=0;TimeDuration Delay()const{return {delay};}TimeDuration EndDelay()const{return {endDelay};}};
namespace mozilla {
class KeyframeUtils {
 public:
 static nsTArray<Keyframe> GetKeyframesFromObject(JSContext*,ProviderDocument*,JSObject*in,const char*,ErrorResult&rv){event("process");if(in->processingError){rv.Throw(3);return {};}return in->input.Clone();}
 static double GetComputedOffset(const Keyframe::OffsetType&,const AnimationTimeline*,const AnimationRange*);
 static KeyframeOffsetsHasRangeOffset ComputeMissingKeyframeOffsets(nsTArray<Keyframe>&,const AnimationTimeline*,const AnimationRange*);
 static nsTArray<AnimationProperty> GetAnimationPropertiesFromKeyframes(const nsTArray<Keyframe>&,Element*,const PseudoStyleRequest&,const ComputedStyle*,CompositeOperation,const AnimationTimeline*);
};
}
 nsTArray<ComputedKeyframeValues> ProviderBaseStyleSet::GetComputedKeyframeValuesFor(const nsTArray<Keyframe>&frames,Element*,const PseudoStyleRequest&,const ComputedStyle*style){
  nsTArray<ComputedKeyframeValues> out;if(style->valuesFail)return out;
  for(const auto&f:frames){auto*row=out.AppendElement();for(const auto&p:f.mPropertyValues){
   event("computed-value:"+std::to_string(int(p.mProperty.mId))+":"+std::to_string(p.mServoDeclarationBlock?p.mServoDeclarationBlock->allocation:-1));
   PropertyValue item;item.mProperty=p.mProperty;if(p.mServoDeclarationBlock)item.mValue.value.emplace(p.mServoDeclarationBlock->value*style->scale);row->AppendElement(item);
  }}return out;
 }
namespace mozilla {
namespace dom {
namespace EffectCompositor { enum class RestyleType { Layer }; }
enum class Flush { None,Style };
class KeyframeEffect {
 public:
 nsTArray<Keyframe> mKeyframes;
 KeyframeOffsetsHasRangeOffset mKeyframeOffsetsHasRangeOffset=KeyframeOffsetsHasRangeOffset::No;
 nsTArray<AnimationProperty> mProperties;
 BaseValueStore mBaseValues;
 struct Target {Element* mElement=nullptr;PseudoStyleRequest mPseudoRequest;operator bool()const{return mElement!=nullptr;}} mTarget;
 struct Options {CompositeOperation mComposite=CompositeOperation::Replace;} mEffectOptions;
 Animation* mAnimation=nullptr;
 ProviderDocument* mDocument=nullptr;
 const ComputedStyle* providerStyle=nullptr;
 int mCumulativeChanges=0;
 RefPtr<const ComputedStyle> GetTargetComputedStyle(Flush f){event(f==Flush::None?"target-style":"target-style-flush");return mTarget?providerStyle:nullptr;}
 void* GetParentObject(){return nullptr;}
 /*GET_COMPUTED*/
 TimingParams providerTiming;
 const TimingParams& NormalizedTiming()const{return providerTiming;}
 void EnsureBaseStyle(const AnimationProperty&,nsPresContext*,const ComputedStyle*,const AnimationTimeline*,RefPtr<const ComputedStyle>&);
 void EnsureBaseStyles(const ComputedStyle*,const nsTArray<AnimationProperty>&,const AnimationTimeline*,bool*);
 void UpdateEffectSet(){event("effect-set");}
 void CalculateCumulativeChangesForProperty(AnimationProperty&p){event("cumulative:"+std::to_string(int(p.mProperty.mId)));++mCumulativeChanges;}
 void MarkCascadeNeedsUpdate(){event("cascade-dirty");}
 void RequestRestyle(EffectCompositor::RestyleType){event("restyle");}
 void SetKeyframes(JSContext*,JS::Handle<JSObject*>,ErrorResult&);
 void SetKeyframes(nsTArray<Keyframe>&&,const ComputedStyle*,const AnimationTimeline*,const AnimationRange*);
 nsTArray<AnimationProperty> BuildProperties(const ComputedStyle*,const AnimationTimeline*);
 void UpdateProperties(const ComputedStyle*,const AnimationTimeline* = nullptr);
 void MaybeUpdateKeyframeComputedOffsets(const AnimationTimeline*,const AnimationRange&);
 void SetComposite(const CompositeOperation&);
 void GetKeyframes(JSContext*,nsTArray<JSObject*>&,ErrorResult&);
};
}
}
