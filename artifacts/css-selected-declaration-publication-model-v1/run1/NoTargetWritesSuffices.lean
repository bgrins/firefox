import Publication
open SelectedDeclaration PreparationStability PreparedPublication
example : (optimized Appearance.none (.literal .base) (run [.observe] clean)).observations = (step .observe (optimized Appearance.none (.literal .base) clean)).observations := by decide
