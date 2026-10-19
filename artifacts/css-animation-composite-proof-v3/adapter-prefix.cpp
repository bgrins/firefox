#include <algorithm>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <sstream>
#include <string>
#include <utility>
#include <vector>
#define MOZ_ASSERT(x, ...) assert(x)
struct nsAutoCString : std::string {
  using std::string::string;
  void Truncate() { clear(); }
  void Append(const std::string& s) { append(s); }
  const char* get() const { return c_str(); }
};
using nsCString = nsAutoCString;
nsAutoCString operator""_ns(const char* s, size_t n) { return {s,n}; }
static std::vector<std::string> trace;
static void event(std::string s) { trace.push_back(s); }
static int failure = 0;
static std::string numeric(double x) {
  if (std::isnan(x)) return "null";
  std::ostringstream out; out << std::setprecision(17) << x; return out.str();
}
static std::string quoted(const std::string& x) { std::ostringstream o; o << std::quoted(x); return o.str(); }
namespace mozilla {
constexpr int fallible = 0;
template<class T> class Maybe : public std::optional<T> {
 public:
  using std::optional<T>::optional;
  T& ref() { return this->value(); }
  const T& ref() const { return this->value(); }
  bool isNothing() const { return !this->has_value(); }
  template<class U> void Construct(U&& u) { this->emplace(std::forward<U>(u)); }
  bool operator==(const Maybe& b) const { return static_cast<const std::optional<T>&>(*this)==static_cast<const std::optional<T>&>(b); }
};
template<class T> class RefPtr {
  T* value = nullptr;
 public:
  RefPtr() = default;
  RefPtr(T* v): value(v) {}
  T* operator->() const { return value; }
  operator T*() const { return value; }
  bool operator==(const RefPtr&) const = default;
};
template<class T> class nsTArray : public std::vector<T> {
 public:
  nsTArray() = default;
  explicit nsTArray(size_t n) { this->reserve(n); }
  size_t Length() const { return this->size(); }
  bool IsEmpty() const { return this->empty(); }
  bool SetCapacity(size_t n, int) { if(failure==1) return false; this->reserve(n); return true; }
  T* AppendElement() { this->emplace_back(); return &this->back(); }
  template<class U> T* AppendElement(U&& x) { this->push_back(std::forward<U>(x)); return &this->back(); }
  T& LastElement() { return this->back(); }
  T* Elements() { return this->data(); }
  nsTArray Clone() const { return *this; }
  bool operator==(const nsTArray& b) const { return static_cast<const std::vector<T>&>(*this)==static_cast<const std::vector<T>&>(b); }
};
template<class T> using CopyableTArray=nsTArray<T>;
template<class T> class RangedPtr {
  T* p;
 public:
  RangedPtr(T* q,size_t):p(q){} RangedPtr(T* q):p(q){}
  T& operator*()const{return *p;} RangedPtr operator+(size_t n)const{return {p+n};}
  RangedPtr operator-(size_t n)const{return {p-n};}
  ptrdiff_t operator-(RangedPtr q)const{return p-q.p;}
  RangedPtr& operator++(){++p;return *this;} bool operator==(const RangedPtr&)const=default;
  T* raw()const{return p;}
};
template<class T> class Range {
  RangedPtr<T> first,last;
 public:
  Range(RangedPtr<T> a,RangedPtr<T> b):first(a),last(b){}
  RangedPtr<T> begin()const{return first;} RangedPtr<T> end()const{return last;}
  size_t length()const{return last-first;} T& operator[](size_t i)const{return *(first+i);}
};
enum class NonCustomCSSPropertyId { eCSSProperty_UNKNOWN=-1, opacity=0, eCSSProperty_float=1, eCSSProperty_offset=2, width=3, eCSSPropertyExtra_variable=4 };
constexpr auto eCSSProperty_UNKNOWN=NonCustomCSSPropertyId::eCSSProperty_UNKNOWN;
struct CSSPropertyId {
  NonCustomCSSPropertyId mId=eCSSProperty_UNKNOWN;
  std::string mCustomName;
  CSSPropertyId()=default; CSSPropertyId(NonCustomCSSPropertyId x):mId(x){}
  bool IsValid()const{return mId!=eCSSProperty_UNKNOWN;}
  bool operator==(const CSSPropertyId&)const=default;
  bool operator<(const CSSPropertyId& b)const{return std::tie(mId,mCustomName)<std::tie(b.mId,b.mCustomName);}
};
std::string nsDependentAtomString(const std::string& s){return s;}
std::string nsAtomCString(const std::string& s){return s;}
int Compare(const std::string&a,const std::string&b){return a.compare(b);}
namespace nsCSSProps {
const char* PropertyIDLName(NonCustomCSSPropertyId p) {
 static const char* names[]={"opacity","cssFloat","offset","width","custom"};return names[int(p)];
}
int PropertyIDLNameSortPosition(NonCustomCSSPropertyId p){static int order[]={2,0,1,3,4};return order[int(p)];}
}
struct nsCSSPropertyIDSet {
 std::set<NonCustomCSSPropertyId> s;
 void AddProperty(NonCustomCSSPropertyId p){s.insert(p);}
 bool HasProperty(CSSPropertyId p)const{return s.count(p.mId);}
 static nsCSSPropertyIDSet CompositorAnimatables(){nsCSSPropertyIDSet r;r.AddProperty(NonCustomCSSPropertyId::opacity);return r;}
};
enum class StyleTimelineRangeName { None, Normal, Cover, Contain, Entry, Exit, EntryCrossing, ExitCrossing };
struct StyleComputedTimingFunction {
 int value=0; bool operator==(const StyleComputedTimingFunction&)const=default;
 void AppendToString(nsAutoCString& s)const{s.Append(value==0?"linear":value==1?"ease":"steps(2)");}
};
struct StyleLockedDeclarationBlock { int allocation; double value; };
bool Servo_DeclarationBlock_Equals(RefPtr<StyleLockedDeclarationBlock>a,RefPtr<StyleLockedDeclarationBlock>b){event("declaration-equals:"+std::to_string(a->allocation)+":"+std::to_string(b->allocation));return a->value==b->value;}
struct AnimationValue {
 Maybe<double> value;
 AnimationValue()=default; AnimationValue(const double* p){if(p)value.emplace(*p);}
 bool IsNull()const{return !value;}
 bool operator==(const AnimationValue&)const=default;
};
struct ComputedStyle { double base=0; double scale=1; bool valuesFail=false; };
struct AnimationPerformanceWarning {};
struct PseudoStyleRequest {};
struct StylePerDocumentStyleData {};
namespace dom {
enum class CompositeOperation { Replace, Add, Accumulate };
enum class CompositeOperationOrAuto { Replace, Add, Accumulate, Auto };
struct Element { Element* GetPseudoElement(const PseudoStyleRequest&){return this;} };
struct AnimationRange { double first=0,second=1; };
struct ViewTimeline {
 bool resolved=true; double start=0,delta=1;
 Maybe<double> MapKeyframeOffsetToOffset(StyleTimelineRangeName name,double p)const {
  event("timeline-map:"+std::to_string(int(name))+":"+numeric(p));
  if(!resolved) return {};return start+delta*p;
 }
 std::pair<double,double> IntervalForAttachmentRange(const AnimationRange&r)const{event("attachment-range");return {r.first,r.second};}
};
struct AnimationTimeline {
 bool view=false; ViewTimeline geometry;
 bool IsViewTimeline()const{return view;} bool IsScrollTimeline()const{return view;}
 const ViewTimeline* AsViewTimeline()const{return &geometry;}
};
struct Animation {
 bool relevant=false; AnimationTimeline* timeline=nullptr; AnimationRange range;
 bool IsRelevant()const{return relevant;} bool AsCSSAnimation()const{return false;}
 AnimationTimeline* GetTimeline()const{return timeline;} const AnimationRange& GetTimelineRange()const{return range;}
 void NotifyEffectPropertiesUpdated(){event("effect-updated");}
};
}
namespace MutationObservers { void NotifyAnimationChanged(dom::Animation*){event("notify");} }
}
using namespace mozilla;
using namespace mozilla::dom;
