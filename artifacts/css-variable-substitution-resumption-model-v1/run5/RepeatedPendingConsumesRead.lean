import Substitution
open SelectedDeclaration PreparationStability SubstitutionResumption
example : (run 20 leftOnly pausedRight).reads = ["left", "right"] := by decide
