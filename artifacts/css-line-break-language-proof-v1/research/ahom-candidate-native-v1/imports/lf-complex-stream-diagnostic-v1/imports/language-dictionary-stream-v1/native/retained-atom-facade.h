#include <functional>
#include <thread>
extern "C" void language_trace(const char*);
template<class T> class already_AddRefed {
  T* p;
 public:
  explicit already_AddRefed(T* value):p(value){}
  T* take() { auto old=p;p=nullptr;return old; }
};
namespace mozilla {
template<class T> struct RefPtrTraits {
  static void AddRef(T* p) { p->AddRef(); }
  static void Release(T* p) { p->Release(); }
};
}
#define MOZ_ONLY_USED_TO_AVOID_STATIC_CONSTRUCTORS
#define MOZ_OWNING_REF
#include "static-ref-native.h"
static const auto mainThread=std::this_thread::get_id();
static std::vector<std::function<void()>> shutdownActions;
namespace mozilla {
template<class T> void ClearOnShutdown(T* pointer) {
  assert(std::this_thread::get_id()==mainThread);
  shutdownActions.emplace_back([pointer]{*pointer=nullptr;});
  language_trace("shutdown register");
}
}
struct nsAtom {
  std::string value;
  unsigned refs=1;
  void AddRef() { ++refs; language_trace(("atom addref "+value+" "+std::to_string(refs)).c_str()); }
  void Release() { assert(refs>1); --refs; language_trace(("atom release "+value+" "+std::to_string(refs)).c_str()); }
};
