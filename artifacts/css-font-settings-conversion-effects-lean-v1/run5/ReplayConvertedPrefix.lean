import Settings
open FontSettingsEffects
example : effects (run [secondPending, waiting, complete] ⟨[], [a, b]⟩).done = [7, 20, 7, 20, 7, 30] := by decide
