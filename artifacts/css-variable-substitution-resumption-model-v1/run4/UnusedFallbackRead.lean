import Substitution
open SelectedDeclaration PreparationStability SubstitutionResumption
example : (run 10 env (start (.fallback "left" (.reference "unknown")))).reads = ["left", "unknown"] := by decide
