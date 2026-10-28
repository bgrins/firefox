import Quantization
open ZoomQuantization
example : crossError (normalize (quantize tiny one) one) (normalize (quantize tiny oneAndHalf) oneAndHalf) = 0 := by
  decide +kernel
