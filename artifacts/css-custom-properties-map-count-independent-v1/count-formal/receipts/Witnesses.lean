import Index
namespace LiveCount

def oldCount (n : Nat) (newOwn parentPresent : Bool) : Nat :=
  if newOwn && !parentPresent then n + 1 else n

theorem original_removal_counterexample :
    let c : Chain Nat String := [[(0, some "value")]]
    count [0] c = 1 ∧ count [0] (insert c 0 none) = 0 ∧ oldCount 1 false false = 1 := by decide

theorem original_resurrection_counterexample :
    let c : Chain Nat String := [[(0, none)]]
    count [0] c = 0 ∧ count [0] (insert ([] :: c) 0 (some "value")) = 1 ∧
      oldCount 1 true false = 2 := by decide

theorem replacement_witness :
    let c : Chain Nat String := [[(0, some "before")]]
    (nativeInsert ⟨c,1⟩ 0 (some "after")).stored = 1 ∧
      lookup (nativeInsert ⟨c,1⟩ 0 (some "after")).chain 0 = some "after" := by decide

theorem removal_witness :
    let c : Chain Nat String := [[(0, some "value")]]
    (nativeInsert ⟨c,1⟩ 0 none).stored = 0 := by decide

theorem resurrection_witness :
    let c : Chain Nat String := [[], [(0, none)], [(0, some "old")]]
    (nativeInsert ⟨c,0⟩ 0 (some "new")).stored = 1 ∧
      lookup (nativeInsert ⟨c,0⟩ 0 (some "new")).chain 0 = some "new" := by decide

theorem valid_empty_witness :
    let c : Chain Nat String := [[(0, some ""), (1, none)]]
    count [0,1] c = 1 ∧ projection [0,1] c = [(0, "")] := by decide

theorem cow_modes_witness :
    let s : Store Nat String := ⟨[[(0,some "x")]],1⟩
    (doInsert true (fun _ _ => false) s 0 none).stored = 0 ∧
    (doInsert false (fun _ _ => false) s 0 none).stored = 0 ∧
    (doInsert false (fun _ _ => true) s 0 (some "x")).stored = 1 := by decide

theorem expansion_witness :
    let own : Node Nat String := (List.range 9).map (fun k => (k,some "x"))
    let s : Store Nat String := ⟨[own],9⟩
    (doInsert false (fun _ _ => false) s 0 none).chain.length = 2 ∧
    (doInsert false (fun _ _ => false) s 0 none).stored = 8 := by decide

theorem raw_iterator_premise_necessary :
    let c : Chain Nat String := [[(0,some "child")], [(0,some "parent"),(1,some "other")]]
    let raw : Node Nat String := [(0,some "child"),(0,some "parent"),(1,some "other")]
    count [0,1] c = 2 ∧
      getIndex raw 2 1 = some (0,some "parent") ∧
      ¬ RawEnumeration c raw := by
  refine ⟨by decide, by decide, ?_⟩
  intro h
  have unique := h.1
  simp at unique

end LiveCount
