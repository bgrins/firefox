import FlexCollect.Preservation

namespace FlexCollect.Cases

theorem witness_targets : WitnessTargets := by unfold WitnessTargets; decide +kernel

theorem empty : collect id 100 0 ([] : List Rat) = [] := by decide +kernel
theorem primary : collect id 100 0 ([150, -50] : List Rat) = [[150], [-50]] := by decide +kernel
theorem absorption : collect id 100 0 ([150, -100] : List Rat) = [[150], [-100]] := by decide +kernel
theorem nearby : collect id 100 0 ([150, -49] : List Rat) = [[150], [-49]] := by decide +kernel
theorem positive : collect id 100 0 ([150, 20] : List Rat) = [[150], [20]] := by decide +kernel
theorem exact_negative : collect id 100 0 ([100, -50] : List Rat) = [[100, -50]] := by decide +kernel
theorem zero_fit : collect id 100 0 ([100, 0, 0] : List Rat) = [[100, 0, 0]] := by decide +kernel
theorem oversized_zero : collect id 100 0 ([150, 0] : List Rat) = [[150], [0]] := by decide +kernel
theorem negative_prefix : collect id 100 0 ([-50, 150] : List Rat) = [[-50, 150]] := by decide +kernel
theorem first_failure : collect id 100 0 ([80, 30, -50] : List Rat) = [[80], [30, -50]] := by decide +kernel
theorem gap_zero : collect id 100 10 ([100, 0] : List Rat) = [[100], [0]] := by decide +kernel
theorem gap_negative : collect id 100 10 ([100, -10] : List Rat) = [[100, -10]] := by decide +kernel
theorem gap_no_edge : collect id 100 10 ([100] : List Rat) = [[100]] := by decide +kernel
theorem zero_threshold : collect id 0 0 ([0, -1, 1] : List Rat) = [[0, -1, 1]] := by decide +kernel
theorem oversized_zero_threshold : collect id 0 0 ([1, -1] : List Rat) = [[1], [-1]] := by decide +kernel
theorem repeated_values : collect id 100 0 ([60, 60, 60] : List Rat) = [[60], [60], [60]] := by decide +kernel
theorem fractional : collect id (7/4) (1/4) ([1, 1/2] : List Rat) = [[1, 1/2]] := by decide +kernel
theorem third_preserved : collect id 100 0 ([150, -50, 20] : List Rat) = [[150], [-50, 20]] := by decide +kernel
theorem distinct_identity :
    collect Prod.snd 100 0 ([(3, 60), (8, 60), (3, 60)] : List (Nat × Rat)) =
      [[(3, 60)], [(8, 60)], [(3, 60)]] := by decide +kernel
theorem nowrap_all : nowrap ([150, -50] : List Rat) = [[150, -50]] := by decide +kernel

theorem no_absorption : collect id 100 0 ([150, -50] : List Rat) ≠ [[150, -50]] := by decide +kernel
theorem no_lookahead : collect id 100 0 ([80, 30, -50] : List Rat) ≠ [[80, 30, -50]] := by decide +kernel
theorem equality_fits : collect id 100 0 ([50, 50] : List Rat) ≠ [[50], [50]] := by decide +kernel
theorem no_prefix_floor : collect id 100 0 ([-50, 150] : List Rat) ≠ [[-50], [150]] := by decide +kernel
theorem no_duplicate_drop : (collect id 100 0 ([60, 60] : List Rat)).flatten ≠ [60] := by decide +kernel
theorem no_edge_gap : collect id 100 10 ([90, 0] : List Rat) ≠ [[90], [0]] := by decide +kernel

end FlexCollect.Cases
