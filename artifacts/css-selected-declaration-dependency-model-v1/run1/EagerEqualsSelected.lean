import Selection
open SelectedDeclaration
example : eager [0, 1] = (scan (fun _ _ => true) direct () [0, 1]).reads := by decide
