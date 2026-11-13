import FlexViolationCaller.Target

namespace FlexViolationCaller

theorem measured_base_counterexample :
    FlexViolation.Fits32 1800000000 ∧ preferredMax < 1800000000 ∧
    FlexViolation.clamped ⟨0, 1800000000 + boundedDelta (60000 - 1800000000), 0, preferredMax⟩ =
      726258177 ∧
    FlexViolation.clamped ⟨0, 1800000000 + (60000 - 1800000000), 0, preferredMax⟩ = 60000 ∧
    FlexViolation.clamped ⟨0, 1800000000 + boundedDelta (60000 - 1800000000), 0, preferredMax⟩ ≠
      FlexViolation.clamped ⟨0, 1800000000 + (60000 - 1800000000), 0, preferredMax⟩ := by
  unfold FlexViolation.Fits32
  decide

end FlexViolationCaller
