import BoundaryMutants
open Destruction Destruction.Ownership

example : nestedAfter 30 = some (.allocation .itemCache) := by decide
