import IndependentChallenges
open IndependentReview StickyAdmission StickyJoined
theorem wrong : (machineRun true refreshedCase).2.nodes[1]!.current = ⟨20, 7⟩ := by decide +kernel
