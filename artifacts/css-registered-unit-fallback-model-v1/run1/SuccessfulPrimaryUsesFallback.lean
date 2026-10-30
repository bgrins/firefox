import UnitFallback
open UnitFallback
example : select (some (.px 20)) (.em 1) = .em 1 := by decide
