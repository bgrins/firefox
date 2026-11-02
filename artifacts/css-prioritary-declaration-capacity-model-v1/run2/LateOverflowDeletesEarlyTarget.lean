import Capacity
open DeclarationCapacity
example : (build 1 0 empty (font :: List.replicate 3 color)).chain = [] := by decide
