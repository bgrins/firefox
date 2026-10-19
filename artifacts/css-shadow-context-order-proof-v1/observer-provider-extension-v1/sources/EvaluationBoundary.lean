import AnimationConstructors
import ObserverBoundary
namespace ShadowOrder

def evaluationVisits [DecidableEq κ] : List (OccurrenceEvent κ α) → List κ → Nat
 | [], _ => 0
 | event::rest, excluded =>
   if event.identity ∈ excluded then evaluationVisits rest excluded
   else 1 + match event.action with
     | .rule => evaluationVisits rest (event.identity::excluded)
     | .effect _ => evaluationVisits rest excluded

def distinctRuleOccurrences : List (OccurrenceEvent Nat Nat) :=
 [⟨0,.rule⟩,⟨1,.rule⟩]

def sharedRuleKeyOccurrences : List (OccurrenceEvent Nat Nat) :=
 [⟨0,.rule⟩,⟨0,.rule⟩]

theorem exact_evaluation_visit_observer_not_quotient_invariant :
 evaluationVisits distinctRuleOccurrences [] = 2 ∧
 evaluationVisits sharedRuleKeyOccurrences [] = 1 := by
 decide

theorem rule_evaluation_counterexample_still_value_equal :
 occurrenceSetExecution (fun (_ : Nat) _ => true) (fun _ _ value => value)
   distinctRuleOccurrences [] 37 =
 occurrenceSetExecution (fun (_ : Nat) _ => true) (fun _ _ value => value)
   sharedRuleKeyOccurrences [] 37 := by
 decide

#print axioms exact_evaluation_visit_observer_not_quotient_invariant
#print axioms rule_evaluation_counterexample_still_value_equal
end ShadowOrder
