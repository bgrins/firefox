import Rollback

namespace RandomIndex.Enclosing

def successfulChunks (entry : State) : List Nat → State
  | [] => entry
  | reads :: rest => successfulChunks (advance entry ⟨reads, true⟩) rest

def compound (guarded : Bool) (entry : State) (chunks : List Nat)
    (accepts : Bool) : Option (List Nat) × State :=
  let parsed := successfulChunks entry chunks
  if accepts then (some (keys entry.count chunks.sum), parsed)
  else (none, if guarded then entry else { parsed with cursor := entry.cursor })

def retry (guarded : Bool) (entry : State) (chunks : List Nat)
    (selectedReads : Nat) : Option (List Nat × State) :=
  select true (compound guarded entry chunks false).2 [⟨selectedReads, true⟩]

theorem successful_chunks_advance (entry : State) (chunks : List Nat) :
    successfulChunks entry chunks =
      ⟨entry.cursor + chunks.sum, entry.count + chunks.sum⟩ := by
  induction chunks generalizing entry with
  | nil => simp [successfulChunks]
  | cons reads rest ih =>
    simp [successfulChunks, ih, advance, Nat.add_assoc]

theorem each_typed_guard_commits (entry : State) (reads : Nat) :
    select true entry [⟨reads, true⟩] =
      some (keys entry.count reads, successfulChunks entry [reads]) := by
  simp [select, successfulChunks]

theorem typed_only_keeps_outer_failure_offset
    (entry : State) (chunks : List Nat) (selectedReads : Nat) :
    retry false entry chunks selectedReads =
      some (keys (entry.count + chunks.sum) selectedReads,
        ⟨entry.cursor + selectedReads, entry.count + chunks.sum + selectedReads⟩) := by
  simp [retry, compound, successful_chunks_advance, select, advance]

theorem outer_guard_preserves_prior_counter
    (entry : State) (chunks : List Nat) (selectedReads : Nat) :
    retry true entry chunks selectedReads =
      select true entry [⟨selectedReads, true⟩] := by
  simp [retry, compound]

theorem accepted_outer_keeps_all_keys (guarded : Bool) (entry : State)
    (chunks : List Nat) :
    compound guarded entry chunks true =
      (some (keys entry.count chunks.sum),
        ⟨entry.cursor + chunks.sum, entry.count + chunks.sum⟩) := by
  simp [compound, successful_chunks_advance]

theorem positive_consumption_changes_selected_state
    (entry : State) (chunks : List Nat) (selectedReads : Nat)
    (positive : 0 < chunks.sum) :
    retry false entry chunks selectedReads ≠ retry true entry chunks selectedReads := by
  rw [typed_only_keeps_outer_failure_offset, outer_guard_preserves_prior_counter]
  simp only [select, Bool.true_eq, ↓reduceIte, advance]
  intro equal
  have counts : entry.count + chunks.sum + selectedReads = entry.count + selectedReads := by
    injection equal with pair
    have states := congrArg Prod.snd pair
    exact congrArg State.count states
  omega

theorem observed_grid_offsets :
    retry false ⟨0, 0⟩ [1] 1 = some ([2], ⟨1, 2⟩) ∧
    retry false ⟨0, 0⟩ [1, 1] 2 = some ([3, 4], ⟨2, 4⟩) ∧
    retry false ⟨0, 0⟩ [1] 2 = some ([2, 3], ⟨2, 3⟩) ∧
    retry true ⟨0, 0⟩ [1, 1] 2 = some ([1, 2], ⟨2, 2⟩) := by decide

end RandomIndex.Enclosing
