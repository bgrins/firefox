import Substitution
open SelectedDeclaration PreparationStability SubstitutionResumption
example : (run 10 env (start fallback)).reads = ["right"] := by decide
