import Capacity
open DeclarationCapacity
example : (build 3 0 empty (List.replicate 3 color ++ [font])).chain = [3] := by decide
