import Substitution
open SelectedDeclaration PreparationStability SubstitutionResumption
example : (run 6 env pausedRight).control = .value (some [30]) := by decide
