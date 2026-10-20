import IndependentChallenges
open IndependentReview StickyAdmission StickyJoined
theorem wrong : (machineRun true rootChain).2.trace = #["subtree:-1", "order:0", "normal:0:0", "flush"] := by decide +kernel
