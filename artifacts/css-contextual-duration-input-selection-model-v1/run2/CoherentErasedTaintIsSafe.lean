import InputSelection
open InputSelection
example : Certified (requiredDuration (taintedInput 2000)) erased := by decide
