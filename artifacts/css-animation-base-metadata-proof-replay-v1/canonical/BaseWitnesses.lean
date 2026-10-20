import BaseLaws
namespace BaseMetadata
open EndpointTaint

def clean (payload : Nat) : Endpoint Nat := some (some ⟨payload, false⟩)
def dirty (payload : Nat) : Endpoint Nat := some (some ⟨payload, true⟩)
def lookup (value : Endpoint Nat) : Lookup Nat Nat := fun key => if key = 7 then value else none
def customKey (key : Nat) : Bool := key == 7

def after (detector : Lookup Nat Nat → List (Entry Nat Nat) → Bool)
    (old next : Endpoint Nat) (forced : Bool := false) : SampleState Nat :=
  let entries := [(7, next)]
  tick (requestsRestyle false true (detector (lookup old) entries)) forced next ⟨old, old⟩

def repairedDetector := changed (fun a b : Nat => a == b) customKey

def originalDetector : Lookup Nat Nat → List (Entry Nat Nat) → Bool := oldChanged (fun a b : Nat => a == b)

theorem both_metadata_directions_detected :
    repairedDetector (lookup (clean 0)) [(7, dirty 0)] = true ∧
    repairedDetector (lookup (dirty 0)) [(7, clean 0)] = true := by decide

theorem original_retains_stale_sample_but_publishes_base :
    (after originalDetector (clean 0) (dirty 0)).base = dirty 0 ∧
    (after originalDetector (clean 0) (dirty 0)).sampled = clean 0 ∧
    (after originalDetector (dirty 0) (clean 0)).sampled = dirty 0 := by decide

theorem repaired_notifies_and_resamples :
    (after repairedDetector (clean 0) (dirty 0)).sampled = dirty 0 ∧
    (after repairedDetector (dirty 0) (clean 0)).sampled = clean 0 := by decide

theorem forced_tick_masks_missing_notification :
    (after originalDetector (clean 0) (dirty 0) true).sampled = dirty 0 := by decide

theorem removed_only_old_key_is_not_detected :
    repairedDetector (lookup (dirty 0)) [] = false ∧
    lookup (dirty 0) 7 ≠ (none : Endpoint Nat) := by decide

theorem missing_null_and_guaranteed_invalid_are_distinguished :
    repairedDetector (fun _ => none) [(7, none)] = false ∧
    repairedDetector (fun _ => none) [(7, some none)] = true := by decide

end BaseMetadata
