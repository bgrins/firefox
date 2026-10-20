import PublicationMap
namespace InvalidPublication

def fixtureEnv (inherits : Bool) : Environment Nat (List Nat) (List Nat) :=
  ⟨fun _ => inherits, fun _ => some [20], id, id⟩

def fixtureState : State Nat (List Nat) :=
  ⟨fun _ _ => some [20], fun _ => false, false⟩

def fixtureInvalid : Endpoint Nat (List Nat) := ⟨7, none⟩

def lowerValid : Entry Nat (List Nat) (List Nat) := ⟨7, .payload [44], true, true⟩

def serializeTokens : Option (List Nat) → List Nat
  | none => []
  | some xs => xs

theorem empty_and_invalid_same_serialization :
    serializeTokens none = serializeTokens (some []) := rfl

theorem empty_and_invalid_distinct_observation :
    referenceObservation (none : Option (List Nat)) ≠ referenceObservation (some []) := by decide

theorem valid_empty_does_not_choose_fallback : fallbackResult [61] (some []) = [] := rfl

theorem candidate_both_routes (route : Bool) :
    selected (fixtureEnv route)
      (run (fixtureEnv route) fixtureState
        (publication (fixtureEnv route).encode (some fixtureInvalid) ++ [lowerValid])) 7 = none := by
  exact (invalid_wins_suffix (fixtureEnv route) fixtureState 7 [lowerValid] rfl).1

theorem original_both_routes (route : Bool) :
    selected (fixtureEnv route)
      (step (fixtureEnv route) fixtureState (originalConvert (fixtureEnv route).encode fixtureInvalid)) 7 = some [20] := by
  exact original_invalid_uses_initial (fixtureEnv route) fixtureState 7 rfl (fun _ => rfl)

theorem dropped_declaration_resurrects :
    selected (fixtureEnv false) (run (fixtureEnv false) fixtureState [lowerValid]) 7 = some [44] := rfl

theorem valid_empty_replacement_is_wrong :
    referenceObservation (selected (fixtureEnv false)
      (step (fixtureEnv false) fixtureState ⟨7, .payload [], true, true⟩) 7) = .value [] := rfl

theorem failed_gate_is_not_a_winner :
    selected (fixtureEnv false)
      (run (fixtureEnv false) fixtureState [⟨7, .invalid, false, true⟩, lowerValid]) 7 = some [44] := rfl

theorem prior_seen_is_not_overwritten :
    selected (fixtureEnv false)
      (step (fixtureEnv false) (mark fixtureState 7) (convert id fixtureInvalid)) 7 = some [20] := rfl

theorem revert_in_lower_suffix_cannot_unmark :
    selected (fixtureEnv false)
      (run (fixtureEnv false) fixtureState
        [convert id fixtureInvalid, ⟨7, .revert, true, true⟩, lowerValid]) 7 = none := rfl

theorem payload_preservation_is_satisfiable (route : Bool) : PayloadPreserved (fixtureEnv route) := by
  intro p; rfl

theorem fallback_can_coincide_with_initial :
    fallbackResult [20] (none : Option (List Nat)) = fallbackResult [20] (some [20]) ∧
    referenceObservation (none : Option (List Nat)) ≠ referenceObservation (some [20]) := by decide

end InvalidPublication
