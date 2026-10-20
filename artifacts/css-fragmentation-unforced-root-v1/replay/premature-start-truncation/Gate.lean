import Witnesses
open Fragmentation
example : scan (decorationsInput 2 true) stages = some (.bothClone, .cut (atA 1)) := by decide
