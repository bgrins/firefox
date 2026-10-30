import AttrContext
open AttrContext
example : eval false (.ref direct outer) = some (markAttr innerValue) := by decide
