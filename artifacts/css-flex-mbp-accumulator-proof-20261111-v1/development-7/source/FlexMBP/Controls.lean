import FlexMBP.Laws

namespace FlexMBP

def dropFirst {α : Type} (mbp : α → Int) (items : List α) : Option Int :=
  wideFold mbp items.tail

def reverseIdentity {α : Type} (mbp : α → Int) (items : List α) :
    Option (List α × Int) :=
  (wideFold mbp items).map (fun total => (items.reverse, total))

def ignoreGap {α : Type} (mbp usedMain : α → Int) (inner : Int)
    (items : List α) : Option Int :=
  freeSpace mbp usedMain inner 0 items

theorem dropFirst_wrong : dropFirst id ([-6, -7] : List Int) = some (-7) := by decide

theorem dropFirst_refutes_sum :
    ¬ (∀ items : List Int, Acquired id items → dropFirst id items = some (sum id items)) := by
  intro h
  have he := h [-6, -7] (by simp [Acquired, Fits32, min32, max32, maxCount])
  rw [dropFirst_wrong] at he
  simp [sum] at he

theorem reverseIdentity_wrong :
    reverseIdentity Prod.snd ([(1, -6), (2, -6)] : List (Nat × Int)) =
      some ([(2, -6), (1, -6)], -12) := by decide

theorem reverseIdentity_refutes_identity :
    ¬ (∀ items : List (Nat × Int), Acquired Prod.snd items →
      reverseIdentity Prod.snd items = some (items, sum Prod.snd items)) := by
  intro h
  have he := h [(1, -6), (2, -6)] (by simp [Acquired, Fits32, min32, max32, maxCount])
  rw [reverseIdentity_wrong] at he
  simp at he

theorem ignoreGap_wrong :
    ignoreGap id (fun _ => 2) 10 ([-2] : List Int) = some 10 := by decide

theorem actual_gap_case :
    freeSpace id (fun _ => 2) 10 3 ([-2] : List Int) = some 7 := by decide

theorem ignoreGap_refutes_actual :
    ignoreGap id (fun _ => 2) 10 ([-2] : List Int) ≠
      freeSpace id (fun _ => 2) 10 3 ([-2] : List Int) := by
  rw [ignoreGap_wrong, actual_gap_case]
  decide

end FlexMBP
