import RelativeBaseline
open FlexRelativeBaseline
example : correctedDistance false .horizontal ⟨160,80⟩ { exampleFrame with normalProperty := some ⟨0,100⟩ } = referenceDistance false .horizontal ⟨160,80⟩ exampleFrame := by decide +kernel
