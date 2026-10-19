#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <memory>
#include <span>
#include <sstream>
#include <string>
#include <vector>
#include <variant>
#include <type_traits>
using nsresult = int;
constexpr int NS_OK=0, NS_ERROR_OUT_OF_MEMORY=1;
#define NS_FAILED(x) ((x)!=0)
#define NS_SUCCEEDED(x) ((x)==0)
#define NS_ASSERTION(x,m) assert(x)
#define MOZ_ASSERT(x,...) assert(x)
#define NS_WARNING(x) ((void)0)
#define MOZ_ASSERT_UNREACHABLE(x) assert(false)
static int gFailAt=-1, gAllocations=0;
static bool allocationFails(){return gFailAt>=0 && gAllocations++==gFailAt;}
namespace mozilla {
struct Fallible{}; inline constexpr Fallible fallible{};
template<class T> using Span=std::span<T>;
template<class T> class AutoRestore { T& ref;T old;public:explicit AutoRestore(T& x):ref(x),old(x){} ~AutoRestore(){ref=old;} };
template<class F> struct ScopeExit{F f;~ScopeExit(){f();}};
template<class F> auto MakeScopeExit(F f){return ScopeExit<F>{f};}
inline bool IsHighSurrogate(uint32_t c){return c>=0xd800&&c<=0xdbff;}
inline bool IsLowSurrogate(uint32_t c){return c>=0xdc00&&c<=0xdfff;}
inline bool IsSurrogatePair(uint32_t a,uint32_t b){return IsHighSurrogate(a)&&IsLowSurrogate(b);}
inline uint32_t SurrogateToUCS4(uint32_t a,uint32_t b){return 0x10000+((a-0xd800)<<10)+(b-0xdc00);}
inline bool IsInBMP(uint32_t c){return c<=0xffff;}
}
template<class T> class nsTArray {
  T* p=nullptr;size_t n=0,cap=0;
  bool grow(size_t size,bool fallible){
    if(fallible&&allocationFails())return false;
    if(size>cap){size_t c=std::max(size,cap*2+8);auto q=static_cast<T*>(::operator new(sizeof(T)*c));for(size_t i=0;i<n;i++){new(q+i)T(std::move(p[i]));p[i].~T();}::operator delete(p);p=q;cap=c;}return true;
  }
 public:
  nsTArray(){grow(8,false);}
  nsTArray(nsTArray&& other)noexcept:p(std::exchange(other.p,nullptr)),n(std::exchange(other.n,0)),cap(std::exchange(other.cap,0)){}
  nsTArray&operator=(nsTArray&&other)noexcept{if(this!=&other){Clear();::operator delete(p);p=std::exchange(other.p,nullptr);n=std::exchange(other.n,0);cap=std::exchange(other.cap,0);}return *this;}
  ~nsTArray(){Clear();::operator delete(p);}
  size_t Length()const{return n;}bool IsEmpty()const{return !n;}
  T* Elements(){return p;}const T* Elements()const{return p;}
  T* data(){return p;}const T* data()const{return p;}
  size_t size()const{return n;}
  T* begin(){return p;}T* end(){return p+n;}
  const T* begin()const{return p;}const T* end()const{return p+n;}
  T& operator[](size_t i){assert(i<n);return p[i];}const T& operator[](size_t i)const{assert(i<n);return p[i];}
  void Clear(){while(n)p[--n].~T();}
  T* AppendElements(size_t count,mozilla::Fallible){if(!grow(n+count,true))return nullptr;T* r=p+n;for(size_t i=0;i<count;i++)new(p+n++)T{};return r;}
  T* AppendElement(T x){grow(n+1,false);new(p+n)T(std::move(x));return p+n++;}
  bool SetLength(size_t count,mozilla::Fallible){if(!grow(count,true))return false;while(n>count)p[--n].~T();while(n<count)new(p+n++)T{};return true;}
  void SetLength(size_t count){grow(count,false);while(n>count)p[--n].~T();while(n<count)new(p+n++)T{};}
  T PopLastElement(){assert(n);T value=std::move(p[--n]);p[n].~T();return value;}
  operator std::span<const T>()const{return {p,n};}
  operator std::span<T>(){return {p,n};}
};
template<class T,size_t N> using AutoTArray=nsTArray<T>;
template<class T> class RefPtr{T* p=nullptr;public:RefPtr()=default;RefPtr(T* x):p(x){}operator T*()const{return p;}T* operator->()const{return p;}T* get()const{return p;}RefPtr& operator=(T*x){p=x;return *this;}};
namespace mozilla { template<class T>using StaticRefPtr=RefPtr<T>;template<class T>void ClearOnShutdown(T*){} }
struct nsAtom{std::string value;};
inline std::string nsAtomCString(nsAtom* p){return p->value;}
struct nsAtomString{nsAtom*atom;explicit nsAtomString(nsAtom*p):atom(p){}bool Equals(nsAtomString b)const{return atom->value==b.atom->value;}};
struct nsAString{
  std::u16string s;nsAString()=default;nsAString(const char16_t*a,const char16_t*b):s(a,b){}
  size_t Length()const{return s.size();}const char16_t* BeginReading()const{return s.data();}const char16_t* get()const{return s.data();}char16_t operator[](size_t i)const{return s.at(i);}
};
using nsAutoString=nsAString;using nsDependentSubstring=nsAString;
struct nsDependentCSubstring{const char*a,*b;nsDependentCSubstring(const char*x,const char*y):a(x),b(y){}};
inline void CopyASCIItoUTF16(nsDependentCSubstring a,nsAutoString& out){for(auto p=a.a;p<a.b;p++)out.s.push_back(uint8_t(*p));}
struct nsAutoCString{std::string s;void Append(uint32_t c){s.push_back(char(c));}size_t Length()const{return s.size();}const char* BeginReading()const{return s.data();}uint8_t operator[](size_t i)const{return uint8_t(s.at(i));}};
extern "C" int8_t u_charType(int32_t);
extern "C" int32_t u_tolower(int32_t);
extern "C" int32_t uloc_addLikelySubtags(const char*,char*,int32_t,int32_t*);
extern "C" int32_t uloc_getScript(const char*,char*,int32_t,int32_t*);

#include "provider/unicode-native.h"
namespace mozilla::intl {
inline bool NS_IsSpace(char16_t c){return c==32||c==9||c==10||c==13;}
enum class WordBreakRule{Normal,BreakAll,KeepAll};
enum class LineBreakRule{Auto,Normal,Loose,Strict,Anywhere};
struct Result{bool bad=false;bool isErr()const{return bad;}};
struct ScriptTag{std::string s;bool Missing()const{return s.empty();}bool EqualTo(const char*x)const{return s==x;}};
struct Locale{
 std::string language;ScriptTag script;
 ScriptTag& Script(){return script;}
 Result AddLikelySubtags(){char full[256],s[32];int32_t err=0;uloc_addLikelySubtags(language.c_str(),full,256,&err);uloc_getScript(full,s,32,&err);if(err>0)return {true};script.s=s;return {};}
};
struct LocaleParser{static Result TryParse(const std::string&s,Locale&out){out.language=s;return {};}};
struct LineBreaker{
 static void ComputeBreakPositions(const nsTArray<char16_t>& text,WordBreakRule w,LineBreakRule l,bool cj,nsTArray<uint8_t>& out){ComputeBreakPositions(std::span<const char16_t>(text.Elements(),text.Length()),w,l,cj,std::span<uint8_t>(out.Elements(),out.Length()));}
 template<class T>static void ComputeBreakPositions(std::span<const T> text,WordBreakRule w,LineBreakRule l,bool,std::span<uint8_t> out){assert(text.size()==out.size());for(size_t i=0;i<text.size();i++)out[i]=(i&&(w==WordBreakRule::BreakAll||l==LineBreakRule::Anywhere))?1:0;}
};
}
#include "../native/range-types.hpp"
extern "C" int32_t mapped_hyph_find_hyphen_values_raw(const uint8_t*,uint32_t,const char*,uint32_t,uint8_t*,uint32_t);
extern "C" int32_t mapped_hyph_find_hyphen_values_dic(const void*,const char*,uint32_t,uint8_t*,uint32_t);
extern "C" bool mapped_hyph_is_valid_hyphenator(const uint8_t*,uint32_t);
struct HyphDic{};
template<class T>using UniquePtr=std::unique_ptr<T>;
template<class T,class...Args>auto MakeUnique(Args&&...args){return std::make_unique<T>(std::forward<Args>(args)...);}
namespace ipc{struct ReadOnlySharedMemoryHandle{};struct ReadOnlySharedMemoryMapping{template<class T>const T*DataAs(){return nullptr;}size_t Size(){return 0;}};}
struct Dictionary{
 std::vector<uint8_t> bytes;
 template<class A,class B,class C,class D>int match(A a,B,C,D){std::span<const uint8_t> s(bytes);return a(s);}
};
class nsHyphenator{
 public:Dictionary mDict;bool mHyphenateCapitalized=false;
 nsresult Hyphenate(const nsAString&,nsTArray<bool>&);
 void HyphenateWord(const nsAString&,uint32_t,uint32_t,nsTArray<bool>&);
};
static nsHyphenator gHyphenator;
class nsHyphenationManager{
 public:static nsHyphenationManager*Instance(){static nsHyphenationManager m;return &m;}
 nsHyphenator*GetHyphenator(nsAtom*a){return a&&(a->value=="en"||a->value=="en-US")?&gHyphenator:nullptr;}
};

using mozilla::Span;using mozilla::fallible;
