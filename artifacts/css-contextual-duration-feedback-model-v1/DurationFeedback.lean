import DurationScheduling

namespace DurationFeedback

open DurationScheduling

def low : State := ⟨1000, 1000, .css⟩
def high : State := ⟨1500, 1500, .css⟩

def feedbackEvent (s : State) : Event :=
  ⟨.animation, 1500000 / s.applied⟩

def feedbackStep (s : State) : State := scopedStep s (feedbackEvent s)

def iterate : Nat → State → State
  | 0, s => s
  | n + 1, s => feedbackStep (iterate n s)

def Pair (s : State) : Prop := s = low ∨ s = high

def EventuallyFixed (s : State) : Prop :=
  ∃ n, feedbackStep (iterate n s) = iterate n s

theorem exact_active_branch_arithmetic :
    0 < 750 ∧ 750 < 1000 ∧ 750 < 1500 ∧
    24000 / 1000 = 24 ∧ 24000 % 1000 = 0 ∧
    24000 / 1500 = 16 ∧ 24000 % 1500 = 0 ∧
    1500000 / 1000 = 1500 ∧ 1500000 % 1000 = 0 ∧
    1500000 / 1500 = 1000 ∧ 1500000 % 1500 = 0 ∧
    24000000 / (16 * 1000) = 1500 ∧
    24000000 / (16 * 1500) = 1000 := by decide

theorem exact_two_cycle :
    feedbackStep low = high ∧ feedbackStep high = low ∧ low ≠ high := by decide

theorem iteration_stays_nonfixed (n : Nat) (s : State) (h : Pair s) :
    Pair (iterate n s) ∧ feedbackStep (iterate n s) ≠ iterate n s := by
  have advance : ∀ x, Pair x → Pair (feedbackStep x) ∧ feedbackStep x ≠ x := by
    intro x hx
    rcases hx with rfl | rfl <;> unfold Pair <;> decide
  have invariant : Pair (iterate n s) := by
    induction n with
    | zero => exact h
    | succ n ih => exact (advance (iterate n s) ih).1
  exact ⟨invariant, (advance (iterate n s) invariant).2⟩

theorem pair_never_reaches_fixed_point (s : State) (h : Pair s) :
    ¬ EventuallyFixed s := by
  rintro ⟨n, hn⟩
  exact (iteration_stays_nonfixed n s h).2 hn

theorem fixed_input_idempotence_does_not_close_feedback :
    scopedStep (scopedStep low (feedbackEvent low)) (feedbackEvent low) =
      scopedStep low (feedbackEvent low) ∧
    feedbackStep (feedbackStep low) ≠ feedbackStep low := by
  constructor
  · exact scoped_fixed_input_idempotent low (feedbackEvent low)
  · decide

instance : Decidable (EventuallyFixed low) :=
  isFalse (pair_never_reaches_fixed_point low (Or.inl rfl))

end DurationFeedback
