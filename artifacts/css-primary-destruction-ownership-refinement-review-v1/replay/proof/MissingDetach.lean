import BoundaryMutants
open Destruction Destruction.Ownership

example : noDetach 0 = some (.frame 1 true emptyTable) := by decide
