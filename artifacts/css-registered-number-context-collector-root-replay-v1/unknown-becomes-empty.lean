import Examples
open NumberContext NumberContext.Examples
example : mutate .unknownEmpty unsupportedRatio = summary unsupportedRatio := by
  decide +kernel
