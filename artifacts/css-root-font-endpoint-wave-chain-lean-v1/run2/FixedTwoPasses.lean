import Waves
open EndpointWaves
example : (waves 4 1 double 2 zeroNodes 3).installed.value = expected 1 double 3 := by decide +kernel
