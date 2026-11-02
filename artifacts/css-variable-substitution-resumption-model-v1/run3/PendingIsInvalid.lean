import Substitution
open SelectedDeclaration PreparationStability SubstitutionResumption
example : run 20 (fun _ => none) (start fallback) = ⟨.value none, [], []⟩ := by decide
