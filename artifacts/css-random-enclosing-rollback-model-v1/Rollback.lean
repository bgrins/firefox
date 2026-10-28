import Lean

namespace RandomIndex

structure State where
  cursor : Nat
  count : Nat
  deriving DecidableEq, Repr

structure Attempt where
  reads : Nat
  accepts : Bool
  deriving DecidableEq, Repr

def keys (count reads : Nat) : List Nat :=
  (List.range reads).map (fun offset => count + offset + 1)

def advance (state : State) (attempt : Attempt) : State :=
  ⟨state.cursor + attempt.reads, state.count + attempt.reads⟩

def select (transactional : Bool) (state : State) : List Attempt → Option (List Nat × State)
  | [] => none
  | attempt :: rest =>
    let next := advance state attempt
    if attempt.accepts then some (keys state.count attempt.reads, next)
    else select transactional (if transactional then state else { next with cursor := state.cursor }) rest

theorem failed_rejected_neutral (state : State) (rejected rest : List Attempt)
    (failed : ∀ a ∈ rejected, a.accepts = false) :
    select true state (rejected ++ rest) = select true state rest := by
  induction rejected with
  | nil => rfl
  | cons a tail ih =>
    have ha : a.accepts = false := failed a (by simp)
    simp only [List.cons_append, select, ha, Bool.false_eq_true, ↓reduceIte]
    exact ih (fun b hb => failed b (by simp [hb]))

theorem selected_stops (transactional : Bool) (state : State) (reads : Nat)
    (rest : List Attempt) :
    select transactional state (⟨reads, true⟩ :: rest) =
      some (keys state.count reads, advance state ⟨reads, true⟩) := by
  simp [select]

theorem failed_scalar_changes_selected_key :
    select false ⟨0, 0⟩ [⟨1, false⟩, ⟨1, true⟩] = some ([2], ⟨1, 2⟩) ∧
    select true ⟨0, 0⟩ [⟨1, false⟩, ⟨1, true⟩] = some ([1], ⟨1, 1⟩) := by decide

theorem failed_list_changes_selected_keys :
    select false ⟨0, 0⟩ [⟨1, false⟩, ⟨2, true⟩] = some ([2, 3], ⟨2, 3⟩) ∧
    select true ⟨0, 0⟩ [⟨1, false⟩, ⟨2, true⟩] = some ([1, 2], ⟨2, 2⟩) := by decide

theorem cursor_equality_insufficient :
    (advance ⟨0, 1⟩ ⟨1, true⟩).cursor = (advance ⟨0, 0⟩ ⟨1, true⟩).cursor ∧
    keys 1 1 ≠ keys 0 1 := by decide

end RandomIndex
