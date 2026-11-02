import Capacity
open DeclarationCapacity
example : (build 2 0 empty [color, color, font]).chain.length = (build 2 0 empty [font]).chain.length := by decide
