import ObserverChallenges
open FlexLineSum IndependentLineSum
theorem wrong : min (1073741823 : Int) (min 1073741823 (1073741823 + 10) - 10) = min (1073741823 : Int) ((1073741823 + 10) - 10) := by decide +kernel
