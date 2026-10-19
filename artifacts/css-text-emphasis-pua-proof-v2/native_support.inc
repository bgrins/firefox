#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <numeric>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>
#define MOZ_ASSERT(x, ...) assert(x)
#define NS_ASSERTION(x, ...) assert(x)
#define MOZ_RELEASE_ASSERT(x, ...) assert(x)
#define MOZ_DIAGNOSTIC_ASSERT(x, ...) assert(x)
#define MOZ_STACK_CLASS
#define DEBUG
using nscoord = int32_t;
using gfxFloat = double;
struct Fallible {};
constexpr Fallible fallible;
bool failSpacingAllocation = false;
std::vector<std::string> providerTrace;
std::vector<uint32_t> drawUnits;
namespace mozilla {
using MallocSizeOf = size_t (*)(const void*);
template<class T> using UniquePtr = std::unique_ptr<T>;
template<class T> auto MakeUnique() { return std::make_unique<T>(); }
namespace gfx {
struct Coord { float value=0; Coord()=default; Coord(float v):value(v){} };
struct Point { Coord x,y; Point()=default; Point(float a,float b):x(a),y(b){} };
struct PaletteCache {};
struct ShapedTextFlags { static constexpr uint32_t TEXT_ENABLE_SPACING=1; };
}
namespace image { struct imgDrawingParams {}; }
}
namespace gfx = mozilla::gfx;
using imgDrawingParams = mozilla::image::imgDrawingParams;
struct gfxContext {};
template<class T> class nsTArray {
  std::vector<T> data;
 public:
  using index_type=size_t;
  static constexpr index_type NoIndex=size_t(-1);
  size_t Length() const { return data.size(); }
  bool IsEmpty() const { return data.empty(); }
  T* Elements() { return data.data(); }
  const T* Elements() const { return data.data(); }
  T* begin() { return data.data(); }
  const T* begin() const { return data.data(); }
  T* end() { return data.data()+data.size(); }
  const T* end() const { return data.data()+data.size(); }
  T& operator[](size_t i) { return data.at(i); }
  const T& operator[](size_t i) const { return data.at(i); }
  T* AppendElements(size_t n) {
    auto old=data.size(); data.resize(old+n);
    providerTrace.push_back("allocate:"+std::to_string(old)+":"+std::to_string(n));
    return data.data()+old;
  }
  T* AppendElements(size_t n,Fallible) {
    if(failSpacingAllocation) { providerTrace.push_back("spacing-allocation-failed"); return nullptr; }
    return AppendElements(n);
  }
  void AppendElement(const T& t) { data.push_back(t); }
  void Clear() { data.clear(); }
  template<class C> void InsertElementSorted(const T& t,C cmp) {
    auto i=std::lower_bound(data.begin(),data.end(),t,[&](auto& a,auto& b){return cmp.LessThan(a,b);});
    data.insert(i,t);
  }
  template<class V,class C> size_t BinaryIndexOf(const V& v,C cmp) const {
    auto i=std::lower_bound(data.begin(),data.end(),v,[&](auto& a,auto& b){return cmp.LessThan(a,b);});
    return i!=data.end() && cmp.Equals(*i,v) ? i-data.begin() : NoIndex;
  }
  size_t ShallowSizeOfExcludingThis(mozilla::MallocSizeOf) const { return 0; }
};
template<class T,size_t N> using AutoTArray=nsTArray<T>;
struct nsLiteralString {
  std::u16string_view text;
  constexpr nsLiteralString(const char16_t* p,size_t n):text(p,n){}
  constexpr bool Contains(char16_t c) const { return text.find(c)!=text.npos; }
};
constexpr nsLiteralString operator""_ns(const char16_t* p,size_t n) { return {p,n}; }
auto IntegerRange(uint32_t n) { return std::views::iota(uint32_t(0),n); }

static_assert(sizeof(float)==4 && std::numeric_limits<float>::is_iec559 && std::numeric_limits<float>::digits==24 && std::numeric_limits<float>::max_exponent==128);
static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559 && std::numeric_limits<double>::digits==53 && std::numeric_limits<double>::max_exponent==1024);
static_assert(sizeof(int32_t)==4 && sizeof(uint32_t)==4 && sizeof(int64_t)==8);
