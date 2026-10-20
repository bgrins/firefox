#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <optional>
#include <vector>
using nscoord = int32_t;
struct Nothing {};
template<class T> struct Maybe {
  std::optional<T> v;
  Maybe(Nothing):v(std::nullopt) {}
  Maybe(T x):v(x) {}
  template<class F> auto map(F f) const -> Maybe<decltype(f(T{}))> {
    return v ? Maybe<decltype(f(T{}))>(f(*v)) : Maybe<decltype(f(T{}))>(Nothing{});
  }
};
template<class T> Maybe<T> Some(T x) { return Maybe<T>(x); }
/* CSS_MIN_MAX */
struct WritingMode { int mode; };
enum class BaselineSharingGroup { First, Last };
enum class BaselineExportContext { LineLayout, Other };
struct Input {
 int id,mode; bool first,line,block,button,contain;
 nscoord outer,inner,border,fallback; std::optional<nscoord> child;
};
static const Input* current;
static std::vector<int> trace;
void checkArgs(WritingMode wm,BaselineSharingGroup group,BaselineExportContext context) {
 if(wm.mode!=current->mode || (group==BaselineSharingGroup::First)!=current->first ||
    (context==BaselineExportContext::LineLayout)!=current->line) std::abort();
}
struct nsBlockFrame {
 bool IsButtonLike() const { trace.push_back(1);return current->button; }
 Maybe<nscoord> GetNaturalBaselineBOffset(WritingMode wm,BaselineSharingGroup group,BaselineExportContext context) const {
  checkArgs(wm,group,context);trace.push_back(4);
  return current->child ? Some(*current->child) : Maybe<nscoord>(Nothing{});
 }
 nscoord BSize(WritingMode wm) const { if(wm.mode!=current->mode)std::abort();trace.push_back(5);return current->inner; }
};
nsBlockFrame* do_QueryFrame(nsBlockFrame* frame) { trace.push_back(0);return current->block?frame:nullptr; }
struct Display {
 bool IsContainLayout() const { trace.push_back(3);return current->contain; }
};
struct LogicalMargin {
 nscoord BStart(WritingMode wm) const { if(wm.mode!=current->mode)std::abort();return current->border; }
};
struct LogicalSize {
 nscoord BSize(WritingMode wm) const { if(wm.mode!=current->mode)std::abort();return current->outer; }
};
struct ScrollContainerFrame {
 nsBlockFrame child; nsBlockFrame* mScrolledFrame=&child; Display display;
 const Display* StyleDisplay() const { return &display; }
 nscoord SynthesizeFallbackBaseline(WritingMode wm,BaselineSharingGroup group) const {
  checkArgs(wm,group,current->line?BaselineExportContext::LineLayout:BaselineExportContext::Other);
  trace.push_back(2);return current->fallback;
 }
 LogicalMargin GetLogicalUsedBorder(WritingMode wm) const { if(wm.mode!=current->mode)std::abort();trace.push_back(6);return {}; }
 LogicalSize GetLogicalSize(WritingMode wm) const { if(wm.mode!=current->mode)std::abort();trace.push_back(7);return {}; }
 Maybe<nscoord> GetNaturalBaselineBOffset(WritingMode,BaselineSharingGroup,BaselineExportContext) const;
};
/* METHOD */
int main() {
 const std::vector<Input> cases={/* CASES */};
 for(const auto& row:cases) {
  current=&row;trace.clear();
  bool legacy=row.line&&!row.first&&row.block&&!row.button;
  int64_t sum=int64_t(row.border)+row.child.value_or(0);
  if(/* ORIGINAL */ && !legacy&&!row.contain&&row.child && (sum<INT32_MIN||sum>INT32_MAX)) {
   std::cout<<row.id<<"|SKIP|\n";continue;
  }
  ScrollContainerFrame frame;
  auto value=frame.GetNaturalBaselineBOffset({row.mode},row.first?BaselineSharingGroup::First:BaselineSharingGroup::Last,row.line?BaselineExportContext::LineLayout:BaselineExportContext::Other);
  std::cout<<row.id<<"|";if(value.v)std::cout<<*value.v;else std::cout<<"none";
  std::cout<<"|";for(size_t i=0;i<trace.size();i++){if(i)std::cout<<",";std::cout<<trace[i];}std::cout<<"\n";
 }
}
