import Rounding

namespace RoundOverflowWitness

open RoundInterval

def quotient : Int := 2 ^ 128
def maxFinite : Int := (2 ^ 24 - 1) * 2 ^ 104

theorem exact_scaled_results (mode : Strategy) :
    roundExact mode quotient 0 quotient quotient = quotient ∧
    roundExact mode (-quotient) 0 (-quotient) (-quotient) = -quotient := by
  constructor <;> apply exact_multiple_preserved

theorem quotient_beyond_finite_and_rounding_threshold :
    maxFinite < quotient ∧ 2 ^ 128 - 2 ^ 103 < quotient := by
  decide

theorem operands_within_normal_exponent_range :
    (-126 : Int) ≤ -64 ∧ -64 ≤ 127 ∧ -126 ≤ 64 ∧ 64 ≤ 127 ∧
    (2 ^ 64 : Int) < maxFinite := by
  decide

theorem quotient_coordinate_identity :
    (2 ^ 64 : Int) * 2 ^ 64 = quotient := by
  decide

end RoundOverflowWitness

#print axioms RoundOverflowWitness.exact_scaled_results
#print axioms RoundOverflowWitness.quotient_beyond_finite_and_rounding_threshold
#print axioms RoundOverflowWitness.operands_within_normal_exponent_range
#print axioms RoundOverflowWitness.quotient_coordinate_identity
