import CompletedPrefix
open SelectedDeclaration PreparationStability CompletedPrefix
example : (scan (SizePrefix.eligible false allow) (evaluate (size 20) expr) 0 [rollback, skipped, dynamic]).reads = ["--size"] := by decide
