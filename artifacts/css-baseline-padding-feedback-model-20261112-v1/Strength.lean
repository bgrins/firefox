import Lean.Elab.Tactic.Omega

namespace BaselineFeedback

structure State where
  raw : Int
  adjustment : Int
  used : Int
  deriving DecidableEq, Repr

inductive Event where
  | parent (raw adjustment : Int)
  | child
  deriving DecidableEq, Repr

def consistent (s : State) : Prop := s.used = s.raw + s.adjustment

def parent (raw adjustment : Int) : State := ⟨raw, adjustment, raw + adjustment⟩

def step (s : State) : Event → State
  | .parent raw adjustment => parent raw adjustment
  | .child => s

def oldStep (s : State) : Event → State
  | .parent raw adjustment => parent raw adjustment
  | .child => { s with used := s.used + s.adjustment }

def run (s : State) (events : List Event) : State := events.foldl step s

def oldRun (s : State) (events : List Event) : State := events.foldl oldStep s

structure Obligations : Prop where
  parent_consistent : ∀ raw adjustment, consistent (parent raw adjustment)
  step_consistent : ∀ s event, consistent s → consistent (step s event)
  history_consistent : ∀ s events, consistent s → consistent (run s events)
  repeated_child : ∀ s n, run s (List.replicate n .child) = s
  old_repeated_child : ∀ s n,
    (oldRun s (List.replicate n .child)).used = s.used + (n : Int) * s.adjustment
  old_nonzero_drift : ∀ raw adjustment, adjustment ≠ 0 →
    ¬ consistent (oldStep (parent raw adjustment) .child)
  reset_independent : ∀ s t raw adjustment events,
    run s (.parent raw adjustment :: events) = run t (.parent raw adjustment :: events)
  zero_adjustment_control : ∀ raw n,
    oldRun (parent raw 0) (List.replicate n .child) = parent raw 0
  concrete_old_witness : consistent (parent 3 18) ∧
    (oldRun (parent 3 18) [.child, .child]).used = 57 ∧
    ¬ consistent (oldRun (parent 3 18) [.child, .child])
  concrete_fixed_witness :
    (run (parent 3 18) [.child, .child]).used = 21 ∧
    (run (parent 3 18) [.child, .parent 4 8, .child]).used = 12

end BaselineFeedback


namespace BaselineFeedback

theorem parent_consistent (raw adjustment : Int) :
    consistent (parent raw adjustment) := rfl

theorem step_consistent (s : State) (event : Event) (h : consistent s) :
    consistent (step s event) := by
  cases event with
  | parent raw adjustment => exact parent_consistent raw adjustment
  | child => exact h

theorem history_consistent (s : State) (events : List Event) (h : consistent s) :
    consistent (run s events) := by
  induction events generalizing s with
  | nil => exact h
  | cons event events ih =>
    exact ih (step s event) (step_consistent s event h)

theorem repeated_child (s : State) (n : Nat) :
    run s (List.replicate n .child) = s := by
  induction n with
  | zero => rfl
  | succ n ih => simpa [run, List.replicate_succ, step] using ih

theorem old_repeated_child (s : State) (n : Nat) :
    (oldRun s (List.replicate n .child)).used = s.used + (n : Int) * s.adjustment := by
  induction n generalizing s with
  | zero => simp [oldRun]
  | succ n ih =>
    simp only [List.replicate_succ, oldRun, List.foldl_cons]
    change (oldRun (oldStep s .child) (List.replicate n .child)).used = _
    rw [ih]
    simp [oldStep, Int.add_mul]
    omega

theorem old_nonzero_drift (raw adjustment : Int) (h : adjustment ≠ 0) :
    ¬ consistent (oldStep (parent raw adjustment) .child) := by
  simp only [consistent, oldStep, parent]
  omega

theorem reset_independent (s t : State) (raw adjustment : Int) (events : List Event) :
    run s (.parent raw adjustment :: events) =
      run t (.parent raw adjustment :: events) := rfl

theorem zero_adjustment_control (raw : Int) (n : Nat) :
    oldRun (parent raw 0) (List.replicate n .child) = parent raw 0 := by
  induction n with
  | zero => rfl
  | succ n ih => simpa [oldRun, List.replicate_succ, oldStep, parent] using ih

theorem concrete_old_witness : consistent (parent 3 18) ∧
    (oldRun (parent 3 18) [.child, .child]).used = 57 ∧
    ¬ consistent (oldRun (parent 3 18) [.child, .child]) := by
  unfold consistent
  decide

theorem concrete_fixed_witness :
    (run (parent 3 18) [.child, .child]).used = 21 ∧
    (run (parent 3 18) [.child, .parent 4 8, .child]).used = 12 := by decide

theorem obligations : Obligations where
  parent_consistent := parent_consistent
  step_consistent := step_consistent
  history_consistent := history_consistent
  repeated_child := repeated_child
  old_repeated_child := old_repeated_child
  old_nonzero_drift := old_nonzero_drift
  reset_independent := reset_independent
  zero_adjustment_control := zero_adjustment_control
  concrete_old_witness := concrete_old_witness
  concrete_fixed_witness := concrete_fixed_witness

end BaselineFeedback

#print axioms BaselineFeedback.parent_consistent
#print axioms BaselineFeedback.step_consistent
#print axioms BaselineFeedback.history_consistent
#print axioms BaselineFeedback.repeated_child
#print axioms BaselineFeedback.old_repeated_child
#print axioms BaselineFeedback.old_nonzero_drift
#print axioms BaselineFeedback.reset_independent
#print axioms BaselineFeedback.zero_adjustment_control
#print axioms BaselineFeedback.concrete_old_witness
#print axioms BaselineFeedback.concrete_fixed_witness
#print axioms BaselineFeedback.obligations
