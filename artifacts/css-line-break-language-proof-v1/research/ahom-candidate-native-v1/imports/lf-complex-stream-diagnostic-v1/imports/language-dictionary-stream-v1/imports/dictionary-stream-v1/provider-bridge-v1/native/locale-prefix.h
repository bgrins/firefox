#pragma once
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <type_traits>
#include <variant>
#include <vector>
#define U_DISABLE_RENAMING 1
#include "unicode/uloc.h"
#define MOZ_ASSERT(x, ...) assert(x)
#define MOZ_ALWAYS_TRUE(x) assert(x)
#define MOZ_CRASH(...) abort()
#define MOZ_STACK_CLASS
#define MOZ_TRY(expr) do { auto result_ = (expr); if (result_.isErr()) return mozilla::Err(result_.unwrapErr()); } while (0)
#define MOZ_MAKE_ENUM_CLASS_BITWISE_OPERATORS(T) inline T& operator|=(T& a,T b) { a=T(unsigned(a)|unsigned(b)); return a; }
namespace mozilla {
struct Ok {};
template<class E> struct Error { E value; };
template<class E> Error<E> Err(E e) { return {e}; }
template<class T,class E> struct Result {
  std::variant<T,E> value;
  Result(T t):value(std::move(t)){}
  Result(Error<E> e):value(e.value){}
  bool isErr() const { return value.index()==1; }
  bool isOk() const { return !isErr(); }
  E unwrapErr() const { return std::get<1>(value); }
  template<class F> auto mapErr(F f) const -> Result<T,decltype(f(unwrapErr()))> {
    if (isErr()) return Err(f(unwrapErr()));
    return std::get<0>(value);
  }
};
template<class T> using UniquePtr=std::unique_ptr<T>;
template<class T,class... A> auto MakeUnique(A&&... a) { return std::make_unique<T>(std::forward<A>(a)...); }
template<class T> using DebugOnly=T;
template<class T> class Maybe : public std::optional<T> {
 public:
  using std::optional<T>::optional;
  bool isNothing() const { return !this->has_value(); }
};
template<class T> Maybe<T> Some(T t) { return Maybe<T>(std::move(t)); }
inline std::nullopt_t Nothing() { return std::nullopt; }
template<class T,size_t N> class Vector {
  std::vector<T> storage;
  size_t used=0;
 public:
  using ElementType=T;
  static constexpr size_t InlineLength=N;
  size_t length() const { return used; }
  size_t size() const { return used; }
  size_t capacity() const { return storage.size(); }
  bool empty() const { return !used; }
  T* begin() { return storage.data(); }
  const T* begin() const { return storage.data(); }
  T* end() { return begin()+used; }
  const T* end() const { return begin()+used; }
  T* data() { return begin(); }
  const T* data() const { return begin(); }
  T& operator[](size_t i) { assert(i<used); return storage[i]; }
  const T& operator[](size_t i) const { assert(i<used); return storage[i]; }
  T& back() { return (*this)[used-1]; }
  const T& back() const { return (*this)[used-1]; }
  bool reserve(size_t n) { if (n>storage.size()) storage.resize(n); return true; }
  bool resize(size_t n) { reserve(n); used=n; return true; }
  bool resizeUninitialized(size_t n) { return resize(n); }
  bool growBy(size_t n) { return resize(used+n); }
  void shrinkBy(size_t n) { assert(n<=used); used-=n; }
  void clearAndFree() { storage.clear(); used=0; }
  void clear() { clearAndFree(); }
  template<class U> bool append(U&& t) { if(used==storage.size()) storage.push_back(std::forward<U>(t)); else storage[used]=std::forward<U>(t); ++used; return true; }
  bool append(const T* p,size_t n) { for(size_t i=0;i<n;++i) append(p[i]); return true; }
  template<class... A> bool emplaceBack(A&&... a) { return append(T(std::forward<A>(a)...)); }
  T* insert(T* p, const T& t) { size_t i=p-begin(); storage.insert(storage.begin()+i,t); ++used; return begin()+i; }
  void erase(T* p) { auto i=p-begin(); for(size_t j=i+1;j<used;++j) storage[j-1]=std::move(storage[j]); --used; }
};
template<class T> class Span : public std::span<T> {
 public:
  using std::span<T>::span;
  template<class U,size_t N> Span(const Vector<U,N>& v):std::span<T>(v.begin(),v.length()){}
  friend constexpr auto operator<=>(const Span& a,const Span& b) { return std::lexicographical_compare_three_way(a.begin(),a.end(),b.begin(),b.end()); }
  friend constexpr bool operator==(const Span& a,const Span& b) { return std::equal(a.begin(),a.end(),b.begin(),b.end()); }
};
template<class T> Span(T*,size_t)->Span<T>;
template<size_t N> constexpr Span<const char> MakeStringSpan(const char (&s)[N]) { return {s,N-1}; }
constexpr Span<const char> MakeStringSpan(const char* s) { size_t n=0; while(s[n]) ++n; return {s,n}; }
template<class T> constexpr bool IsAscii(T c) { return uint32_t(c)<128; }
template<class T> constexpr bool IsAsciiUppercaseAlpha(T c) { return c>='A'&&c<='Z'; }
template<class T> constexpr bool IsAsciiLowercaseAlpha(T c) { return c>='a'&&c<='z'; }
template<class T> constexpr bool IsAsciiAlpha(T c) { return IsAsciiUppercaseAlpha(c)||IsAsciiLowercaseAlpha(c); }
template<class T> constexpr bool IsAsciiDigit(T c) { return c>='0'&&c<='9'; }
template<class T> constexpr bool IsAsciiAlphanumeric(T c) { return IsAsciiAlpha(c)||IsAsciiDigit(c); }
template<class T> constexpr unsigned AsciiAlphanumericToNumber(T c) { return IsAsciiDigit(c)?c-'0':(IsAsciiLowercaseAlpha(c)?c-'a':c-'A')+10; }
namespace intl {
enum class ICUError { OutOfMemory, InternalError };
using ICUResult=Result<Ok,ICUError>;
inline bool ICUSuccessForStringSpan(UErrorCode s) { return U_SUCCESS(s)||s==U_STRING_NOT_TERMINATED_WARNING; }
inline ICUError ToICUError(UErrorCode s) { return s==U_MEMORY_ALLOCATION_ERROR?ICUError::OutOfMemory:ICUError::InternalError; }
template<auto Count,auto Get> struct AvailableLocalesEnumeration {};
}
}
