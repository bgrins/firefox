import Std
namespace IndependentFlexReview
def M : Int := 1073741823
def raw (a b c d o : Int) := max (max (a+b) (c+d)) o
def fixed (a b c d o : Int) := min M (raw a b c d o)
theorem defined_but_above_cap_changes :
    raw 700000000 1400000000 (-M) (-M) 0 = 2100000000 ∧
    fixed 700000000 1400000000 (-M) (-M) 0 = M := by decide +kernel
theorem earlier_subtraction_is_outside_int32 :
    (2147483647 : Int) - (-1) > 2147483647 := by decide +kernel
theorem exported_last_baseline_safe (line offset : Int)
    (hl : 0 ≤ line ∧ line ≤ M)
    (ho : -M ≤ offset ∧ offset ≤ 2147483647) :
    -2147483648 ≤ line - offset ∧ line - offset ≤ 2147483647 := by
  unfold M at *
  omega
theorem three_ordinary_lines_still_overflow : M + M + M > 2147483647 := by decide +kernel
theorem both_min_max_clamps_preserved (a b c d o lo hi : Int)
    (hhi : hi ≤ M) :
    max lo (min hi (fixed a b c d o)) = max lo (min hi (raw a b c d o)) := by
  unfold fixed
  have : min hi (min M (raw a b c d o)) = min hi (raw a b c d o) := by omega
  rw [this]
#print axioms defined_but_above_cap_changes
#print axioms earlier_subtraction_is_outside_int32
#print axioms exported_last_baseline_safe
#print axioms three_ordinary_lines_still_overflow
#print axioms both_min_max_clamps_preserved
end IndependentFlexReview
