import Waves
open EndpointWaves
example : (waves 1 1 double 0 zeroNodes 0).installed.value = 2 := by decide +kernel
