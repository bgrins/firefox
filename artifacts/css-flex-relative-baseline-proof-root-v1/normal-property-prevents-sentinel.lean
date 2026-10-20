import RelativeBaseline
open FlexRelativeBaseline
example : correctedDistance false .verticalRL ⟨0,80⟩ { exampleFrame with actual := ⟨0,0⟩, expectedNormal := ⟨0,0⟩, size := ⟨1073741823,50⟩, firstAscent := 0 } ≠ unset := by decide +kernel
