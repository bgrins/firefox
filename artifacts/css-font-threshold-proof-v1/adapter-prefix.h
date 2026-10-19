#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <new>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <tuple>
#include <utility>
#include <vector>
#define MOZ_ASSERT(x, ...) assert(x)
#define NS_ASSERTION(x, ...) assert(x)
#define MOZ_ASSERT_UNREACHABLE(...) assert(false)
#define MOZ_UNLIKELY(x) (x)
#define LOG_FONTLIST_ENABLED() false
#define LOG_FONTLIST(...) ((void)0)
#define MOZ_LOG_TEST(...) false
#define MOZ_LOG(...) ((void)0)
#define AUTO_PROFILER_LABEL_DYNAMIC_NSCSTRING(...) ((void)0)
struct nsACString : std::string {
  using std::string::string;
  const char* get() const { return c_str(); }
  void AppendFloat(float) {}
  void Append(const char*) {}
};
using nsCString = nsACString;
using nsAutoCString = nsCString;
using gfxFloat = double;
using LogModule = int;
enum class LogLevel { Debug };
enum class ThreadProfilingFeatures { Sampling, Markers };
int Combine(ThreadProfilingFeatures, ThreadProfilingFeatures) { return 0; }
bool profiler_thread_is_being_profiled(int) { return false; }
template<class... T> nsCString nsPrintfCString(T...) { return {}; }
int Compare(const nsCString& a, const nsCString& b) { return a.compare(b); }
namespace intl { enum class Script { Common }; struct UnicodeProperties {
  static Script GetScriptCode(uint32_t) { return Script::Common; }
}; }
using Script = intl::Script;
std::vector<std::string> events;
void note(const std::string& label, int id) { events.push_back(label + std::to_string(id)); }
template<class T> struct RefPtr {
  T* value = nullptr;
  RefPtr() = default;
  RefPtr(T* p) : value(p) {}
  operator T*() const { return value; }
  T* operator->() const { return value; }
  T& operator*() const { return *value; }
  T* get() const { return value; }
  T* forget() { return std::exchange(value, nullptr); }
  void swap(T*& p) { std::swap(value, p); }
};
template<class T> using already_AddRefed = T*;
template<class T> struct nsTArray : std::vector<T> {
  using std::vector<T>::vector;
  uint32_t Length() const { return this->size(); }
  bool IsEmpty() const { return this->empty(); }
  void AppendElement(T t) { this->push_back(t); }
  void Clear() { this->clear(); }
  void SetLength(size_t n) { this->resize(n); }
  template<class F> void RemoveElementsBy(F f) {
    this->erase(std::remove_if(this->begin(), this->end(), f), this->end());
  }
};
template<class T, size_t N> using AutoTArray = nsTArray<T>;
struct Lock {
  void AssertCurrentThreadIn() const {}
  bool LockedForWritingByCurrentThread() const { return true; }
};
struct AutoReadLock { explicit AutoReadLock(const Lock&) {} };
constexpr uint8_t kItalicMask = 2, kBoldMask = 1;
constexpr uint8_t kRegularFaceIndex = 0, kBoldFaceIndex = 1;
constexpr uint8_t kItalicFaceIndex = 2, kBoldItalicFaceIndex = 3;

std::vector<void*> allocations;
