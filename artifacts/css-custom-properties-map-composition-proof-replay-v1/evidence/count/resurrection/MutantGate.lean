import Mutant
open LiveCount
example : (trialInsert ⟨[[(0,none)]],0⟩ 0 (some "x")).stored = 1 := by decide
