import Std
import Init.Data.Rat.Lemmas

open scoped Rat

namespace RoundRemainder

structure Remainder (a b q r : Int) : Prop where
  positiveStep : 0 < b
  decomposition : a = q * b + r
  boundedBelow : -b < r
  boundedAbove : r < b
  sign : if a < 0 then r ≤ 0 else 0 ≤ r

def lower (a b r : Int) : Int := if a < 0 then a - r - b else a - r

def upper (a b r : Int) : Int := if a < 0 then a - r else a - r + b

structure Adjacent (a b l u : Int) : Prop where
  multiples : ∃ index : Int, l = index * b ∧ u = (index + 1) * b
  below : l < a
  above : a < u

def magnitude (x : Int) : Int := if x < 0 then -x else x

def nearest (a l u : Int) : Int := if a - l < u - a then l else u

def towardZero (l u : Int) : Int := if magnitude l < magnitude u then l else u

theorem remainder_bounds {a b q r : Int} (h : Remainder a b q r) (nonzero : r ≠ 0) :
    Adjacent a b (lower a b r) (upper a b r) := by
  rcases h with ⟨positive, decomposition, below, above, sign⟩
  by_cases negative : a < 0
  · simp only [negative, ↓reduceIte] at sign
    refine ⟨⟨q - 1, ?_, ?_⟩, ?_, ?_⟩
    · simp only [lower, negative, ↓reduceIte, Int.sub_mul, Int.one_mul]
      omega
    · simp only [upper, negative, ↓reduceIte]
      have : q - 1 + 1 = q := by omega
      rw [this]
      omega
    · simp only [lower, negative, ↓reduceIte]
      omega
    · simp only [upper, negative, ↓reduceIte]
      omega
  · simp only [negative, ↓reduceIte] at sign
    refine ⟨⟨q, ?_, ?_⟩, ?_, ?_⟩
    · simp only [lower, negative, ↓reduceIte]
      omega
    · simp only [upper, negative, ↓reduceIte, Int.add_mul, Int.one_mul]
      omega
    · simp only [lower, negative, ↓reduceIte]
      omega
    · simp only [upper, negative, ↓reduceIte]
      omega

theorem adjacent_directed {a b l u : Int} (positive : 0 < b) (h : Adjacent a b l u) :
    (∀ k : Int, k * b ≤ a → k * b ≤ l) ∧
    (∀ k : Int, a ≤ k * b → u ≤ k * b) := by
  rcases h.multiples with ⟨index, lowerMultiple, upperMultiple⟩
  constructor
  · intro k bound
    by_cases order : k ≤ index
    · have product := Int.mul_le_mul_of_nonneg_right order (by omega : 0 ≤ b)
      rw [lowerMultiple]
      exact product
    · have order : index + 1 ≤ k := by omega
      have product := Int.mul_le_mul_of_nonneg_right order (by omega : 0 ≤ b)
      rw [← upperMultiple] at product
      have := h.above
      omega
  · intro k bound
    by_cases order : index + 1 ≤ k
    · have product := Int.mul_le_mul_of_nonneg_right order (by omega : 0 ≤ b)
      rw [upperMultiple]
      exact product
    · have order : k ≤ index := by omega
      have product := Int.mul_le_mul_of_nonneg_right order (by omega : 0 ≤ b)
      rw [← lowerMultiple] at product
      have := h.below
      omega

theorem nearest_minimal_upper_tie {a b l u : Int} (positive : 0 < b)
    (h : Adjacent a b l u) :
    (∃ k : Int, nearest a l u = k * b) ∧
    ∀ k : Int, magnitude (nearest a l u - a) ≤ magnitude (k * b - a) ∧
      (magnitude (nearest a l u - a) = magnitude (k * b - a) → k * b ≤ nearest a l u) := by
  have directed := adjacent_directed positive h
  rcases h.multiples with ⟨index, lowerMultiple, upperMultiple⟩
  have low := h.below
  have high := h.above
  constructor
  · unfold nearest
    split
    · exact ⟨index, lowerMultiple⟩
    · exact ⟨index + 1, upperMultiple⟩
  · intro k
    by_cases side : k * b ≤ a
    · have outside := directed.1 k side
      unfold nearest magnitude
      split <;> split <;> split <;> omega
    · have outside := directed.2 k (by omega)
      unfold nearest magnitude
      split <;> split <;> split <;> omega

theorem remainder_toward_zero {a b q r : Int} (h : Remainder a b q r) (nonzero : r ≠ 0) :
    towardZero (lower a b r) (upper a b r) = a - r := by
  have positive := h.positiveStep
  have bounds := remainder_bounds h nonzero
  have directed := adjacent_directed h.positiveStep bounds
  by_cases negative : a < 0
  · have upperNonpositive : upper a b r ≤ 0 := by
      have := directed.2 0 (by simp; omega)
      simpa using this
    have low := bounds.below
    simp only [lower, upper, negative, ↓reduceIte] at upperNonpositive low ⊢
    unfold towardZero magnitude
    split <;> split <;> split <;> omega
  · have lowerNonnegative : 0 ≤ lower a b r := by
      have := directed.1 0 (by simp; omega)
      simpa using this
    have high := bounds.above
    simp only [lower, upper, negative, ↓reduceIte] at lowerNonnegative high ⊢
    unfold towardZero magnitude
    split <;> split <;> split <;> omega

theorem common_denominator_order (x y d : Int) (positive : 0 < d) :
    x /. d < y /. d ↔ x < y := by
  have pos : (0 : Rat) < (d : Rat) := by
    exact Rat.intCast_lt_intCast.mpr positive
  rw [Rat.divInt_eq_div, Rat.divInt_eq_div, Rat.div_def, Rat.div_def,
    Rat.mul_lt_mul_right (Rat.inv_pos.mpr pos), Rat.intCast_lt_intCast]

theorem rational_nearest_refinement (a l u d : Int) (positive : 0 < d) :
    (if a /. d - l /. d < u /. d - a /. d then l /. d else u /. d) =
      nearest a l u /. d := by
  have nonzero : d ≠ 0 := by omega
  have difference (x y : Int) : x /. d - y /. d = (x - y) /. d := by
    rw [Rat.divInt_sub_divInt x y nonzero nonzero, ← Int.sub_mul,
      Rat.divInt_mul_right nonzero]
  simp only [difference, common_denominator_order _ _ _ positive]
  unfold nearest
  split <;> rfl

example {a b q : Int} (h : Remainder a b q 0) : a = q * b := by
  have := h.decomposition
  omega
example : ¬ ∃ k : Int, 33554432 = k * 11184811 := by omega
example : (33554432 : Int) /. 11184811 < 3 ∧
    3 - (33554432 : Int) /. 11184811 = (1 : Int) /. 11184811 := by decide +kernel

example : Remainder 33554432 11184811 2 11184810 := by
  constructor <;> decide
example : lower 33554432 11184811 11184810 = 22369622 ∧
    upper 33554432 11184811 11184810 = 33554433 := by decide
example : Remainder (-33554432) 11184811 (-2) (-11184810) := by
  constructor <;> decide
example : lower (-33554432) 11184811 (-11184810) = -33554433 ∧
    upper (-33554432) 11184811 (-11184810) = -22369622 := by decide
example : nearest (-3) (-4) (-2) = -2 ∧ nearest 3 2 4 = 4 := by decide
example : (3 : Int) * 11184811 > 33554432 := by decide

#print axioms remainder_bounds
#print axioms adjacent_directed
#print axioms nearest_minimal_upper_tie
#print axioms remainder_toward_zero
#print axioms common_denominator_order
#print axioms rational_nearest_refinement

end RoundRemainder
