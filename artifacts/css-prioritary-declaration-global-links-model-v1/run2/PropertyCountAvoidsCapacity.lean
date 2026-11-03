import GlobalLinks
open GlobalDeclarationLinks
example : DeclarationLinks.read 2 (view (build testMapping 2 (empty 2) [b, unrelated, a]) 0) = [2] := by decide
