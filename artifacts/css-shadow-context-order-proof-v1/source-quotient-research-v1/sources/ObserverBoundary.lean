import TwoPhaseQuotient
namespace ShadowOrder

def observerWitness : List (OccurrenceEvent Nat Nat) :=
 [⟨0,.rule⟩,⟨0,.effect 7⟩]

def isLogicalWitness (event : OccurrenceEvent Nat Nat) : Bool :=
 match event.action with
 | .rule => false
 | .effect _ => true

def afterFirstRuleDeletion :=
 [⟨0,.rule⟩] ++ remaining [0] observerWitness.tail

theorem observation_before_guard_not_deletion_invariant :
 observerWitness.any isLogicalWitness = true ∧
 afterFirstRuleDeletion.any isLogicalWitness = false := by
 decide

theorem witness_selected_value_unchanged :
 occurrenceSetExecution (fun (_ : Nat) _ => true) (fun _ _ value => value)
   observerWitness [] 0 = 0 ∧
 occurrenceDeletionReference (fun (_ : Nat) _ => true) (fun _ _ value => value)
   observerWitness 0 = 0 := by
 simp [observerWitness,occurrenceSetExecution,occurrenceDeletionReference,remaining]

theorem observer_composition_requires_an_observer_relation
 (left right : σ) (computed : left = right) (leftObservation rightObservation : ω)
 (observed : leftObservation = rightObservation) :
 (leftObservation,left) = (rightObservation,right) := by
 cases computed
 cases observed
 rfl

#print axioms observation_before_guard_not_deletion_invariant
#print axioms witness_selected_value_unchanged
#print axioms observer_composition_requires_an_observer_relation
end ShadowOrder
