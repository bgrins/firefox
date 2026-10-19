#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>
#define MOZ_ASSERT(x,...) assert(x)
#define NS_ASSERTION(x,m) assert(x)
template<class T>using DebugOnly=T;
template<class T>struct RefPtr{T*p;RefPtr(T*v):p(v){}operator T*()const{return p;}T*operator->()const{return p;}};
using nsFrameState=uint64_t;
struct gfxTextRun{
 void*data=nullptr;uint32_t flags=0;void*GetUserData()const{return data;}void SetUserData(void*p){data=p;}
 uint32_t GetFlags2()const{return flags;}template<class T>void ClearFlagBits(T f){flags&=~uint32_t(f);}
};
struct nsTextFrame{
 enum TextRunType{eInflated,eNotInflated};
 nsTextFrame*next=nullptr;gfxTextRun*mTextRun=nullptr;gfxTextRun*uninflated=nullptr;void*mFontMetrics=reinterpret_cast<void*>(1);nsFrameState state=0;
 gfxTextRun*GetTextRun(TextRunType type)const{return type==eInflated?mTextRun:uninflated;}
 nsTextFrame*GetNextContinuation()const{return next;}bool IsTextFrame()const{return true;}
 bool HasAnyStateBits(nsFrameState s)const{return state&s;}void RemoveStateBits(nsFrameState s){state&=~s;}
 static int UninflatedTextRunProperty(){return 0;}gfxTextRun*GetProperty(int)const{return uninflated;}void RemoveProperty(int){uninflated=nullptr;}
 bool RemoveTextRun(gfxTextRun*);void ClearTextRun(nsTextFrame*,TextRunType);
};
namespace nsTextFrameUtils{struct Flags{enum{IsSimpleFlow=0x10,MightHaveGlyphChanges=0x1000};};}
struct SimpleTextRunUserData{nsTextFrame*mFrame;};
