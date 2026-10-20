import LiveAtoms
namespace IndependentReview
open OrderedTypes TypeMutations

theorem every_finite_prefix (input : List Nat) (ops : List (Op Nat)) :
    (history (start input 7 9) ops).1.native =
      (referenceHistory 7 (firsts [] input) ops).1 ∧
    observed (history (start input 7 9) ops).1 =
      (referenceHistory 7 (firsts [] input) ops).1 := by
  have good := history_good (start input 7 9) ops (start_good input 7 9)
  have result := arbitrary_successful_observations input ops 7 9
  exact ⟨(public_native _ good).symm.trans result.1, result.1⟩

theorem lazy_observe_then_readd :
    (history (start [3,1,3] 7 9) [.observe, .delete 3, .observe, .add 3, .observe]).1.native = [1,3] := by
  decide +kernel

theorem lazy_materialize_twice (xs : List Nat) :
    materialize (materialize (start xs 7 9)) = materialize (start xs 7 9) :=
  materialize_idempotent _

def live : LiveAtoms.State Nat Nat := ⟨[0], [0]⟩

theorem different_live_equal_atom_not_canonical :
    ¬ LiveAtoms.Canonical (fun a => a % 2) live.native 0 2 := by
  intro h
  have bad := h.2 0 (by decide) (by decide)
  omega

theorem noncanonical_delete_breaks_agreement :
    (LiveAtoms.operation live (.delete 0 2)).1.native = [0] ∧
    (LiveAtoms.operation live (.delete 0 2)).1.backing = [] := by
  decide +kernel

def generations : List (LiveAtoms.Op Nat Nat) :=
  [.add 0 0, .delete 0 0, .add 0 2, .delete 0 2, .add 0 4]

theorem generations_admitted :
    LiveAtoms.AdmittedHistory (fun a => a % 2) ⟨[], []⟩ generations := by
  simp [LiveAtoms.AdmittedHistory, LiveAtoms.admitted, LiveAtoms.operation,
    LiveAtoms.Canonical, generations]

theorem generations_observe_new_owner :
    (LiveAtoms.history (⟨[], []⟩ : LiveAtoms.State Nat Nat) generations).1 = ⟨[4], [0]⟩ := by
  decide +kernel

theorem utf16_not_unicode_normalized :
    firsts [] ([[0x61,0x301], [0xe1], [0x61,0x301]] : List AtomProvider.DOMString) =
      [[0x61,0x301], [0xe1]] := by decide +kernel

theorem utf16_surrogate_nul_distinct :
    firsts [] ([[0xd800], [0xdc00], [0], [], [0xd800]] : List AtomProvider.DOMString) =
      [[0xd800], [0xdc00], [0], []] := by decide +kernel

theorem ghost_weak_key_drops_value :
    (initialRun (⟨[3], []⟩ : Initial Nat) [3]).native = [] := by decide +kernel

def world : TypeObservation.World Nat :=
  ⟨fun d => if d = 9 then some 7 else none, fun _ => []⟩

theorem active_identity_without_installation_not_enough :
    observed (start [3] 7 9) = [3] ∧
    TypeObservation.nativeMatch world ⟨9,true,true⟩ [3] (fun _ => true) = false := by
  decide +kernel

theorem valid_current_match_does_not_update_arbitrary_cache :
    let current : TypeObservation.World Nat := ⟨fun _ => some 7, fun _ => []⟩
    let cached := true
    TypeObservation.nativeMatch current ⟨9,true,true⟩ [3] (fun _ => true) ≠ cached := by
  decide +kernel

#print axioms every_finite_prefix
#print axioms lazy_observe_then_readd
#print axioms lazy_materialize_twice
#print axioms different_live_equal_atom_not_canonical
#print axioms noncanonical_delete_breaks_agreement
#print axioms generations_admitted
#print axioms generations_observe_new_owner
#print axioms utf16_not_unicode_normalized
#print axioms utf16_surrogate_nul_distinct
#print axioms ghost_weak_key_drops_value
#print axioms active_identity_without_installation_not_enough
#print axioms valid_current_match_does_not_update_arbitrary_cache
end IndependentReview
