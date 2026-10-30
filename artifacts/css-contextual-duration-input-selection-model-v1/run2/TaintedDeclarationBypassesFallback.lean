import InputSelection
open InputSelection
example : requiredDuration (taintedInput 1000) = 1000 := by decide
