import Waves
open EndpointWaves
example : (wave 1 1 double zeroNodes 1).installed.value = 2 := by decide +kernel
