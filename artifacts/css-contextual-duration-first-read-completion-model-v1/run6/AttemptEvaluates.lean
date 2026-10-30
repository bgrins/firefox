import Completion
open Completion
example : (attemptKey (initial 1 .absent) 1).value 1 = true := by decide
