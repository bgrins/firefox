import Settings
open FontSettingsEffects
example : (publish (poll waiting ⟨[], [a]⟩)).isSome = true := by decide
