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

def signed32Projection (value : Int) : Int :=
  max FlexViolation.min32 (min FlexViolation.max32 value)

theorem representable_target_reporting (base delta : Int)
    (hb : FlexViolation.Fits32 base) (ht : FlexViolation.Fits32 (base + delta)) :
    signed32Projection (base + delta) = base + delta ∧
    signed32Projection (base + delta) - base = delta ∧ FlexViolation.Fits64 delta := by
  simp only [FlexViolation.Fits32, FlexViolation.min32, FlexViolation.max32] at hb ht
  simp only [signed32Projection, FlexViolation.min32, FlexViolation.max32,
    FlexViolation.Fits64, FlexViolation.min64, FlexViolation.max64]
  omega

theorem outside32_aggregate_sign :
    FlexViolation.total [⟨0,-3100000000,0,0⟩,⟨1,1500000000,0,0⟩,⟨2,1500000000,0,0⟩] = 100000000 ∧
    FlexViolation.total [⟨0,signed32Projection (-3100000000),0,0⟩,
      ⟨1,1500000000,0,0⟩,⟨2,1500000000,0,0⟩] = -852516352 := by
  decide

end FlexViolationCaller
