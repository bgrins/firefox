import Dispatch
import ReviewedKernel
namespace ProviderRoot
open ScrollBaselineProvider ScrollBaselineDispatch

theorem independent_projection_agrees (first : Bool)
    (outer inner border baseline : Int) :
    repaired first outer inner border baseline =
      ProviderReview.project first outer inner border baseline := by
  cases first <;>
    simp [repaired, fromStart, clamp, ProviderReview.project, ProviderReview.clamp]

theorem delegated_result_matches_independent_projection (i : Input)
    (noLegacy : legacy i = false) (noContain : i.contain = false) :
    (native i).value = i.child.map
      (ProviderReview.project i.first i.outer i.inner i.border) := by
  simp only [native_value_split, noLegacy, noContain, Bool.false_eq_true, ite_false]
  cases i.child with
  | none => rfl
  | some d => simp [independent_projection_agrees]

def legacyCase : Input :=
  ⟨false, true, true, false, true, 0, 0, 0, 77, none⟩

theorem legacy_output_is_not_a_border_clamped_delegated_value :
    (native legacyCase).value = some 77 ∧
    (native legacyCase).calls = [.queryBlock, .queryButton, .fallback] := by
  decide +kernel

theorem negative_outer_extent_is_outside_the_range_contract :
    repaired false (-1) 50 9 30 = -1 := by decide +kernel

theorem absent_child_preserves_laziness_after_button_exception :
    native { legacyCase with button := true, contain := false } =
      ⟨none, [.queryBlock, .queryButton, .containment, .child]⟩ := by decide +kernel

#print axioms independent_projection_agrees
#print axioms delegated_result_matches_independent_projection
#print axioms legacy_output_is_not_a_border_clamped_delegated_value
#print axioms negative_outer_extent_is_outside_the_range_contract
#print axioms absent_child_preserves_laziness_after_button_exception
end ProviderRoot
