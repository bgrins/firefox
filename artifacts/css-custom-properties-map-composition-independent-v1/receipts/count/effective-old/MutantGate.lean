import Mutant
open LiveCount
example : (trialInsert ⟨[[],[(0,some "x")]],1⟩ 0 none).stored = 0 := by decide
