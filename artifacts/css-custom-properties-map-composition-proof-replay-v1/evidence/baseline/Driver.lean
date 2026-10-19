import Model
open MapComposition Wiring
def main : IO Unit := do
  let observations := [decide ((MapIterator.live (raw removed.chain)).length = removed.stored),
    decide (indexed removed 0 = some (1,some 11)),
    decide (indexed restored 0 = some (0,some 99)),
    decide (owner removed.chain 0 = some none),
    decide (indexed removed removed.stored = none)]
  IO.println (String.intercalate "|" (observations.map toString))
