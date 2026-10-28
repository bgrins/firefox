import Quantization
open ZoomQuantization
example : crossError tiny (normalize (quantize tiny oneAndHalf) oneAndHalf) = 0 := by
  decide +kernel
