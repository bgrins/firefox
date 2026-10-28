import Std

namespace RoundBoundedSignificand

theorem quotient_from_relative_step (a b binade scale q r : Int)
    (nonnegative : 0 ≤ a) (positiveStep : 0 < b)
    (remainderLower : 0 ≤ r) (remainderUpper : r < b)
    (decomposition : a = q * b + r)
    (inputUpper : a < 2 * binade) (stepLower : binade ≤ scale * b) :
    0 ≤ q ∧ q < 2 * scale := by
  constructor
  · by_cases nonnegativeQ : 0 ≤ q
    · exact nonnegativeQ
    · have qUpper : q ≤ -1 := by omega
      have product := Int.mul_le_mul_of_nonneg_right qUpper (by omega : 0 ≤ b)
      simp only [Int.neg_one_mul] at product
      omega
  · by_cases bound : q < 2 * scale
    · exact bound
    · have qLower : 2 * scale ≤ q := by omega
      have product := Int.mul_le_mul_of_nonneg_right qLower (by omega : 0 ≤ b)
      rw [Int.mul_assoc] at product
      omega

def DyadicCapacity (value : Int) : Prop :=
  ∃ coefficient : Int, ∃ exponent : Nat,
    -(2^53 : Int) < coefficient ∧ coefficient < (2^53 : Int) ∧
    exponent ≤ 253 ∧ value = coefficient * (2 : Int)^exponent

theorem adjacent_capacity (a b binade scale q r m : Int) (e : Nat)
    (nonnegative : 0 ≤ a) (positiveStep : 0 < b)
    (remainderLower : 0 ≤ r) (remainderUpper : r < b)
    (decomposition : a = q * b + r)
    (inputUpper : a < 2 * binade)
    (stepLower : binade ≤ scale * b) (scaleUpper : scale ≤ 268435456)
    (mantissaLower : 0 < m) (mantissaUpper : m < 16777216)
    (stepEncoding : b = m * (2 : Int)^e) (exponentBound : e ≤ 253) :
    DyadicCapacity (q * b) ∧ DyadicCapacity ((q + 1) * b) ∧
    DyadicCapacity (-(q * b)) ∧ DyadicCapacity (-((q + 1) * b)) := by
  have qb := quotient_from_relative_step a b binade scale q r
    nonnegative positiveStep remainderLower remainderUpper decomposition inputUpper stepLower
  have qUpper : q + 1 ≤ 536870912 := by omega
  have lowerNonnegative : 0 ≤ q * m := Int.mul_nonneg qb.1 (by omega)
  have order := Int.mul_le_mul_of_nonneg_right (show q ≤ q + 1 by omega) (by omega : 0 ≤ m)
  have upperFirst := Int.mul_le_mul_of_nonneg_right qUpper (by omega : 0 ≤ m)
  have upperSecond := Int.mul_le_mul_of_nonneg_left
    (show m ≤ 16777215 by omega) (by decide : (0 : Int) ≤ 536870912)
  have capacity : 0 ≤ q * m ∧ q * m < 9007199254740992 ∧
      0 ≤ (q + 1) * m ∧ (q + 1) * m < 9007199254740992 := by omega
  have power : (2^53 : Int) = 9007199254740992 := by decide
  refine ⟨⟨q * m, e, ?_, ?_, exponentBound, ?_⟩,
    ⟨(q + 1) * m, e, ?_, ?_, exponentBound, ?_⟩,
    ⟨-(q * m), e, ?_, ?_, exponentBound, ?_⟩,
    ⟨-((q + 1) * m), e, ?_, ?_, exponentBound, ?_⟩⟩
  all_goals first | (rw [power]; omega) | (simp [stepEncoding, Int.mul_assoc, Int.neg_mul])

theorem binary64_capacity_window {value : Int} (h : DyadicCapacity value) :
    ∃ coefficient : Int, ∃ exponent : Nat,
      value = coefficient * (2 : Int)^exponent ∧
      -(2^53 : Int) < coefficient ∧ coefficient < (2^53 : Int) ∧
      -1022 ≤ (exponent : Int) - 149 ∧ (exponent : Int) - 149 + 52 ≤ 1023 := by
  rcases h with ⟨coefficient, exponent, lo, hi, bound, encoding⟩
  refine ⟨coefficient, exponent, encoding, ?_, ?_, ?_, ?_⟩
  all_goals simp only [show (2^53 : Int) = 9007199254740992 by decide] at *
  all_goals omega

example : 268435456 ≤ (268435456 : Int) * 1 ∧
    536870911 < 2 * (268435456 : Int) ∧
    536870911 = (536870911 : Int) * 1 + 0 := by decide

example : (536870912 : Int) * 16777215 < 2^53 := by decide

example : (536870912 : Int) * 16777215 ≥ 2^52 := by decide

example : (536870912 : Int) = 536870912 * 1 + 0 ∧
    ¬ ((536870912 : Int) < 536870912) := by decide

example : (536870912 : Int) < 2 * 536870912 ∧
    ¬ ((536870912 : Int) ≤ 268435456 * 1) := by decide

example : (268435456 : Int) ≤ 268435456 * 1 ∧
    (536870912 : Int) = 2 * 268435456 := by decide

example : (2^149 : Int) ≤ 268435456 * (11184811 * 2^124) ∧
    ¬ ((2^149 : Int) ≤ 268435456 * 5) := by decide

example : DyadicCapacity (3 * 11184811 * (2 : Int)^124) := by
  exact ⟨33554433, 124, by decide, by decide, by decide, by decide⟩

example (binade step : Int) (smallBinade : binade ≤ 268435456)
    (positiveGridStep : 1 ≤ step) : binade ≤ 268435456 * step := by omega

#print axioms quotient_from_relative_step
#print axioms adjacent_capacity
#print axioms binary64_capacity_window

end RoundBoundedSignificand
