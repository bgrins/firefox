import Completion
open Completion
example : (round 2 (initial 2 .absent)).queued 2 = .absent := by decide
