import DispatchAttempt
open DispatchAttempt
example : (request safeWitness).timingVersion = safeWitness.timingVersion + 1 := by decide
