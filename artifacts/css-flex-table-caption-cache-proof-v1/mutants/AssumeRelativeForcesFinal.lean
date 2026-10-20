import Witnesses
open CaptionCache
example : needsFinal (reusableFinal 120) ⟨120,false⟩ 120 = true := by decide +kernel
