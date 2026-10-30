import DispatchAttempt
open DispatchAttempt
example : (repeatRequests 2 safeWitness).attempts = 2 := by decide
