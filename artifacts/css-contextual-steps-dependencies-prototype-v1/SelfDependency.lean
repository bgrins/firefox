namespace ContextualEasing

def count (font : Nat) : Nat := if font < 15 then 2 else 1

def nextFont (font : Nat) : Nat :=
  let steps := count font
  10 + (10 * ((3 * steps) / 4)) / steps

theorem concrete_two_cycle : nextFont 10 = 15 ∧ nextFont 15 = 10 := by decide +kernel

theorem image (font : Nat) : nextFont font = 10 ∨ nextFont font = 15 := by
  unfold nextFont count
  split <;> decide +kernel

theorem no_fixed_point (font : Nat) : nextFont font ≠ font := by
  intro fixed
  rcases image font with low | high
  · have eq : font = 10 := fixed.symm.trans low
    subst font
    contradiction
  · have eq : font = 15 := fixed.symm.trans high
    subst font
    contradiction

#print axioms concrete_two_cycle
#print axioms image
#print axioms no_fixed_point
end ContextualEasing
