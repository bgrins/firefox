import re
from pathlib import Path

BASE = Path(__file__).resolve().parent


def definition(text, name):
    start = text.index("nsGridContainerFrame::Grid::" + name + "(")
    end = text.index("\n}", start) + 2
    return text[start:end] + "\n"


def source(namespace, files, candidate):
    methods = ["ResolveLineRangeHelper", "ResolveLineRange", "ResolveAbsPosLineRange"]
    declarations = []
    definitions = []
    for method in methods:
        body = files[method]
        result = "nsGridContainerFrame::Grid::LinePair" if method.endswith("Helper") else "nsGridContainerFrame::LineRange"
        definitions.append(result + " " + body)
        decl = body[:body.index("{")].replace("nsGridContainerFrame::Grid::", "")
        if candidate and method == "ResolveLineRange":
            decl = decl.replace("bool aIsAbsPos)", "bool aIsAbsPos = false)")
        declarations.append(("LinePair " if method.endswith("Helper") else "LineRange ") + decl + ";")
    return "namespace " + namespace + " {\n" + PRELUDE + "\n" + "\n".join(declarations) + "\n};\n};\n" + "\n".join(definitions) + "\n}\n"


PRELUDE = r"""
__CONSTANTS__
enum class LogicalAxis { Inline, Block };
enum class LogicalEdge { Start, End };
using LogicalSide = LogicalEdge;
LogicalSide MakeLogicalSide(LogicalAxis, LogicalEdge edge) { return edge; }
struct nsStylePosition {};
struct Name {
  bool empty;
  bool IsEmpty() const { return empty; }
};
struct StyleGridLine {
  int32_t line_num;
  bool is_span;
  Name name;
  int32_t resolved;
  bool IsAuto() const { return line_num == 0 && !is_span && name.empty; }
  const Name* LineName() const { return &name; }
};
struct LineNameMap { int32_t mClampMinLine, mClampMaxLine; };
struct nsGridContainerFrame {
__LINE_RANGE__
  struct Grid {
    using LinePair = std::pair<int32_t,int32_t>;
    std::vector<std::tuple<int32_t,int32_t,uint32_t,LogicalSide>> calls;
    int32_t ResolveLine(const StyleGridLine& line, int32_t nth, uint32_t from,
                        const LineNameMap&, LogicalSide side, uint32_t,
                        const nsStylePosition*) {
      calls.emplace_back(line.line_num, nth, from, side);
      return line.name.empty ? int32_t(from) + std::clamp(nth,kMinLine,kMaxLine) : line.resolved;
    }
"""


MAIN = r"""
using Pair = std::pair<int32_t,int32_t>;
static uint64_t normal_count = 0, abs_count = 0, projection_count = 0;
int32_t cap(int32_t x, int32_t lo, int32_t hi) {
  return x < lo ? lo : (x > hi ? hi : x);
}
Pair finalize(Pair p, int32_t lo, int32_t hi) {
  p = {cap(p.first,lo,hi), cap(p.second,lo,hi)};
  auto left = std::min(p.first,p.second), right = std::max(p.first,p.second);
  if (left == right) {
    left = std::min(left,hi-1);
    right = left+1;
  }
  return {left,right};
}
int32_t project(int32_t x, int32_t lo, int32_t hi) {
  return lo <= x && x <= hi ? x : 23457;
}
Pair projected(Pair p, int32_t lo, int32_t hi) {
  return {project(p.first,lo,hi),project(p.second,lo,hi)};
}
void require(bool yes, const char* what) {
  if (!yes) { std::cerr << what << '\n'; std::exit(1); }
}
int main() {
  std::vector<int32_t> nums = {-10001,-10000,-7,-2,-1,0,1,2,3,4,7,9999,10000,10001};
  std::vector<int32_t> resolutions = {-10001,-10000,-7,-1,0,1,2,3,4,7,9999,10000,10001,13457};
  std::vector<std::pair<int32_t,int32_t>> maps = {{-10000,10000},{1,2},{1,3},{1,10000},{1,20001}};
  std::vector<int32_t> explicitEnds = {2,3,9999,10000};
  for (auto map : maps) for (auto explicitEnd : explicitEnds)
    for (auto first : nums) for (auto second : nums)
      for (int firstKind=0; firstKind<4; ++firstKind)
        for (int secondKind=0; secondKind<4; ++secondKind) {
    bool firstSpan = firstKind >= 2, secondSpan = secondKind >= 2;
    bool firstNamed = firstKind % 2, secondNamed = secondKind % 2;
    if ((firstSpan && first <= 0 && !firstNamed) ||
        (secondSpan && second <= 0 && !secondNamed) ||
        (firstSpan && first < 0) || (secondSpan && second < 0)) continue;
    for (auto resolution : resolutions) {
      Before::StyleGridLine a{first,firstSpan,{!firstNamed},resolution};
      Before::StyleGridLine b{second,secondSpan,{!secondNamed},resolution+1};
      After::StyleGridLine c{first,firstSpan,{!firstNamed},resolution};
      After::StyleGridLine d{second,secondSpan,{!secondNamed},resolution+1};
      Before::LineNameMap m{map.first,map.second};
      After::LineNameMap n{map.first,map.second};
      Before::nsGridContainerFrame::Grid old;
      After::nsGridContainerFrame::Grid now;
      auto oldNormal = old.ResolveLineRange(a,b,m,Before::LogicalAxis::Inline,explicitEnd,nullptr);
      auto newNormal = now.ResolveLineRange(c,d,n,After::LogicalAxis::Inline,explicitEnd,nullptr,false);
      require(oldNormal.mUntranslatedStart == newNormal.mUntranslatedStart &&
              oldNormal.mUntranslatedEnd == newNormal.mUntranslatedEnd,"normal-flow changed");
      require(old.calls.size() == now.calls.size(),"resolver call count changed");
      for (size_t i=0;i<old.calls.size();++i) {
        auto [on,ot,of,os] = old.calls[i];
        auto [nn,nt,nf,ns] = now.calls[i];
        require(on==nn && ot==nt && of==nf && int(os)==int(ns),"resolver call arguments changed");
      }
      ++normal_count;
      if (a.IsAuto() || b.IsAuto()) continue;
      auto helper = now.ResolveLineRangeHelper(c,d,n,After::LogicalAxis::Inline,explicitEnd,nullptr,-10000,10000);
      auto actual = now.ResolveAbsPosLineRange(c,d,n,After::LogicalAxis::Inline,explicitEnd,1,3,nullptr);
      Pair expected;
      if (helper.first == 23457) expected = {23457,23457};
      else expected = projected(finalize(helper,-10000,10000),1,3);
      require(Pair(actual.mUntranslatedStart,actual.mUntranslatedEnd) == expected,"abspos policy/finalizer mismatch");
      ++abs_count;
      if (helper.first != 23457 && helper.first != helper.second &&
          -10000 <= helper.first && helper.first <= 10000 &&
          -10000 <= helper.second && helper.second <= 10000) {
        auto spec = projected({std::min(helper.first,helper.second),std::max(helper.first,helper.second)},1,3);
        require(Pair(actual.mUntranslatedStart,actual.mUntranslatedEnd) == spec,"endpoint projection mismatch");
        ++projection_count;
      }
    }
  }
  struct Witness { int32_t a, b; bool spanA, spanB; int32_t wantA, wantB; };
  const Witness witnesses[] = {
    {4,5,false,false,23457,23457}, {-5,-4,false,false,23457,23457},
    {4,1,false,true,23457,23457}, {1,-4,true,false,23457,23457},
    {3,1,false,true,3,23457}, {1,1,true,false,23457,1},
    {4,2,false,false,2,23457}, {2,-4,false,false,23457,2},
    {3,1,false,false,1,3}
  };
  for (auto w : witnesses) {
    After::StyleGridLine a{w.a,w.spanA,{true},0}, b{w.b,w.spanB,{true},0};
    After::LineNameMap map{1,3};
    After::nsGridContainerFrame::Grid grid;
    auto actual = grid.ResolveAbsPosLineRange(a,b,map,After::LogicalAxis::Inline,3,1,3,nullptr);
    require(actual.mUntranslatedStart == w.wantA && actual.mUntranslatedEnd == w.wantB,
            "independent endpoint witness mismatch");
  }
  std::cout << "{\"normal_flow_cases\":" << normal_count << ",\"abspos_cases\":" << abs_count
            << ",\"bounded_distinct_projection_cases\":" << projection_count << "}\n";
}
"""


def generate(read):
    before = {n: read(n + "-before.inc") for n in ["ResolveLineRangeHelper", "ResolveLineRange", "ResolveAbsPosLineRange"]}
    after = {n: read(n + "-after.inc") for n in before}
    common = read("AutoIfOutside.inc")
    global PRELUDE
    original = PRELUDE
    PRELUDE = PRELUDE.replace("__LINE_RANGE__", read("LineRange-adapter.inc")).replace("__CONSTANTS__", read("constants.inc")) + common
    try:
        return "#include <algorithm>\n#include <cstdint>\n#include <cstdlib>\n#include <iostream>\n#include <tuple>\n#include <utility>\n#include <vector>\n#define MOZ_ASSERT(x,...) do { if (!(x)) std::abort(); } while(false)\n#define MOZ_UNLIKELY(x) (x)\n" + source("Before", before, False) + source("After", after, True) + MAIN
    finally:
        PRELUDE = original
