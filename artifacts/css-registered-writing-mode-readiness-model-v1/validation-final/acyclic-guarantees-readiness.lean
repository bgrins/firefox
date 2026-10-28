import Readiness
open WritingModeReadiness
example : ranked = true → (run badOrder initial).writingMode = some .vertical := by
  decide +kernel
