import Substitution
open SelectedDeclaration PreparationStability SubstitutionResumption
example : ∃ tokens, tick (fun _ => none) (run (rank (start fallback) + 1) (fun _ => none) (start fallback)) = .done tokens := by decide
