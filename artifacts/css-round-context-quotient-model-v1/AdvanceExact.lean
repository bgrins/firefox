import Rounding
open RoundInterval RoundInterval.Strategy
example : roundExact up 2 0 2 3 = 3 := by
  decide
