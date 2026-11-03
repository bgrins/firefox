import Waves
open EndpointWaves
example : EndpointApplication.ready (waves 3 1 double 2 zeroNodes 2) → (waves 3 1 double 2 zeroNodes 2).installed.value = expected 1 double 2 := by decide +kernel
