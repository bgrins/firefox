import Waves
open EndpointWaves
example : (waves 3 2 double 1 (waves 3 1 double 3 zeroNodes) 2).installed.value = 16 := by decide +kernel
