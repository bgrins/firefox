import Dag
open Dag
example : observed (run editedDiamond 1 incremental) = [4, 12, 5, 17] := by decide
