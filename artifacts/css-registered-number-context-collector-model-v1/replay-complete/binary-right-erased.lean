import Examples
open NumberContext NumberContext.Examples
example : mutate .dropRight (.binary .logBase literal ratio) = summary (.binary .logBase literal ratio) := by
  decide +kernel
