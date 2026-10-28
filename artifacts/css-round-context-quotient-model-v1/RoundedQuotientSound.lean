import Rounding
open RoundInterval RoundInterval.Strategy
example : choose nearest 33554433 33554432 33554436 = choose down witnessValue witnessLower witnessUpper := by
  decide
