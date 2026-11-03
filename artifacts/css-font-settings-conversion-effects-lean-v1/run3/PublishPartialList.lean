import Settings
open FontSettingsEffects
example : (publish (poll complete ⟨[], [a, b]⟩)).isSome = true := by decide
