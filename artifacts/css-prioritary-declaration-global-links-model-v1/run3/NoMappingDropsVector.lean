import GlobalLinks
open GlobalDeclarationLinks
example : (build testMapping 8 (empty 8) [a, unrelated, b]).vector = [a, b] := by decide
