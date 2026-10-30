import Selection
open SelectedColor
example : selectedCycle [.color, .ident] (primaryOrFallback .light .canvas false) true = false := by decide
