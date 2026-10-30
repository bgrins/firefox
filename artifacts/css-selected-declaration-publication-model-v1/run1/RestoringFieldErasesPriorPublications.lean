import Publication
open SelectedDeclaration PreparationStability PreparedPublication
example : (optimized Appearance.none .initial (run [.publish .base, .publish .none] clean)).publications = [.none] := by decide
