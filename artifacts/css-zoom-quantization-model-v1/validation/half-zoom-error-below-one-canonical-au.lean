import Quantization
open ZoomQuantization
example : (crossError tiny (normalize (quantize tiny half) half)).natAbs < 100 := by
  decide +kernel
