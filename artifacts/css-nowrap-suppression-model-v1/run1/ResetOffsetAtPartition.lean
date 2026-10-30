import Suppression
open NowrapSuppression
example : helper 0 false true 0 ([1] ++ [2]) = helper 0 false true 0 [1] ++ helper 0 false true 0 [2] := by decide
