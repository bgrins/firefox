import Witnesses
open Fragmentation
example :
    rules .strict {page := true} [] { (atA 1) with controls := [.avoidColumn] } = true ∧
    rules .strict {page := true, column := true} []
      { (atA 1) with controls := [.avoidColumn] } = false := by decide
