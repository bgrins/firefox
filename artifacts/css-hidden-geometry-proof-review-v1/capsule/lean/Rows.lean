import Hidden

open Hidden

def provider (mode : Int) (k : Key) : Size :=
  let out := fixedBlock k
  ⟨out.i + mode, out.b + 2 * mode⟩

def bit (b : Bool) : String := if b then "1" else "0"

def main (args : List String) : IO Unit := do
  if args != ["old"] && args != ["repaired"] then
    throw (IO.userError "Rows.lean old|repaired")
  let repair := args == ["repaired"]
  let mut id : Nat := 0
  for hidden in [false, true] do
    for dirty in [false, true] do
      for cacheMode in [0, 1, 2] do
        for sizeMode in [false, true] do
          for border in ([0, 1] : List Int) do
            for mode in ([0, 1] : List Int) do
              for forceKeyMode in [false, true] do
                let computed : Size := if sizeMode then ⟨17, 13⟩ else ⟨24, 32⟩
                let k : Key := ⟨computed, ⟨320, 0⟩, border, 2 * border,
                  3 * border, 4 * border, 0, 1000, 1000⟩
                let cachedKey := if cacheMode == 2 then {k with containingBlock := ⟨320, 32⟩} else k
                let prior := provider mode cachedKey
                let cache := if cacheMode == 0 then none else some ⟨cachedKey, cacheableB cachedKey prior⟩
                let initial : Frame := ⟨dirty, prior, cache⟩
                let after := measure repair hidden (provider mode) k initial
                let forcedKey := if forceKeyMode then {k with containingBlock := ⟨320, 32⟩} else k
                let queried := geometryQuery hidden (provider mode) forcedKey after.frame
                let forces : Nat := if after.frame.dirty && hidden then 1 else 0
                let repeated := geometryQuery hidden (provider mode) forcedKey queried
                let secondForces : Nat := if queried.dirty && hidden then 1 else 0
                IO.println (String.intercalate "," [toString id,
                  toString after.frame.geometry.i, toString after.frame.geometry.b,
                  bit after.frame.dirty, toString after.measuredB, bit after.reused,
                  toString queried.geometry.i, toString queried.geometry.b, bit queried.dirty,
                  toString forces, toString repeated.geometry.i, toString repeated.geometry.b,
                  bit repeated.dirty, toString (forces + secondForces)])
                id := id + 1
