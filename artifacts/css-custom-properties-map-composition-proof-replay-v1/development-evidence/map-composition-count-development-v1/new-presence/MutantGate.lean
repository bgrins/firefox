import Mutant
open LiveCount
example : (trialInsert ⟨[[]],0⟩ 0 (some "")).stored = 1 := by decide
