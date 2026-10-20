import Witnesses
open Fragmentation
example :
    (List.map (rules .strict {page := true} sevenLines) [linePoint 2, linePoint 3, linePoint 4, linePoint 5, linePoint 6]) =
      [false, true, true, true, false] ∧ lineCount 99 sevenLines = 0 := by decide
