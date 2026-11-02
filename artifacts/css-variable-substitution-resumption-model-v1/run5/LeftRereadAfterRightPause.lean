import Substitution
open SelectedDeclaration PreparationStability SubstitutionResumption
example : (run 6 env pausedRight).reads = ["left", "left", "right"] := by decide
