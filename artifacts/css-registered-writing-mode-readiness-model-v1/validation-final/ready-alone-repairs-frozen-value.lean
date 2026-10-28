import Readiness
open WritingModeReadiness
example : (ensureWritingMode (run badOrder initial)).writingMode = some .vertical := by
  decide +kernel
