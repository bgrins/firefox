import Witnesses
open Fragmentation
example :
    rules .strict three.types three.content (atA 2) = true ∧
    evaluate .strict {three with capacity := 1, opportunities := [atA 2]} = none := by decide
