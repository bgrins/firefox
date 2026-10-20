import TypeObservation
namespace TypeWitnesses
open OrderedTypes TypeMutations TypeObservation

def oldStart (xs : List Nat) : State Nat := ⟨xs, none, 7, 9⟩
def oldDeleted := (operation (oldStart [0,0]) (.delete 0)).1

theorem original_duplicate_disagreement :
    oldDeleted.native = [0] ∧ observed oldDeleted = [] := by decide +kernel

theorem repaired_duplicate_delete :
    (operation (start [0,0] 7 9) (.delete 0)).1.native = [] ∧
    (operation (start [0,0] 7 9) (.delete 0)).2 = .deleted true := by decide +kernel

theorem first_occurrences_not_sorted :
    (initialRun ⟨[], []⟩ [2,0,2,1,0]).native = [2,0,1] := by decide +kernel

theorem existing_add_keeps_position :
    (operation (start [1,0] 7 9) (.add 1)).1.native = [1,0] := by decide +kernel

theorem readdition_moves_to_end :
    (history (start [0,1] 7 9) [.delete 0, .add 0]).1.native = [1,0] := by decide +kernel

theorem absent_delete_returns_false :
    (operation (start [0] 7 9) (.delete 1)).2 = .deleted false := by decide +kernel

theorem clear_then_add :
    (history (start [0,1,0] 7 9) [.clear, .add 2]).1.native = [2] := by decide +kernel

theorem case_distinct : firsts [] ([[97],[65],[97]] : List AtomProvider.DOMString) = [[97],[65]] := by
  decide +kernel

theorem folded_provider_changes_ordered_set :
    firsts [] ([0,0] : List Nat) ≠ [0,1] := by decide +kernel

theorem ignored_initialization_failure_breaks_agreement :
    ¬ Good (⟨[0], some [], 7, 9⟩ : State Nat) := by
  intro h
  have := h.2 [] rfl
  contradiction

theorem missing_uniqueness_breaks_delete :
    ([0,0] : List Nat).erase 0 ≠ [0,0].filter (fun a => decide (a ≠ 0)) := by decide +kernel

def world : World Nat := ⟨fun d => if d = 9 then some 7 else some 8,
  fun t => if t = 7 then [0] else [1]⟩
def root : Element := ⟨9, true, true⟩

theorem multiple_query_matches_any :
    nativeMatch world root [2,0] (fun _ => true) = true := by decide +kernel

theorem foreign_document_reads_foreign_types :
    nativeMatch world ⟨10,true,true⟩ [0] (fun _ => true) = false := by decide +kernel

theorem missing_state_blocks_public_member :
    nativeMatch world ⟨9,true,false⟩ [0] (fun _ => true) = false ∧
    specMatch world ⟨9,true,false⟩ [0] = true := by decide +kernel

theorem invalid_query_filter_boundary :
    nativeMatch world root [0] (fun _ => false) = false ∧
    specMatch world root [0] = true := by decide +kernel

theorem nonroot_flag_counterexample :
    nativeMatch world ⟨9,false,true⟩ [0] (fun _ => true) = true ∧
    specMatch world ⟨9,false,true⟩ [0] = false := by decide +kernel

theorem prefix_set_mismatch_breaks_initialization :
    (initialRun (⟨[0], []⟩ : Initial Nat) [0]).native = [] := by decide +kernel

end TypeWitnesses
