import Completion
open Completion
example : (discard (initial 1 .absent)).value 1 = true := by decide
