import UnitFallback
open UnitFallback
example : dependency .substituted (some (.px 20)) (.em 1) = dependency .lexicalInventory (some (.px 20)) (.em 1) := by decide
