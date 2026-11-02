import Substitution
open SelectedDeclaration PreparationStability SubstitutionResumption
example : (run 4 (CompletedPrefix.complete env "alias" (some [30])) ⟨.await "alias" none, [.right [20]], ["left"]⟩).control = .value (some [20]) := by decide
