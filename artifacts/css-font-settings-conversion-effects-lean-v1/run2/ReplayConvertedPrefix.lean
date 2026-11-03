import Settings
open FontSettingsEffects
example : effects (run [secondPending, waiting, complete] ⟨[], [a, b]⟩).done = [7, 7, 9] := by decide
