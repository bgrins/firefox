import BoundaryMutants
open Destruction Destruction.Ownership

example : (removeAll aliasAfter 2).isSome = true := by decide
