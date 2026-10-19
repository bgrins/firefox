import Observation
namespace TaintShortcut

def equalNat (a b : Nat) : Bool := a == b
def clean : State Nat := some ⟨7,false⟩
def tainted : State Nat := some ⟨7,true⟩
def literal : Incoming Nat := ⟨7,false,false,false,true⟩
def explicitTaint : Incoming Nat := ⟨7,false,true,false,true⟩
def directResolve (d : Incoming Nat) : State Nat := some (declaredValue d)
def referenceResolve (d : Incoming Nat) : State Nat :=
  if d.hasReferences then some ⟨9,true⟩ else some (declaredValue d)

theorem nat_payload_sound : PayloadSound equalNat := by
  intro a b h; simpa [equalNat] using h

theorem old_map_loses_taint :
    observeURL some (mapUpdate (payloadSame equalNat) false clean tainted) = some 7 ∧
    observeURL some tainted = none := by decide

theorem old_map_retains_taint :
    observeURL some (mapUpdate (payloadSame equalNat) false tainted clean) = none ∧
    observeURL some clean = some 7 := by decide

theorem map_repair_both_directions :
    mapUpdate (metadataSame equalNat) false clean tainted = tainted ∧
    mapUpdate (metadataSame equalNat) false tainted clean = clean := by decide

theorem map_only_masked_by_gate :
    pipeline (payloadSame equalNat) (metadataSame equalNat) directResolve false clean explicitTaint = clean ∧
    pipeline (payloadSame equalNat) (metadataSame equalNat) directResolve false tainted literal = tainted := by decide

theorem gate_only_masked_by_map :
    pipeline (metadataSame equalNat) (payloadSame equalNat) directResolve false clean explicitTaint = clean ∧
    pipeline (metadataSame equalNat) (payloadSame equalNat) directResolve false tainted literal = tainted := by decide

theorem unique_branch_cannot_fix_prior_skip :
    pipeline (payloadSame equalNat) (metadataSame equalNat) directResolve true clean explicitTaint = clean ∧
    pipeline (payloadSame equalNat) (metadataSame equalNat) directResolve true tainted literal = tainted := by decide

theorem combined_both_directions :
    pipeline (metadataSame equalNat) (metadataSame equalNat) directResolve false clean explicitTaint = tainted ∧
    pipeline (metadataSame equalNat) (metadataSame equalNat) directResolve false tainted literal = clean := by decide

theorem taint_sources_distinct :
    (declaredValue explicitTaint).attr = true ∧
    (declaredValue (⟨7,true,false,true,true⟩ : Incoming Nat)).attr = true := by decide

theorem missing_not_valid_empty :
    metadataSame equalNat none (some ⟨0,false⟩) = false ∧
    metadataSame equalNat (some ⟨0,false⟩) none = false := by decide

theorem provider_without_domain : ReferenceFreeProvider referenceResolve := by
  intro d _ h; simp [referenceResolve, h]

theorem unresolved_domain_necessary :
    let d : Incoming Nat := ⟨7,false,false,true,true⟩
    ¬EligibleDomain d ∧
    pipeline (metadataSame equalNat) (metadataSame equalNat) referenceResolve false clean d = clean ∧
    observeURL some (referenceResolve d) = none ∧ observeURL some clean = some 7 := by
  simp [EligibleDomain, pipeline, metadataSame, equalNat, declaredValue, clean, referenceResolve, observeURL]

theorem comparator_projection_necessary :
    mapUpdate (metadataSame (fun _ _ : Nat => true)) false clean (some ⟨8,false⟩) = clean ∧
    observeURL some clean ≠ observeURL some (some ⟨8,false⟩) := by decide

theorem finite_taint_round_trip :
    let ops : List (Op Nat) := [⟨explicitTaint,false⟩,⟨literal,false⟩]
    optimizedHistory equalNat directResolve clean ops = clean ∧
    optimizedHistory equalNat directResolve clean (ops.take 1) = tainted := by decide
end TaintShortcut
