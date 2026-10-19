import TaintHistory
open TaintShortcut
def main : IO Unit := do
  let cmp := fun (a b : State Nat) => payloadSame (fun x y => x == y) a b && (a.isNone || b.isNone || ((a.map Value.attr).getD false || !((b.map Value.attr).getD false)))
  let forward := LiveCount.run cmp LiveCount.initial TaintHistory.exampleOps
  let reverseOps : List (LiveCount.Op Nat (Value Nat)) :=
    [⟨1,some ⟨7,true⟩,false⟩,⟨1,some ⟨7,false⟩,false⟩]
  let reverse := LiveCount.run cmp LiveCount.initial reverseOps
  let removed := LiveCount.run cmp forward [⟨1,none,false⟩]
  let observations := [decide (forward.stored = 1),
    decide (LiveCount.lookup forward.chain 1 = some ⟨7,true⟩),
    decide (MapIterator.getIndex forward.chain forward.stored 0 = some (1,some ⟨7,true⟩)),
    decide (reverse.stored = 1),
    decide (LiveCount.lookup reverse.chain 1 = some ⟨7,false⟩),
    decide (MapIterator.getIndex reverse.chain reverse.stored 0 = some (1,some ⟨7,false⟩)),
    decide (removed.stored = 0 ∧ LiveCount.lookup removed.chain 1 = none)]
  IO.println (String.intercalate "|" (observations.map toString))
