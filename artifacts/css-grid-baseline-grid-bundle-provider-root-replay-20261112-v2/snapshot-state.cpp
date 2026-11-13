#include <cstdio>
#include <cstdlib>
#include "nsGridContainerFrame.h"

using namespace mozilla;
template <typename T> using PerLogicalAxis = nsGridContainerFrame::PerLogicalAxis<T>;
template <typename T> using PerBaseline = nsGridContainerFrame::PerBaseline<T>;

#include "snapshot-extracted.inc"

static unsigned checks = 0;
static void Check(bool value) {
  ++checks;
  if (!value) {
    std::fprintf(stderr, "state check %u failed\n", checks);
    std::abort();
  }
}

int main() {
  using R = MeasuringReflowRequest;
  Snapshot natural;
  natural.mRequest = R::NaturalFirst;
  natural.mGeometry.mBSize = 31;
  natural.mHasBaseline = true;
  natural.mBaselines[LogicalAxis::Block][BaselineSharingGroup::First] = 17;
  auto answer = natural.Result(R::NaturalFirst);
  Check(answer && answer->mBaseline && *answer->mBaseline == 17);
  auto geometry = natural.Result(R::Geometry);
  Check(geometry && !geometry->mBaseline && geometry->mBSize == 31);
  Check(natural.Result(R::NaturalFirst)->mBaseline.value() == 17);
  Check(!natural.Result(R::NaturalLast));
  natural.mHasBaseline = false;
  answer = natural.Result(R::NaturalFirst);
  Check(answer && !answer->mBaseline);
  Check(!natural.Result(R::NaturalLast));
  Snapshot grid;
  grid.mRequest = R::GridBlockFirst;
  grid.mGeometry.mBSize = 47;
  grid.mHasBaseline = true;
  grid.mHasGridBaselines = true;
  grid.mBaselines[LogicalAxis::Block][BaselineSharingGroup::First] = 11;
  grid.mBaselines[LogicalAxis::Block][BaselineSharingGroup::Last] = 23;
  grid.mBaselines[LogicalAxis::Inline][BaselineSharingGroup::First] = 37;
  grid.mBaselines[LogicalAxis::Inline][BaselineSharingGroup::Last] = 53;
  const R requests[] = {R::GridBlockFirst, R::GridBlockLast, R::GridInlineFirst, R::GridInlineLast};
  const nscoord expected[] = {11, 23, 37, 53};
  for (unsigned i = 0; i < 4; ++i) {
    auto value = grid.Result(requests[i]);
    Check(value && value->mBaseline && *value->mBaseline == expected[i] && value->mBSize == 47);
  }
  geometry = grid.Result(R::Geometry);
  Check(geometry && !geometry->mBaseline && geometry->mBSize == 47);
  Check(grid.mHasGridBaselines);
  Check(grid.Result(R::GridInlineLast)->mBaseline.value() == 53);
  Check(!grid.Result(R::NaturalFirst));
  Snapshot replacement;
  replacement.mRequest = R::Geometry;
  replacement.mGeometry.mBSize = 67;
  grid = replacement;
  Check(grid.Result(R::Geometry)->mBSize == 67);
  for (auto request : requests) {
    Check(!grid.Result(request));
  }
  Snapshot fallback;
  fallback.mRequest = R::GridInlineLast;
  fallback.mHasBaseline = true;
  fallback.mBaselines[LogicalAxis::Block][BaselineSharingGroup::First] = 79;
  Check(fallback.Result(R::GridInlineLast)->mBaseline.value() == 79);
  Check(!fallback.Result(R::GridBlockFirst));
  std::printf("PASS %u actual Snapshot projection/state checks\n", checks);
}
