import MaskedBaseInput

namespace SnapshotLifecycle

open MaskedBaseInput (Owner)

structure Collection (Key : Type) where
  sampled : Option Key
  applied : Nat
  owner : Owner
  deriving DecidableEq, Repr

inductive Reason | full | verify
  deriving DecidableEq, Repr

structure Outcome where
  survives : Bool
  reusesEffect : Bool
  deriving DecidableEq, Repr

def dispatch {K : Type} [DecidableEq K]
    (state : Option (Collection K)) (reason : Reason) (key : K) : Bool :=
  match reason, state with
  | .full, _ => true
  | .verify, none => false
  | .verify, some old => decide (old.sampled ≠ some key)

def commit {K : Type} (state : Option (Collection K)) (key : K)
    (composedDuration : Nat) (outcome : Outcome) : Option (Collection K) :=
  if outcome.survives then
    match state with
    | some old =>
      if outcome.reusesEffect && decide (old.owner = .script) then
        some { old with sampled := some key }
      else some ⟨some key, composedDuration, .css⟩
    | none => some ⟨some key, composedDuration, .css⟩
  else none

def step {K : Type} [DecidableEq K] (state : Option (Collection K))
    (reason : Reason) (key : K) (composedDuration : Nat) (outcome : Outcome) :=
  if dispatch state reason key then commit state key composedDuration outcome else state

theorem verify_absence_cannot_create {K : Type} [DecidableEq K]
    (key : K) (duration : Nat) (outcome : Outcome) :
    step none .verify key duration outcome = none := by
  simp [step, dispatch]

theorem unknown_snapshot_dispatches {K : Type} [DecidableEq K]
    (old : Collection K) (key : K) (unknown : old.sampled = none) :
    dispatch (some old) .verify key = true := by
  simp [dispatch, unknown]

theorem equal_verification_preserves_every_field {K : Type} [DecidableEq K]
    (old : Collection K) (key : K) (duration : Nat) (outcome : Outcome)
    (equal : old.sampled = some key) :
    step (some old) .verify key duration outcome = some old := by
  simp [step, dispatch, equal]

theorem skipped_existing_verification_requires_known_equal_input
    {K : Type} [DecidableEq K] (old : Collection K) (key : K)
    (skipped : dispatch (some old) .verify key = false) :
    old.sampled = some key := by
  simpa [dispatch] using skipped

theorem full_reason_always_dispatches {K : Type} [DecidableEq K]
    (state : Option (Collection K)) (key : K) :
    dispatch state .full key = true := by
  rfl

theorem surviving_commit_seeds_input {K : Type}
    (state : Option (Collection K)) (key : K) (duration : Nat) (outcome : Outcome)
    (survives : outcome.survives = true) :
    (commit state key duration outcome).bind Collection.sampled = some key := by
  cases state with
  | none => simp [commit, survives]
  | some old =>
    simp only [commit, survives, Bool.true_eq, ↓reduceIte]
    split <;> rfl

theorem admitted_surviving_step_seeds_input {K : Type} [DecidableEq K]
    (state : Option (Collection K)) (reason : Reason) (key : K)
    (duration : Nat) (outcome : Outcome)
    (admitted : dispatch state reason key = true)
    (survives : outcome.survives = true) :
    (step state reason key duration outcome).bind Collection.sampled = some key := by
  simpa [step, admitted] using surviving_commit_seeds_input state key duration outcome survives

theorem cancellation_erases_collection {K : Type}
    (state : Option (Collection K)) (key : K) (duration : Nat) (reuse : Bool) :
    commit state key duration ⟨false, reuse⟩ = none := by
  rfl

theorem recreation_cannot_inherit_old_cache_or_override {K : Type} [DecidableEq K]
    (state : Option (Collection K)) (oldKey newKey : K)
    (oldDuration newDuration : Nat) (reuse : Bool) :
    step (commit state oldKey oldDuration ⟨false, reuse⟩)
      .full newKey newDuration ⟨true, true⟩ =
      some ⟨some newKey, newDuration, .css⟩ := by
  rfl

theorem retained_script_effect_preserves_override {K : Type}
    (old : Collection K) (key : K) (duration : Nat)
    (script : old.owner = .script) :
    commit (some old) key duration ⟨true, true⟩ =
      some { old with sampled := some key } := by
  simp [commit, script]

theorem concrete_full_update_wins_over_equal_key :
    step (some (⟨some 1000, 1000, .css⟩ : Collection Nat))
      .full 1000 2000 ⟨true, true⟩ = some ⟨some 1000, 2000, .css⟩ := by decide

theorem fresh_cache_does_not_certify_applied_base_duration :
    commit (some (⟨none, 750, .css⟩ : Collection Nat)) 1000 2000 ⟨true, true⟩ =
      some ⟨some 1000, 2000, .css⟩ ∧ (1000 : Nat) ≠ 2000 := by decide

theorem replacement_is_not_script_preservation :
    commit (some (⟨some 1000, 1250, .script⟩ : Collection Nat))
      2000 2000 ⟨true, false⟩ = some ⟨some 2000, 2000, .css⟩ := by decide

end SnapshotLifecycle
