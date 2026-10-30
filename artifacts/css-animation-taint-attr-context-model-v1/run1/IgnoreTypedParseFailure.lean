import AttrContext
open AttrContext
example : eval false (.attr false body outer) = some innerValue := by decide
