import Witnesses
open Fragmentation
example :
    rules .strict three.types three.content
      { (atA 1) with commonAncestors := [.avoid] } = false ∧
    rules .strict three.types three.content
      { (atA 1) with controls := [.avoidColumn], commonAncestors := [.avoid] } = true := by decide
