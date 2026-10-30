import AttrContext
open AttrContext
example : eval false (.attr false body outer) = some (markAttr innerValue) := by decide
