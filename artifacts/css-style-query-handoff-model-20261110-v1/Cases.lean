import Model

namespace CssQueryHandoff.Cases

def parent : Fin 6 → Option (Fin 6)
  | ⟨0, _⟩ => none
  | ⟨1, _⟩ => some 0
  | ⟨2, _⟩ => some 1
  | ⟨3, _⟩ => some 2
  | ⟨4, _⟩ => some 2
  | _ => some 0

def next : Fin 6 → Fin 6
  | ⟨2, _⟩ => 1
  | ⟨3, _⟩ | ⟨4, _⟩ => 2
  | _ => 0

def depth : Fin 6 → Nat
  | ⟨0, _⟩ => 0
  | ⟨2, _⟩ => 2
  | ⟨3, _⟩ | ⟨4, _⟩ => 3
  | _ => 1

def children : Fin 6 → List (Fin 6)
  | ⟨0, _⟩ => [1, 5]
  | ⟨1, _⟩ => [2]
  | ⟨2, _⟩ => [3, 4]
  | _ => []

def tree : Tree 6 := {
  root := 0
  parent := parent
  next := next
  depth := depth
  root_parent := by decide
  next_edge := by decide
  decreases := by decide
  children := children
  children_exact := by decide
}

def styled (node : Fin 6) : Bool := node == 3

def empty : State 6 := ⟨fun _ _ => false, fun _ => false⟩
def oldFont : State 6 := ⟨fun _ bit => bit == .font || bit == .other, fun _ => false⟩
def unnamed : Producer 6 := ⟨2, fun bit => bit == .unnamedQuery⟩
def named : Producer 6 := ⟨2, fun bit => bit == .namedQuery⟩
def fontOnly : Producer 6 := ⟨2, fun bit => bit == .font⟩
def existingDirty : Certificates 6 := ⟨fun _ => false, fun node => node == 2⟩
def unsound : Certificates 6 := ⟨fun node => node == 2, fun node => node == 2⟩

def checks : List (String × Bool) := [
  ("unnamed mask reaches styled child", decide ((handoff tree styled true [unnamed] empty).hints 3 .unnamedQuery = true)),
  ("named mask reaches styled child", decide ((handoff tree styled true [named] empty).hints 3 .namedQuery = true)),
  ("named mask does not invent unnamed bit", decide ((handoff tree styled true [named] empty).hints 3 .unnamedQuery = false)),
  ("producer receives no self hint", decide ((handoff tree styled true [unnamed] empty).hints 2 .unnamedQuery = false)),
  ("root child is not producer child", decide ((handoff tree styled true [unnamed] empty).hints 1 .unnamedQuery = false)),
  ("unstyled child skipped", decide ((handoff tree styled true [unnamed] empty).hints 4 .unnamedQuery = false)),
  ("sibling branch unaffected", decide ((handoff tree styled true [unnamed] empty).hints 5 .unnamedQuery = false)),
  ("existing font hint preserved", decide ((handoff tree styled true [unnamed] oldFont).hints 3 .font = true)),
  ("existing other hint preserved", decide ((handoff tree styled true [unnamed] oldFont).hints 3 .other = true)),
  ("query does not invent font hint", decide ((handoff tree styled true [unnamed] empty).hints 3 .font = false)),
  ("font-only producer not collected", decide ((handoff tree styled true [fontOnly] empty).hints 3 .font = false)),
  ("normal traversal not collected", decide ((handoff tree styled false [unnamed] empty).hints 3 .unnamedQuery = false)),
  ("root dirty", decide ((handoff tree styled true [unnamed] empty).dirty 0 = true)),
  ("ancestor dirty", decide ((handoff tree styled true [unnamed] empty).dirty 1 = true)),
  ("producer dirty", decide ((handoff tree styled true [unnamed] empty).dirty 2 = true)),
  ("seeded child excluded from dirty path", decide ((handoff tree styled true [unnamed] empty).dirty 3 = false)),
  ("sibling dirty bit untouched", decide ((handoff tree styled true [unnamed] empty).dirty 5 = false)),
  ("duplicate producer preserves union", decide ((handoff tree styled true [unnamed, named, unnamed] empty).hints 3 .namedQuery = true)),
  ("empty certificate ignores preexisting dirty bit", decide (clippedAncestors tree existingDirty.certified 2 = [2, 1, 0])),
  ("preexisting dirty bit does not hide root", decide ((certify tree 2 existingDirty).dirty 0 = true)),
  ("first producer certifies full path", decide ((certify tree 2 existingDirty).certified 0 = true)),
  ("later producer stops at certified ancestor", decide (clippedAncestors tree (certify tree 2 existingDirty).certified 3 = [3])),
  ("duplicate producer has empty new prefix", decide (clippedAncestors tree (certify tree 2 existingDirty).certified 2 = [])),
  ("shared path keeps root dirty", decide ((certifyMany tree [2, 3, 2] existingDirty).dirty 0 = true)),
  ("unsound certificate can miss root (off-domain)", decide ((certify tree 2 unsound).dirty 0 = false))
]

end CssQueryHandoff.Cases
