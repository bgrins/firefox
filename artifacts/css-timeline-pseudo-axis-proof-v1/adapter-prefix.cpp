#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <memory>
#include <optional>
#include <string>
#include <utility>
#include <vector>
#define MOZ_ASSERT(x, ...) assert(x)
#define MOZ_ASSERT_UNREACHABLE(x) assert(false)
#define PROGRESS_TIMELINE_DURATION_MILLISEC 100000
using nscoord = int32_t;
template<class T> using RefPtr = T*;
template<class T> using already_AddRefed = T*;
template<class T> struct Maybe : std::optional<T> {
  using std::optional<T>::optional;
  using std::optional<T>::operator=;
  Maybe() = default;
  Maybe(const Maybe&) = default;
  Maybe& operator=(const Maybe&) = default;
  Maybe(Maybe&& other) : std::optional<T>(std::move(other)) { other.reset(); }
  Maybe& operator=(Maybe&& other) { std::optional<T>::operator=(std::move(other)); other.reset(); return *this; }
  bool isSome() const { return this->has_value(); }
  T valueOr(T x) const { return this->value_or(x); }
  bool operator==(const Maybe& other) const { return static_cast<const std::optional<T>&>(*this) == static_cast<const std::optional<T>&>(other); }
};
template<class T> Maybe<T> Some(T x) { return Maybe<T>(std::move(x)); }
std::nullopt_t Nothing() { return std::nullopt; }
template<class T> struct Nullable {
  std::optional<T> value;
  Nullable() = default;
  Nullable(std::nullptr_t) {}
  Nullable(T v) : value(v) {}
  void SetNull() { value.reset(); }
  T& SetValue() { return value.emplace(); }
};
struct nsPoint { nscoord x=0,y=0; };
struct nsRect { nscoord x=0,y=0,width=0,height=0; };
enum class StyleScrollAxis : uint8_t { Block, Inline, X, Y };
enum class StyleScroller : uint8_t { Root, Nearest, SelfElement };
enum class StyleOverflow : uint8_t { Visible, Hidden, Scroll, Auto, Clip };
namespace layers { enum class ScrollDirection : uint8_t { eHorizontal, eVertical }; }
struct WritingMode { bool vertical=false; bool reversed=false; bool IsVertical() const { return vertical; } };
struct ScrollStyles { StyleOverflow mHorizontal{},mVertical{}; };
std::vector<std::array<int64_t,4>> events;
void record(int id,int op,int arg,int64_t result) { events.push_back({id,op,arg,result}); }
enum class PseudoStyleType { NotPseudo, Before, After, Marker, Backdrop, Checkmark, PickerIcon, Transition };
struct nsAtom { int id=0; };
struct PseudoStyleRequest {
  PseudoStyleType type{}; nsAtom* name=nullptr;
  PseudoStyleRequest() = default;
  explicit PseudoStyleRequest(PseudoStyleType t,nsAtom* n=nullptr):type(t),name(n){}
  static PseudoStyleRequest NotPseudo(){return {};}
  static PseudoStyleRequest Before(){return PseudoStyleRequest(PseudoStyleType::Before);}
  static PseudoStyleRequest After(){return PseudoStyleRequest(PseudoStyleType::After);}
  static PseudoStyleRequest Marker(){return PseudoStyleRequest(PseudoStyleType::Marker);}
  static PseudoStyleRequest Backdrop(){return PseudoStyleRequest(PseudoStyleType::Backdrop);}
  bool operator==(const PseudoStyleRequest&) const=default;
};
namespace PseudoStyle { bool IsViewTransitionPseudoElement(PseudoStyleType t){return t==PseudoStyleType::Transition;} }
namespace nsGkAtoms { int name=0; }
class Element; class Document; class ScrollContainerFrame; class ScrollTimeline; class ViewTimeline;
struct PresShell { int id=2001; ScrollContainerFrame* root=nullptr; ScrollContainerFrame* GetRootScrollContainerFrame() const; };
struct nsIFrame {
 int id=0; nsIFrame* parent=nullptr; Element* content=nullptr;
 ScrollContainerFrame* target=nullptr; ::PresShell* shell=nullptr;
 bool scroll=false; WritingMode mode;
 nsIFrame* GetParent() const {record(id,3,0,parent?parent->id:0);return parent;}
 Element* GetContent() const;
 bool IsScrollContainerFrame() const {record(id,4,0,scroll);return scroll;}
 ScrollContainerFrame* GetScrollTargetFrame() const;
 ::PresShell* PresShell() const {record(id,9,0,shell?shell->id:0);return shell;}
 WritingMode GetWritingMode() const {record(id,5,mode.reversed,mode.vertical);return mode;}
 virtual ~nsIFrame()=default;
};
struct DirectionSet { int bits; bool contains(layers::ScrollDirection d) const { return bits & (1<<int(d)); } };
class ScrollContainerFrame : public nsIFrame { public:
 int available=0; nsPoint position; nsRect range; ScrollStyles styles;
 DirectionSet GetAvailableScrollingDirections() const {record(id,6,0,available);return {available};}
 ScrollStyles GetScrollStyles() const {record(id,7,int(styles.mHorizontal),int(styles.mVertical));return styles;}
 const nsPoint& GetScrollPosition() const {record(id,8,position.x,position.y);return position;}
 const nsRect& GetScrollRange() const {record(id,10,range.width,range.height);return range;}
};
struct TimelinesController { template<class T> void AddScrollTimeline(T&) {} };
struct ScopeObject { int GetRTPCallerType() const {return 0;} };
class Document { public:
 int id=2000; Element* root=nullptr; Element* scrolling=nullptr; PresShell* shell=nullptr;
 ::TimelinesController controller; ScopeObject scope;
 Element* GetScrollingElementNoFlush() const;
 Element* GetRootElement() const;
 PresShell* GetPresShell() const {record(id,11,0,shell?shell->id:0);return shell;}
 int GetParentObject()const{return 0;} ScopeObject* GetScopeObject(){return &scope;}
 ::TimelinesController& TimelinesController(){return controller;}
};
struct Attr { nsAtom atom; nsAtom* GetAtomValue(){return &atom;} };
class Element { public:
 int id=0; bool isElement=true; int kind=0; Element* parent=nullptr;
 Document* doc=nullptr; nsIFrame* primary=nullptr; std::array<Element*,8> pseudos{};
 bool apzDisabled=false,displayport=false; Attr attr; bool hasName=false;
 nsIFrame* GetPrimaryFrame() const {record(id,1,0,primary?primary->id:0);return primary;}
 Document* OwnerDoc() const {record(id,12,0,doc?doc->id:0);return doc;}
 Document* GetOwnerDocument() const {return OwnerDoc();}
 Element* GetPseudoElement(PseudoStyleRequest p) const {
   Element* e=int(p.type)==0?const_cast<Element*>(this):pseudos[int(p.type)];
   record(id,2,int(p.type),e?e->id:0);return e;
 }
 bool IsElement()const {record(id,13,0,isElement);return isElement;}
 Element* AsElement(){assert(isElement);return this;}
 const Element* AsElement()const{assert(isElement);return this;}
 Element* GetParent()const{record(id,14,0,parent?parent->id:0);return parent;}
 bool IsGeneratedContentContainerForBefore()const{return kind==1;}
 bool IsGeneratedContentContainerForAfter()const{return kind==2;}
 bool IsGeneratedContentContainerForMarker()const{return kind==3;}
 bool IsGeneratedContentContainerForBackdrop()const{return kind==4;}
 bool IsGeneratedContentContainerForCheckmark()const{return kind==5;}
 bool IsGeneratedContentContainerForPickerIcon()const{return kind==6;}
 PseudoStyleType GetPseudoElementType()const{return PseudoStyleType(kind);}
 bool HasName()const{return hasName;}
 Attr* GetParsedAttr(int)const{return const_cast<Attr*>(&attr);}
};
using nsIContent=Element;
Element* nsIFrame::GetContent()const{record(id,15,0,content?content->id:0);return content;}
ScrollContainerFrame* nsIFrame::GetScrollTargetFrame()const{record(id,16,0,target?target->id:0);return target;}
ScrollContainerFrame* PresShell::GetRootScrollContainerFrame()const{record(id,17,0,root?root->id:0);return root;}
Element* Document::GetScrollingElementNoFlush()const{record(id,18,0,scrolling?scrolling->id:0);return scrolling;}
Element* Document::GetRootElement()const{record(id,19,0,root?root->id:0);return root;}
struct OwningAnimationTarget {
 Element* mElement=nullptr; PseudoStyleRequest mPseudoRequest;
 OwningAnimationTarget()=default;
 OwningAnimationTarget(Element* e,PseudoStyleRequest p):mElement(e),mPseudoRequest(p){}
 explicit operator bool()const{return mElement!=nullptr;}
};
struct NonOwningAnimationTarget:OwningAnimationTarget{
 using OwningAnimationTarget::OwningAnimationTarget;
 NonOwningAnimationTarget(const OwningAnimationTarget& x):OwningAnimationTarget(x){}
};
namespace AnimationUtils { std::pair<const Element*,PseudoStyleRequest> GetElementPseudoPair(const Element*); }
namespace nsLayoutUtils {
 nsIFrame* GetScrollContainerFrameFromContent(nsIContent*);
 ScrollContainerFrame* FindScrollContainerFrameFor(nsIContent*);
 bool ShouldDisableApzForElement(Element* e){record(e->id,20,0,e->apzDisabled);return e->apzDisabled;}
}
namespace gfxPlatform { bool enabled=false; bool AsyncPanZoomEnabled(){record(0,21,0,enabled);return enabled;} }
namespace DisplayPortUtils { bool HasNonMinimalNonZeroDisplayPort(Element* e){record(e->id,22,0,e->displayport);return e->displayport;} }
namespace StaticPrefs { bool typed=false; bool layout_css_typed_om_enabled(){return typed;} }
struct TimeDuration {double value;static TimeDuration FromMilliseconds(double x){return {x};}};
struct CSSNumericValue {double value=0;};
struct OwningCSSNumberish { CSSNumericValue* css=nullptr; double duration=0; CSSNumericValue*& SetAsCSSNumericValue(){return css;} };
struct StyleNumericType {static int Percent(){return 0;}};
std::string operator""_ns(const char* s,size_t n){return std::string(s,n);}
std::vector<std::unique_ptr<CSSNumericValue>> numericValues;
CSSNumericValue* MakeCSSUnitValue(int,int,double x,std::string){numericValues.push_back(std::make_unique<CSSNumericValue>());numericValues.back()->value=x;return numericValues.back().get();}
class AnimationTimeline { public:
 int mWindow=0;
 AnimationTimeline(int,int){}
 virtual ~AnimationTimeline()=default;
 virtual Nullable<TimeDuration> GetCurrentTimeAsDuration() const=0;
 void GetCurrentTime(Nullable<OwningCSSNumberish>& out)const{
   auto value=GetCurrentTimeAsDuration();if(!value.value){out.SetNull();return;}
   out.SetValue().duration=value.value->value;
 }
};
class Animation;
template<class T> struct LinkedListElement { T* next=nullptr; T* getNext() const{return next;} };
class Animation: public LinkedListElement<Animation> { public:
 int id=0;
 void UpdateNormalizedTimingForTimelineDataChange(){record(id,23,0,0);}
 void MaybeUpdateKeyframeComputedOffsets(){record(id,24,0,0);}
};
struct AnimationOrder {Animation* first=nullptr;Animation* getFirst()const{return first;}};
bool NS_IsMainThread(){return true;}
template<class T,class... Args> T* MakeAndAddRef(Args&&... args){return new T(std::forward<Args>(args)...);}
