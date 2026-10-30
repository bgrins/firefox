import Selection
open SelectedDeclaration
example : "--unused" ∈ (scan allowed evaluate 0 [0, 1, 2]).reads := by decide
