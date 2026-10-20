import Witnesses
namespace IndependentFragmentation
open Fragmentation

theorem forced_whole_flow_admission_needed :
    scan { three with capacity := 3, opportunities := [{ (atA 1) with controls := [.force] }] } stages =
      some (.strict, .finish) := by decide

theorem ancestor_provider_is_material :
    rules .strict three.types three.content { cut := 1, kind := .c, ancestors := [] } = true ∧
    rules .strict three.types three.content { cut := 1, kind := .c, ancestors := [.avoid] } = false := by decide

theorem no_zero_or_complete_cut :
    candidate .strict three (atA 0) = false ∧
    candidate .strict three (atA 3) = false := by decide

theorem unrelated_lines_do_not_satisfy_orphans :
    lineCount 8 [⟨.line 8 0, 1⟩, ⟨.line 99 0, 1⟩, ⟨.line 8 1, 1⟩] = 2 := by decide

theorem positive_start_decoration_changes_top :
    noBelowTop { zeroInput with content := [box 0 0, box 1 5], decorations := [⟨1, 0, false⟩] } [atA 1] = false := by decide

theorem region_validity_not_enforced_by_slice_function :
    graphicSlice graphic [] = some 2 ∧
    graphicSlice graphic [atA 1] = none ∧
    ¬ RegionCandidateAdmitted graphic [atA 1] := by decide

theorem complete_slice_history_inhabited : SliceHistory 5 [2, 2, 1] := by
  apply SliceHistory.step (by decide) (by decide)
  apply SliceHistory.step (by decide) (by decide)
  apply SliceHistory.step (by decide) (by decide)
  exact SliceHistory.finish

#print axioms forced_whole_flow_admission_needed
#print axioms ancestor_provider_is_material
#print axioms no_zero_or_complete_cut
#print axioms unrelated_lines_do_not_satisfy_orphans
#print axioms positive_start_decoration_changes_top
#print axioms region_validity_not_enforced_by_slice_function
#print axioms complete_slice_history_inhabited
end IndependentFragmentation
