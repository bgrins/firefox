import Rollback
open RandomIndex
example : keys 0 2 = keys 0 1 ++ keys 0 1 := by decide
