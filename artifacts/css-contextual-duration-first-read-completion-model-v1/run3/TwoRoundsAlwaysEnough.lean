import Completion
open Completion
example : (run 3 2 (initial 3 .absent)).value 3 = true := by decide
