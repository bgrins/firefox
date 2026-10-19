import Std

namespace WorkerRebuild

def add (xs : List Nat) (e : Nat) : List Nat :=
  if xs.getLast? = some e then xs else xs ++ [e]

def accumulate (xs entries : List Nat) : List Nat := entries.foldl add xs

def lastMatch (p : Nat → Bool) (xs : List Nat) : Option Nat :=
  xs.reverse.find? p

theorem mem_add (xs : List Nat) (e x : Nat) :
    x ∈ add xs e ↔ x ∈ xs ∨ x = e := by
  unfold add
  split
  next h =>
    constructor
    · exact Or.inl
    · intro h'
      rcases h' with h' | rfl
      · exact h'
      · exact List.mem_of_getLast? h
  next => simp

theorem mem_accumulate (entries xs : List Nat) (x : Nat) :
    x ∈ accumulate xs entries ↔ x ∈ xs ∨ x ∈ entries := by
  induction entries generalizing xs with
  | nil => simp [accumulate]
  | cons e es ih =>
    simpa [accumulate, List.foldl_cons, mem_add, or_assoc, or_left_comm,
      or_comm] using ih (add xs e)

theorem lastMatch_add (p : Nat → Bool) (xs : List Nat) (e : Nat) :
    lastMatch p (add xs e) = if p e then some e else lastMatch p xs := by
  unfold add
  split
  next h =>
    obtain ⟨ys, rfl⟩ := List.getLast?_eq_some_iff.mp h
    cases hp : p e <;> simp [lastMatch, hp]
  next => cases hp : p e <;> simp [lastMatch, hp]

def referenceLast (p : Nat → Bool) (initial : Option Nat)
    (entries : List Nat) : Option Nat :=
  entries.foldl (fun previous e => if p e then some e else previous) initial

theorem lastMatch_accumulate (p : Nat → Bool) (entries xs : List Nat) :
    lastMatch p (accumulate xs entries) =
      referenceLast p (lastMatch p xs) entries := by
  induction entries generalizing xs with
  | nil => rfl
  | cons e es ih =>
    simpa [accumulate, referenceLast, lastMatch_add] using ih (add xs e)

abbrev Store := Nat → List Nat
abbrev Admission := Nat → Option (Nat × Nat)

def insert (a : Admission) (s : Store) (face : Nat) : Store :=
  match a face with
  | none => s
  | some (family, entry) => fun q => if q = family then add (s q) entry else s q

def projected (a : Admission) (family : Nat) (faces : List Nat) : List Nat :=
  faces.filterMap fun f => match a f with
    | none => none
    | some (g, e) => if family = g then some e else none

def rebuild (a : Admission) (faces : List Nat) : Store :=
  faces.foldl (insert a) (fun _ => [])

theorem project_fold (a : Admission) (family : Nat) (faces : List Nat) (s : Store) :
    faces.foldl (insert a) s family = accumulate (s family) (projected a family faces) := by
  induction faces generalizing s with
  | nil => rfl
  | cons f fs ih =>
    simp only [List.foldl_cons]
    rw [ih]
    cases h : a f with
    | none => simp [insert, h, projected]
    | some v =>
      rcases v with ⟨g,e⟩
      by_cases hg : family = g
      · simp [insert, h, projected, hg, accumulate]
      · simp [insert, h, projected, hg]

theorem exact_rebuild (a : Admission) (family : Nat) (faces : List Nat) :
    rebuild a faces family = accumulate [] (projected a family faces) :=
  project_fold a family faces (fun _ => [])

theorem rebuild_membership (a : Admission) (family entry : Nat) (faces : List Nat) :
    entry ∈ rebuild a faces family ↔ entry ∈ projected a family faces := by
  rw [exact_rebuild, mem_accumulate]
  simp

theorem removed_unshared_absent (a : Admission) (family entry : Nat)
    (remaining : List Nat) (h : entry ∉ projected a family remaining) :
    entry ∉ rebuild a remaining family := by
  simpa [rebuild_membership] using h

theorem shared_entry_preserved (a : Admission) (family entry : Nat)
    (remaining : List Nat) (h : entry ∈ projected a family remaining) :
    entry ∈ rebuild a remaining family := by
  exact (rebuild_membership a family entry remaining).mpr h

theorem last_matching_preserved (a : Admission) (family : Nat)
    (faces : List Nat) (p : Nat → Bool) :
    lastMatch p (rebuild a faces family) =
      referenceLast p none (projected a family faces) := by
  rw [exact_rebuild, lastMatch_accumulate]
  rfl

def candidate (_old : Store) (a : Admission) (faces : List Nat) : Store := rebuild a faces

theorem old_history_irrelevant (old₁ old₂ : Store) (a : Admission) (faces : List Nat) :
    candidate old₁ a faces = candidate old₂ a faces := rfl

theorem clear_empty (old : Store) (a : Admission) (family : Nat) :
    candidate old a [] family = [] := rfl

theorem repeat_rebuild (old : Store) (a : Admission) (faces : List Nat) :
    candidate (candidate old a faces) a faces = candidate old a faces := rfl

theorem adjacent_dedup : accumulate [] [0,0] = [0] := by decide
theorem nonadjacent_preserved : accumulate [] [0,1,0] = [0,1,0] := by decide
theorem original_clear_stale : accumulate [1] [] = [1] ∧ accumulate [] [] = [] := by decide
theorem original_delete_stale : accumulate [0,1] [0] = [0,1,0] ∧
    accumulate [] [0] = [0] := by decide
theorem shared_face_control : rebuild (fun _ => some (0,7)) [1] 0 = [7] := by decide

end WorkerRebuild

#print axioms WorkerRebuild.mem_add
#print axioms WorkerRebuild.mem_accumulate
#print axioms WorkerRebuild.lastMatch_add
#print axioms WorkerRebuild.lastMatch_accumulate
#print axioms WorkerRebuild.project_fold
#print axioms WorkerRebuild.exact_rebuild
#print axioms WorkerRebuild.rebuild_membership
#print axioms WorkerRebuild.removed_unshared_absent
#print axioms WorkerRebuild.shared_entry_preserved
#print axioms WorkerRebuild.last_matching_preserved
#print axioms WorkerRebuild.old_history_irrelevant
#print axioms WorkerRebuild.clear_empty
#print axioms WorkerRebuild.repeat_rebuild
#print axioms WorkerRebuild.adjacent_dedup
#print axioms WorkerRebuild.nonadjacent_preserved
#print axioms WorkerRebuild.original_clear_stale
#print axioms WorkerRebuild.original_delete_stale
#print axioms WorkerRebuild.shared_face_control
