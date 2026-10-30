import Selection
open SelectedDeclaration
example : (scan allowed evaluate 0 [0, 1, 2]).reads = ["--missing", "--fallback"] := by decide
