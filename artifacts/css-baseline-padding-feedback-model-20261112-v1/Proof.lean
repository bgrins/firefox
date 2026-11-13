import Target

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
