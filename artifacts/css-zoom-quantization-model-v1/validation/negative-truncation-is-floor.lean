import Quantization
open ZoomQuantization
example : quantize (negate tiny) oneAndHalf = -12 := by
  decide +kernel
