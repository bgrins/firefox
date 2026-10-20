import Std

namespace FlexLineSum

def limit : Nat := 1073741823
def cap (n : Nat) := min limit n

def accumulate : Nat → List Nat → Nat
  | initial, [] => cap initial
  | initial, line :: rest => accumulate (cap (initial + line)) rest

theorem cap_add (a b : Nat) : cap (cap a + b) = cap (a + b) := by
  unfold cap
  omega

theorem arbitrary_line_sum (initial : Nat) (lines : List Nat) :
    accumulate initial lines = cap (initial + lines.sum) := by
  induction lines generalizing initial with
  | nil => simp [accumulate]
  | cons line rest ih =>
    simp only [accumulate, List.sum_cons]
    rw [ih, cap_add]
    simp [Nat.add_assoc]

theorem capped_initial_sum (initial : Nat) (lines : List Nat) :
    accumulate (cap initial) lines = cap (initial + lines.sum) := by
  rw [arbitrary_line_sum, cap_add]

theorem gap_product_fits_signed64 (gap count : Nat)
    (hg : gap ≤ 2147483647) (hn : 1 ≤ count ∧ count ≤ 4294967295) :
    gap * (count - 1) ≤ 9223372036854775807 := by
  have hn' : count - 1 ≤ 4294967294 := by omega
  have bound := Nat.mul_le_mul hg hn'
  omega

theorem capped_step_fits_signed64 (initial line : Nat)
    (hl : line ≤ 2147483647) :
    cap initial + line ≤ 9223372036854775807 := by
  unfold cap limit
  omega

theorem stored_value_fits_signed32 (n : Nat) : cap n ≤ 2147483647 := by
  unfold cap limit
  omega

theorem bounded_min_max_observer (initial lo hi : Nat) (lines : List Nat)
    (hh : hi ≤ limit) :
    max lo (min hi (accumulate (cap initial) lines)) =
      max lo (min hi (initial + lines.sum)) := by
  rw [capped_initial_sum]
  unfold cap
  omega

theorem identity_within_range (initial : Nat) (lines : List Nat)
    (h : initial + lines.sum ≤ limit) :
    accumulate (cap initial) lines = initial + lines.sum := by
  rw [capped_initial_sum]
  unfold cap
  omega

theorem three_large_lines_overflow_signed32 :
    (3 * 12000000 * 60 : Nat) > 2147483647 := by decide +kernel

theorem three_large_gaps_overflow_signed32 :
    (3 * 12000000 * 60 : Nat) > 2147483647 := by decide +kernel

theorem capped_browser_observer :
    min 6000 (accumulate 0 [720000000, 720000000, 720000000]) = 6000 := by
  decide +kernel

#print axioms cap_add
#print axioms arbitrary_line_sum
#print axioms capped_initial_sum
#print axioms gap_product_fits_signed64
#print axioms capped_step_fits_signed64
#print axioms stored_value_fits_signed32
#print axioms bounded_min_max_observer
#print axioms identity_within_range
#print axioms three_large_lines_overflow_signed32
#print axioms three_large_gaps_overflow_signed32
#print axioms capped_browser_observer

end FlexLineSum
