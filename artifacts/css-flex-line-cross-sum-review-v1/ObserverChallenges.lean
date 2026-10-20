import LineSum
namespace IndependentLineSum
open FlexLineSum

def bounded (v : Option Nat) : Prop := ∀ n, v = some n → n ≤ limit

def applyBounds (lo hi : Option Nat) (n : Nat) : Nat :=
  let above := match hi with | none => n | some h => min n h
  match lo with | none => above | some l => max above l

theorem optional_bounds_commute_with_saturation (lo hi : Option Nat) (n : Nat)
    (hl : bounded lo) (hh : bounded hi) :
    applyBounds lo hi (cap n) = cap (applyBounds lo hi n) := by
  cases lo <;> cases hi <;> simp_all [bounded, applyBounds, cap] <;> omega

theorem automatic_minimum_commutes_with_saturation (n computed : Nat)
    (hc : computed ≤ limit) :
    max (cap n) computed = cap (max n computed) := by
  unfold cap
  omega

theorem complete_optional_observer (lo hi : Option Nat) (initial computed : Nat)
    (lines : List Nat) (automatic : Bool)
    (hl : bounded lo) (hh : bounded hi) (hc : computed ≤ limit) :
    (if automatic then max (applyBounds lo hi (accumulate (cap initial) lines)) computed
      else applyBounds lo hi (accumulate (cap initial) lines)) =
    cap (if automatic then max (applyBounds lo hi (initial + lines.sum)) computed
      else applyBounds lo hi (initial + lines.sum)) := by
  rw [capped_initial_sum, optional_bounds_commute_with_saturation lo hi _ hl hh]
  cases automatic
  · rfl
  · exact automatic_minimum_commutes_with_saturation _ _ hc

theorem original_identity_within_supported_range (lo hi : Option Nat)
    (initial : Nat) (lines : List Nat) (h : initial + lines.sum ≤ limit) :
    applyBounds lo hi (accumulate (cap initial) lines) =
      applyBounds lo hi (initial + lines.sum) := by
  rw [identity_within_range _ _ h]

theorem absent_max_changes_some_old_defined_values :
    (1440000000 : Nat) ≤ 2147483647 ∧
    applyBounds none none (accumulate 0 [720000000, 720000000]) = limit ∧
    applyBounds none none (1440000000 : Nat) ≠ limit := by decide +kernel

theorem minimum_wins_when_bounds_conflict :
    applyBounds (some 80) (some 60) (accumulate 0 [720000000, 720000000]) = 80 := by
  decide +kernel

theorem empty_container_one_empty_line_has_no_gap :
    accumulate (cap (720000000 * (1 - 1))) [0] = 0 := by decide +kernel

theorem maximum_count_and_gap_product :
    (2147483647 * (4294967295 - 1) : Nat) = 9223372028264841218 ∧
    (2147483647 * (4294967295 - 1) : Nat) ≤ 9223372036854775807 := by decide +kernel

theorem nonnegative_suffix_is_necessary :
    min (1073741823 : Int) (min 1073741823 (1073741823 + 10) - 10) ≠
    min (1073741823 : Int) ((1073741823 + 10) - 10) := by decide +kernel

theorem sum_fix_does_not_prove_later_packing_safe :
    min (6000 : Int) 1073741823 - 720000000 - 720000000 - 720000000 < -2147483648 := by
  decide +kernel

end IndependentLineSum
