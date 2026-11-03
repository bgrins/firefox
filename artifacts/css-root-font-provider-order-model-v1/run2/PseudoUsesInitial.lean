import Provider
open FontProviderEffects
example : read initialMetrics (initial underlying) .rootPseudo .fontSize .rem = some (.font (.size 16)) := by decide
