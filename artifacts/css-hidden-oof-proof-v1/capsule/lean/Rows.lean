import OOF

def bit (n i : Nat) : Bool := (n / 2 ^ i) % 2 == 1
def bn (b : Bool) : Int := if b then 1 else 0

def stateBits : Subtree.Tree → Int
  | .node _ d h _ _ => bn d + 2 * bn h

def main : IO Unit := do
  let mut row := 0
  for timing in [OOF.Timing.original, .beforeInput, .afterInput] do
    for dm in [0:8] do
      for hm in [0:4] do
        for ph in [false, true] do
          for next in [false, true] do
            for differs in [false, true] do
              for table in [false, true] do
                for owner in [false, true] do
                  for anon in [false, true] do
                    let leaf := Subtree.Tree.node 2 (bit dm 2) (bit hm 1) false []
                    let mid := Subtree.Tree.node 1 (bit dm 1) false table [leaf]
                    let tree := Subtree.Tree.node 0 (bit dm 0) (bit hm 0) false [mid]
                    let hidden := OOF.nativeHidden ph true anon
                    let result := OOF.execute timing hidden next differs
                      (fun _ t => ⟨t, ⟨720, 480⟩⟩) OOF.centered tree
                    let middle := (Subtree.locate [0] result.tree).getD tree
                    let selected := (Subtree.locate [0, 0] result.tree).getD tree
                    let r := result.rect
                    let values : List Int := [row, (match timing with | .original => 0 | .beforeInput => 1 | .afterInput => 2), dm, hm,
                      bn ph, bn next, bn differs, bn table, bn owner, bn anon,
                      bn result.iResize, stateBits result.tree, stateBits middle, stateBits selected,
                      bn (Subtree.eligible result.tree), bn (Subtree.eligible selected),
                      bn (Subtree.eligible selected && ph), r.x, r.y, r.w, r.h]
                    IO.println (String.intercalate "," (values.map toString))
                    row := row + 1
