import Substitution
open SelectedDeclaration PreparationStability SubstitutionResumption
example : (match tick (fun _ => none) (run (rank (start fallback) + 1) (fun _ => none) (start fallback)) with | .done _ => true | _ => false) = true := by decide
