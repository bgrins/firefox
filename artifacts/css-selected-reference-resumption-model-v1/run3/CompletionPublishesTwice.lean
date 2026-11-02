import Resumption
open SelectedDeclaration PreparationStability SelectedResumption
example : (publish (publish completedPublication)).values = [some 700, some 700] := by decide
