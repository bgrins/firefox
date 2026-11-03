import Waves
open EndpointWaves
example : (waves 2 1 double 1 zeroNodes 1).installed.value = 4 := by decide +kernel
