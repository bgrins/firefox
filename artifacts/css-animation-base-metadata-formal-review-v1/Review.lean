import BaseLaws
open EndpointTaint BaseMetadata
namespace IndependentBaseReview

def clean : Endpoint Nat := some (some ⟨1, false⟩)
def dirty : Endpoint Nat := some (some ⟨1, true⟩)
def old (value : Endpoint Nat) : Lookup Nat Nat := fun k => if k = 7 then value else none
def custom (k : Nat) : Bool := k == 7

theorem nonreflexive_comparator_may_request :
    changed (fun _ _ : Nat => false) custom (old clean) [(7, clean)] = true := by decide

theorem arbitrary_comparator_cannot_hide_custom_taint :
    changed (fun _ _ : Nat => true) custom (old clean) [(7, dirty)] = true := by decide

theorem key_alignment_matters :
    changed (fun a b : Nat => a == b) custom (old dirty) [(8, clean)] = true ∧
    changed (fun a b : Nat => a == b) custom (old dirty) [(7, dirty)] = false := by decide

theorem custom_filter_is_not_universal_taint_detection :
    changed (fun a b : Nat => a == b) (fun _ => false) (old clean) [(7, dirty)] = false := by decide

theorem prior_coherence_is_necessary_for_skip_observation :
    let delta := changed (fun a b : Nat => a == b) custom (old clean) [(7, clean)]
    tainted (tick (requestsRestyle false true delta) false clean ⟨clean, dirty⟩).sampled ≠
      tainted clean := by decide

theorem outer_absence_is_not_guaranteed_invalid :
    endpointSame (fun a b : Nat => a == b) none (some none) = false ∧
    tainted (none : Endpoint Nat) = tainted (some none : Endpoint Nat) := by decide

theorem request_and_forced_delivery_are_separate :
    requestsRestyle false true true = true ∧
    (tick false false dirty ⟨clean, clean⟩).sampled = clean ∧
    (tick true false dirty ⟨clean, clean⟩).sampled = dirty := by decide

end IndependentBaseReview
#print axioms IndependentBaseReview.nonreflexive_comparator_may_request
#print axioms IndependentBaseReview.arbitrary_comparator_cannot_hide_custom_taint
#print axioms IndependentBaseReview.key_alignment_matters
#print axioms IndependentBaseReview.custom_filter_is_not_universal_taint_detection
#print axioms IndependentBaseReview.prior_coherence_is_necessary_for_skip_observation
#print axioms IndependentBaseReview.outer_absence_is_not_guaranteed_invalid
#print axioms IndependentBaseReview.request_and_forced_delivery_are_separate
