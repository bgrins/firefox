import Witness

namespace FlexViolationCaller

theorem joint_target : JointTarget := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · rcases two_pass_joint with ⟨ha, hh, he, hf, hi, hc, hm, hb1, hb2, hr, hfr⟩
    exact ⟨ha, firstPass, secondPass, finalState, he, hh, hf, hi, hc, hm, hb1, hb2, hr, hfr⟩
  · constructor
    · simp [SeedsValid, earlySeeds, normalSeed, strutSeed, SeedValid, FieldsValid,
        FlexViolation.Fits32, FlexViolation.min32, FlexViolation.max32, FlexViolation.maxCount]
    · decide
  · refine ⟨?_, by decide, by decide, ?_⟩
    · simp [SeedsValid, strutSeed, SeedValid, FieldsValid, FlexViolation.Fits32,
        FlexViolation.min32, FlexViolation.max32, FlexViolation.maxCount]
    · refine ⟨(runPass 0 (start [strutSeed 0] true true).line [123]).getD emptyPass,
        by decide, by decide, by decide, by decide⟩
  · decide

end FlexViolationCaller
