import Examples
open NumberContext NumberContext.Examples
example : mutate .dropLineHeight (.leaf .lineHeight) = summary (.leaf .lineHeight) := by
  decide +kernel
