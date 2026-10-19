import Model
open TaintShortcut
def main : IO Unit := do
  let cmp : Nat → Nat → Bool := fun a b => a == b
  let clean : State Nat := some ⟨7,false⟩
  let tainted : State Nat := some ⟨7,true⟩
  let literal : Incoming Nat := ⟨7,false,false,false,true⟩
  let explicit : Incoming Nat := ⟨7,false,true,false,true⟩
  let typed : Incoming Nat := ⟨9,false,false,false,false⟩
  let syntax : Incoming Nat := ⟨7,true,false,true,false⟩
  let resolve : Incoming Nat → State Nat := fun d => some (declaredValue d)
  let observations := [decide (repaired cmp resolve false clean explicit = tainted),
    decide (repaired cmp resolve false tainted literal = clean),
    decide (repaired cmp resolve true clean typed = some ⟨9,false⟩),
    decide (mapUpdate (metadataSame cmp) false none (some ⟨0,false⟩) = some ⟨0,false⟩),
    decide (mapUpdate (metadataSame cmp) false tainted none = none),
    decide (repaired cmp resolve false clean syntax = tainted),
    decide (repaired cmp resolve false clean literal = clean)]
  IO.println (String.intercalate "|" (observations.map toString))
