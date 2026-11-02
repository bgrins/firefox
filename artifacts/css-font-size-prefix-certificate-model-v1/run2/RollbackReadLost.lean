import Prefix
open SelectedDeclaration PreparationStability SizePrefix
example : (scan (eligible false allow) (evaluate oldDynamic) 0 [rollback, winner 8, winner 20]).reads = [20] := by decide
