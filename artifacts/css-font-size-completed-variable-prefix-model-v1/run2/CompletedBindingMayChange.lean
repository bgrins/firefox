import CompletedPrefix
open SelectedDeclaration PreparationStability CompletedPrefix
example : (scan (SizePrefix.eligible false allow) (evaluate (size 20) expr) 0 [dynamic]).finish = (scan (SizePrefix.eligible false allow) (evaluate (size 30) expr) 0 [dynamic]).finish := by decide
