import MathMLRectObservation
open MathMLRectObservation

theorem correct_post_state_makes_old_observation_correct :
    (observeBefore marked .leaf).map Prod.snd = some expectedRect := by
  simp only [marked_eq]
  decide
