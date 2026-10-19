import Model
open MapIterator
def main : IO Unit := do
  let shadow : Chain Nat Nat := [[(0,some 20)],[(0,some 10),(1,some 30)]]
  let deep : Chain Nat Nat := [[(0,some 40)],[],[(0,some 10),(1,some 30)]]
  let tomb : Chain Nat Nat := [[(0,none)],[(0,some 10),(1,some 30)]]
  let checks := [decide (drain (start shadow) = [(0,some 20),(1,some 30)]),
    decide (drain (start deep) = [(0,some 40),(1,some 30)]),
    decide (drain (start tomb) = [(0,none),(1,some 30)]),
    decide (getIndex tomb 1 0 = some (1,some 30)),
    decide (drain (start ([[],[],[]] : Chain Nat Nat)) = [])]
  IO.println (String.intercalate "|" (checks.map toString))
