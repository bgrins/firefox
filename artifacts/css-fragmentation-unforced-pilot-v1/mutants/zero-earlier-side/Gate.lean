import Witnesses
open Fragmentation
example : evaluate .strict zeroInput = some (.cut (atA 2)) := by decide
