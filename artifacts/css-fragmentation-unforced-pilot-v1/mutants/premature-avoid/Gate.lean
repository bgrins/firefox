import Witnesses
open Fragmentation
example :
    evaluate .lines avoidInput = none ∧ scan avoidInput stages =
      some (.avoid, .cut { (atA 1) with controls := [.avoid] }) := by decide
