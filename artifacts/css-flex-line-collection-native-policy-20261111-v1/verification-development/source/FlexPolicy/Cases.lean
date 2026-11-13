import FlexPolicy.Laws

namespace FlexPolicy.Cases

theorem old_primary : old id 100 0 1000 ([150, -50] : List Rat) = [[150, -50]] := by decide +kernel
theorem patched_primary : patched id 100 0 1000 ([150, -50] : List Rat) = [[150], [-50]] := by decide +kernel

theorem old_not_collected : ¬FlexCollect.Collected id 100 0 ([150, -50] : List Rat)
    (old id 100 0 1000 [150, -50]) := by
  intro h
  have heq := FlexCollect.collected_complete id 100 0 h
  have hne : FlexCollect.collect id 100 0 ([150, -50] : List Rat) ≠ old id 100 0 1000 [150, -50] := by
    decide +kernel
  exact hne heq

theorem counterexample : CounterexampleTarget := ⟨old_primary, patched_primary, old_not_collected⟩

theorem later_large : patched id 100 0 1000 ([-50, 150] : List Rat) = [[-50, 150]] := by decide +kernel
theorem first_failure : patched id 100 0 1000 ([80, 30, -50] : List Rat) = [[80], [30, -50]] := by decide +kernel
theorem exact_fit : patched id 100 0 1000 ([50, 50] : List Rat) = [[50, 50]] := by decide +kernel
theorem zeros_fit : patched id 100 0 1000 ([100, 0, 0] : List Rat) = [[100, 0, 0]] := by decide +kernel
theorem gap_zero : patched id 100 10 1000 ([100, 0] : List Rat) = [[100], [0]] := by decide +kernel
theorem gap_signed : patched id 100 10 1000 ([100, -10] : List Rat) = [[100, -10]] := by decide +kernel
theorem gap_reset : patched id 100 30 1000 ([80, 80, -10] : List Rat) = [[80], [80, -10]] := by decide +kernel
theorem empty : patched id 100 10 1000 ([] : List Rat) = [] := by decide +kernel
theorem fractional : patched id (7/4) (1/4) 1000 ([1, 1/2] : List Rat) = [[1, 1/2]] := by decide +kernel
theorem identity_repeats :
    patched Prod.snd 100 0 1000 ([(3, 60), (8, 60), (3, 60)] : List (Nat × Rat)) =
      [[(3, 60)], [(8, 60)], [(3, 60)]] := by decide +kernel
theorem third_preserved : patched id 100 0 1000 ([150, -50, 20] : List Rat) = [[150], [-50, 20]] := by decide +kernel
theorem ordinary_negative : patched id 100 0 1000 ([80, -50] : List Rat) = [[80, -50]] := by decide +kernel
theorem positive_second : patched id 100 0 1000 ([150, 20] : List Rat) = [[150], [20]] := by decide +kernel
theorem near_negative : patched id 100 0 1000 ([150, -49] : List Rat) = [[150], [-49]] := by decide +kernel
theorem nowrap_projection : FlexCollect.nowrap ([150, -50] : List Rat) = [[150, -50]] := by decide +kernel

theorem bound_equality : patched id 100 0 100 ([50, 50] : List Rat) = [[50], [50]] := by decide +kernel
theorem bound_necessary : patched id 100 0 100 ([50, 50] : List Rat) ≠
    FlexCollect.collect id 100 0 [50, 50] := by decide +kernel
theorem no_unconditional_refinement : ¬(∀ (xs : List Rat),
    patched id 100 0 100 xs = FlexCollect.collect id 100 0 xs) := by
  intro h
  exact bound_necessary (h _)

theorem old_partition_only : (old id 100 0 1000 ([150, -50] : List Rat)).flatten = [150, -50] := by decide +kernel
theorem old_ready_fails : ¬Ready id 100 0 ([150, -50] : List Rat) := by
  intro h
  rcases h.2 with ⟨x, heq, _⟩ | hfit
  · have := congrArg List.length heq
    simp at this
  · have hx := hfit [150] [-50] rfl (by decide)
    have hnot : ¬FlexCollect.span id 0 ([150] : List Rat) ≤ 100 := by decide +kernel
    exact hnot hx

end FlexPolicy.Cases
