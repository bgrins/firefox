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
template <class NumericType>
NumericType CSSMinMax(NumericType aValue, NumericType aMinValue,
                      NumericType aMaxValue) {
  NumericType result = aValue;
  if (aMaxValue < result) {
    result = aMaxValue;
  }
  if (aMinValue > result) {
    result = aMinValue;
  }
  return result;
}
Maybe<nscoord> ScrollContainerFrame::GetNaturalBaselineBOffset(
    WritingMode aWM, BaselineSharingGroup aBaselineGroup,
    BaselineExportContext aExportContext) const {
  // Block containers (except buttons) that are scrollable always have a last
  // baseline that are synthesized from block-end margin edge.
  // Note(dshin): This behaviour is really only relevant to `inline-block`
  // alignment context. In the context of table/flex/grid alignment, first/last
  // baselines are calculated through `GetFirstLineBaseline`, which does
  // calculations of its own.
  // https://drafts.csswg.org/css-align/#baseline-export
  if (aExportContext == BaselineExportContext::LineLayout &&
      aBaselineGroup == BaselineSharingGroup::Last) {
    if (nsBlockFrame* bf = do_QueryFrame(mScrolledFrame);
        bf && !bf->IsButtonLike()) {
      return Some(SynthesizeFallbackBaseline(aWM, aBaselineGroup));
    }
  }

  if (StyleDisplay()->IsContainLayout()) {
    return Nothing{};
  }

  // OK, here's where we defer to our scrolled frame.
  return mScrolledFrame
      ->GetNaturalBaselineBOffset(aWM, aBaselineGroup, aExportContext)
      .map([this, aWM, aBaselineGroup](nscoord aBaseline) {
        const bool first = aBaselineGroup == BaselineSharingGroup::First;
        const int64_t fromStart =
            first ? int64_t(aBaseline)
                  : int64_t(mScrolledFrame->BSize(aWM)) - aBaseline;
        // Add our block-start border; the scrolled frame handles our padding.
        LogicalMargin border = GetLogicalUsedBorder(aWM);
        const auto bSize = GetLogicalSize(aWM).BSize(aWM);
        // Clamp the baseline to the border rect. See bug 1791069.
        const nscoord baseline = nscoord(CSSMinMax(
            border.BStart(aWM) + fromStart, int64_t(0), int64_t(bSize)));
        return baseline;
      });
}
int main(){int group,context,kind,contain,present,wm;nscoord outer,inner,bstart,bend,baseline,synth;
 while(std::cin>>group>>context>>kind>>contain>>present>>wm>>outer>>inner>>bstart>>bend>>baseline>>synth){
 counts={};Frame plain;nsBlockFrame block;block.button=kind==2;Frame* child=kind?static_cast<Frame*>(&block):&plain;
 child->present=present;child->baseline=baseline;child->inner=inner;
 ScrollContainerFrame frame{child,outer,bstart,bend,synth,{bool(contain)}};
 auto result=frame.GetNaturalBaselineBOffset(wm,BaselineSharingGroup(group),BaselineExportContext(context));
 std::cout<<bool(result.v)<<' '<<result.v.value_or(0)<<' '<<counts.style<<' '<<counts.query<<' '<<counts.natural<<' '<<counts.inner<<' '<<counts.border<<' '<<counts.outer<<' '<<counts.fallback<<' '<<counts.wm<<' '<<counts.group<<' '<<counts.context<<"\n";
 }
}
