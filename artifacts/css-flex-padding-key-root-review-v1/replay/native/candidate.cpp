
#include <algorithm>
#include <cstdint>
#include <iostream>
using nscoord = int32_t;
struct WritingMode {};
struct LogicalSize { int32_t i,b; bool operator==(const LogicalSize&) const = default; };
struct LogicalMargin {
  int32_t iStart,iEnd,bStart,bEnd;
  bool operator==(const LogicalMargin&) const = default;
  int32_t BStartEnd(WritingMode) const { return bStart+bEnd; }
};
struct ReflowInput {
  int32_t data[9];
  LogicalSize ComputedSize() const { return {data[0],data[1]}; }
  LogicalMargin ComputedLogicalBorderPadding(WritingMode) const { return {data[5],data[6],data[7],data[8]}; }
  WritingMode GetWritingMode() const { return {}; }
  int32_t ComputedMinBSize() const { return data[2]; }
  int32_t ComputedMaxBSize() const { return data[3]; }
  int32_t AvailableBSize() const { return data[4]; }
};
struct ReflowOutput { int32_t BSize(WritingMode) const { return 100000; } };
class nsFlexContainerFrame { public: class CachedBAxisMeasurement; };
class nsFlexContainerFrame::CachedBAxisMeasurement {
  struct Key {
    const LogicalSize mComputedSize;
    const LogicalMargin mBorderPadding;
    const nscoord mComputedMinBSize;
    const nscoord mComputedMaxBSize;
    const nscoord mAvailableBSize;

    explicit Key(const ReflowInput& aRI)
        : mComputedSize(aRI.ComputedSize()),
          mBorderPadding(
              aRI.ComputedLogicalBorderPadding(aRI.GetWritingMode())),
          mComputedMinBSize(aRI.ComputedMinBSize()),
          mComputedMaxBSize(aRI.ComputedMaxBSize()),
          mAvailableBSize(aRI.AvailableBSize()) {}

    bool operator==(const Key& aOther) const = default;
  };

  const Key mKey;

  // This could/should be const, but it's non-const for now just because it's
  // assigned via a series of steps in the constructor body:
  nscoord mBSize;

 public:
  CachedBAxisMeasurement(const ReflowInput& aReflowInput,
                         const ReflowOutput& aReflowOutput)
      : mKey(aReflowInput) {
    // To get content-box bsize, we have to subtract off border & padding
    // (and floor at 0 in case the border/padding are too large):
    WritingMode itemWM = aReflowInput.GetWritingMode();
    nscoord borderBoxBSize = aReflowOutput.BSize(itemWM);
    mBSize =
        borderBoxBSize -
        aReflowInput.ComputedLogicalBorderPadding(itemWM).BStartEnd(itemWM);
    mBSize = std::max(0, mBSize);
  }

  /**
   * Returns true if this cached flex item measurement is valid for (i.e. can
   * be expected to match the output of) a measuring reflow whose input
   * parameters are given via aReflowInput.
   */
  bool IsValidFor(const ReflowInput& aReflowInput) const {
    return mKey == Key(aReflowInput);
  }

  nscoord BSize() const { return mBSize; }
};

int main() {
  int id,present,dirty;
  while(std::cin>>id>>present>>dirty) {
    ReflowInput old{},current{};
    for(auto& value:old.data) if(!(std::cin>>value)) return 2;
    for(auto& value:current.data) if(!(std::cin>>value)) return 2;
    nsFlexContainerFrame::CachedBAxisMeasurement cached(old,ReflowOutput{});
    bool valid=cached.IsValidFor(current);
    std::cout<<id<<" "<<valid<<" "<<(present&&!dirty&&valid)<<" "<<cached.BSize()<<"\n";
  }
}
