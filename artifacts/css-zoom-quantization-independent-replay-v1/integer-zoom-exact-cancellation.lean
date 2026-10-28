import Quantization
open ZoomQuantization
example : crossError tiny (normalize (quantize tiny (Zoom.mk ⟨2, by decide⟩ ⟨1, by decide⟩)) (Zoom.mk ⟨2, by decide⟩ ⟨1, by decide⟩)) = 0 := by
  decide +kernel
