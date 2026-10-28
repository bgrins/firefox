import Rounding
open RoundInterval RoundInterval.Strategy
example : (-4 : Int) < -5 ∧ (-5 : Int) < -4 + 2 := by
  decide
