import CssSemantics.CssIntegerRounding

namespace IntegerRangePolicy
open CssSemantics.CssIntegerRounding

theorem old_agrees_iff (minimum : Int) (value : Rat) :
    round (max (minimum : Rat) value) = round value ↔ minimum ≤ round value := by
  rw [round_max, round_integer]
  simp only [Int.max_def]
  split <;> omega

example : round (max (1 : Rat) (-10)) = 1 ∧ round (-10) = -10 := by decide +kernel
example : round (max (0 : Rat) (-10)) = 0 ∧ round (-10) = -10 := by decide +kernel
example : round (max (1 : Rat) (3 / 4)) = round (3 / 4) := by decide +kernel
example : ¬ (∀ x : Rat, round (max 1 x) = round x) := by
  intro h
  have bad := h (-10)
  have different : round (max (1 : Rat) (-10)) ≠ round (-10) := by decide +kernel
  exact different bad

#print axioms old_agrees_iff
end IntegerRangePolicy
