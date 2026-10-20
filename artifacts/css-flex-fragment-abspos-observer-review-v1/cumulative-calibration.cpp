#include <cstdint>
#include <cstdio>
#include <cstdlib>
using nscoord = int32_t;
constexpr nscoord NS_UNCONSTRAINEDSIZE = 1073741823;
int main(int argc,char** argv) {
  if (argc != 3) return 2;
  nscoord mCumulativeContainingBlockBSize = std::strtol(argv[1],nullptr,10);
  const nscoord availBSize = std::strtol(argv[2],nullptr,10);
  if (availBSize != NS_UNCONSTRAINEDSIZE) {
    mCumulativeContainingBlockBSize += availBSize;
  }
  std::printf("%d\n",mCumulativeContainingBlockBSize);
}
