import ObserverChallenges
open FlexLineSum IndependentLineSum
theorem wrong : applyBounds none none (accumulate 0 [720000000, 720000000]) = 1440000000 := by decide +kernel
