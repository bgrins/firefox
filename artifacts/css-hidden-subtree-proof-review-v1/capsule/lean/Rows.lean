import Subtree
open Subtree

def flag (mask bit : Nat) : Bool := mask / (2 ^ bit) % 2 == 1

def fixture (mask hm tm : Nat) : World :=
  let leaf4 := Tree.node 4 (flag mask 3) (flag hm 1) false []
  let leaf5 := Tree.node 5 (flag mask 4) false false []
  let inner2 := Tree.node 2 (flag mask 1) false (tm == 1) [leaf4]
  let inner3 := Tree.node 3 (flag mask 2) false false [leaf5]
  let item := Tree.node 1 (flag mask 0) (flag hm 0) (tm == 2) [inner2, inner3]
  let placeholder := Tree.node 6 (flag mask 5) false false []
  ⟨flag mask 6, [item, placeholder], [.node 7 false false false []],
   [.node 8 false false false []], [.node 9 false false false []]⟩

mutual
 def observations : Tree → List (Nat × Bool × Bool)
   | .node id d h _ cs => (id, d, d || h) :: observationList cs
 def observationList : List Tree → List (Nat × Bool × Bool)
   | [] => []
   | t :: ts => observations t ++ observationList ts
end

def bitString (b : Bool) : String := if b then "1" else "0"

def main : IO Unit := do
  let mut id := 0
  for produce in [false, true] do
    for hidden in [false, true] do
      for mask in List.range 128 do
        for hm in List.range 4 do
          for tm in List.range 3 do
            let initial := fixture mask hm tm
            let before := if produce then {initial with principal := match initial.principal with | [] => [] | first :: rest => forceAll first :: rest} else initial
            let after := if hidden then markPrincipal before else before
            let rows := observationList (after.principal ++ after.otherLists ++ after.externalOutOfFlow ++ after.nextContinuation)
            let mut values := [toString id, bitString after.ownDirty]
            for (nodeId, d, e) in rows do
              values := values ++ [toString nodeId, bitString d, bitString e,
                bitString (e && hidden && nodeId ≤ 7)]
            IO.println (String.intercalate "," values)
            id := id + 1
