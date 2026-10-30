import AttrContext
open AttrContext
example : eval false (.ref direct outer) = some innerValue := by decide
