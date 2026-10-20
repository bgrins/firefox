import Witnesses
open CaptionCache
example : blockOnly (tableInput 200) ⟨(),⟨300,200⟩⟩ = candidate (tableInput 200) ⟨(),⟨300,200⟩⟩ := by decide +kernel
