import Examples
open NumberContext NumberContext.Examples
example : mutate .dropTail (.variadic .minMax [literal, ratio]) = summary (.variadic .minMax [literal, ratio]) := by
  decide +kernel
