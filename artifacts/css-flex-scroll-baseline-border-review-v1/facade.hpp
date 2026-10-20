#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <optional>
using nscoord=int32_t;
using WritingMode=int;
enum class BaselineSharingGroup {First,Last};
enum class BaselineExportContext {LineLayout,Other};
struct Nothing {};
template<class T>struct Maybe {std::optional<T> v;Maybe(Nothing):v(){}Maybe(T x):v(x){}template<class F>auto map(F f)const -> Maybe<decltype(f(T{}))>{if(v)return f(*v);return Nothing{};}};
template<class T>Maybe<T> Some(T x){return x;}
struct Counters {int style=0,query=0,natural=0,inner=0,border=0,outer=0,fallback=0,wm=-1,group=-1,context=-1;};
static Counters counts;
struct Frame {bool present=false;nscoord baseline=0,inner=0;virtual ~Frame()=default;
 Maybe<nscoord> GetNaturalBaselineBOffset(WritingMode wm,BaselineSharingGroup g,BaselineExportContext c)const{counts.natural++;counts.wm=wm;counts.group=int(g);counts.context=int(c);if(present)return baseline;return Nothing{};}
 nscoord BSize(WritingMode wm)const{assert(wm==counts.wm);counts.inner++;return inner;}
};
struct nsBlockFrame:Frame{bool button=false;bool IsButtonLike()const{return button;}};
nsBlockFrame* do_QueryFrame(Frame* f){counts.query++;return dynamic_cast<nsBlockFrame*>(f);}
struct LogicalMargin{nscoord start=0,end=0;nscoord BStart(int)const{return start;}nscoord BEnd(int)const{return end;}};
struct LogicalSize{nscoord size;nscoord BSize(int)const{return size;}};
struct Display{bool contain;bool IsContainLayout()const{return contain;}};
struct ScrollContainerFrame{
 Frame* mScrolledFrame;nscoord outer,bstart,bend,synth;Display display;
 const Display* StyleDisplay()const{counts.style++;return &display;}
 LogicalMargin GetLogicalUsedBorder(int)const{counts.border++;return {bstart,bend};}
 LogicalSize GetLogicalSize(int)const{counts.outer++;return {outer};}
 nscoord SynthesizeFallbackBaseline(int,BaselineSharingGroup)const{counts.fallback++;return synth;}
 Maybe<nscoord> GetNaturalBaselineBOffset(WritingMode,BaselineSharingGroup,BaselineExportContext)const;
};
