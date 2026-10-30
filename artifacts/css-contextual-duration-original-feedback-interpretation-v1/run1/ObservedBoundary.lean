import DurationFeedback

namespace ObservedBoundary
open DurationScheduling DurationFeedback

def observed : State := ⟨1500, 1000, .css⟩

theorem observed_stale_boundary :
    feedbackEvent observed = ⟨.animation, 1500⟩ ∧
    feedbackStep observed = observed ∧ observed ≠ low ∧ observed ≠ high := by decide

theorem observed_not_synchronized : ¬ Synced observed := by
  simp [Synced, observed]

end ObservedBoundary
