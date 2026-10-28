namespace SuspensionOwnership
structure State where
  suspendedBy : Option Nat
  deriving DecidableEq, Repr
inductive Outcome where
  | running | demand
  deriving DecidableEq, Repr

def unownedResume (_continuation : Nat) (_s : State) : Outcome × State :=
  (.running, ⟨none⟩)

def release (continuation : Nat) (s : State) : State :=
  if s.suspendedBy = some continuation then ⟨none⟩ else s

def resume (continuation : Nat) (s : State) : Outcome × State :=
  match s.suspendedBy with
  | none => (.running, s)
  | some owner => if owner = continuation then (.running, release continuation s)
      else (.demand, s)

theorem foreign_release_preserves (owner other : Nat) (different : owner ≠ other) :
    release other ⟨some owner⟩ = ⟨some owner⟩ := by simp [release, different]

theorem only_owner_can_clear (s : State) (me owner : Nat)
    (held : s.suspendedBy = some owner)
    (cleared : (release me s).suspendedBy = none) : me = owner := by
  unfold release at cleared
  split at cleared
  next same => rw [held] at same; exact (Option.some.inj same).symm
  next => rw [held] at cleared; contradiction

theorem foreign_resume_demands (owner other : Nat) (different : owner ≠ other) :
    resume other ⟨some owner⟩ = (.demand, ⟨some owner⟩) := by simp [resume, different]

theorem owning_resume_can_retry (owner : Nat) :
    resume owner ⟨some owner⟩ = (.running, ⟨none⟩) := by simp [resume, release]

theorem unowned_clear_bypasses_marker :
    unownedResume 2 ⟨some 1⟩ = (.running, ⟨none⟩) ∧
    resume 2 ⟨some 1⟩ = (.demand, ⟨some 1⟩) := by decide +kernel

theorem fresh_drop_preserves_outer : release 2 ⟨some 1⟩ = ⟨some 1⟩ := by decide +kernel
end SuspensionOwnership
