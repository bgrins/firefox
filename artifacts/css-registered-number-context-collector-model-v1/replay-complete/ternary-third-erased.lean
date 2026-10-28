import Examples
open NumberContext NumberContext.Examples
example : mutate .dropThird (.ternary .clamp literal literal ratio) = summary (.ternary .clamp literal literal ratio) := by
  decide +kernel
