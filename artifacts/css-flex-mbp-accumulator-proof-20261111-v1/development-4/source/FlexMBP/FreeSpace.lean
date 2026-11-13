import FlexMBP.Boundary

namespace FlexMBP

theorem subtractUsed_of_prefixes {α : Type} (usedMain : α → Int)
    (items : List α) (initial : Int)
    (h : ∀ n ≤ items.length, Fits64 (initial - sum usedMain (items.take n))) :
    subtractUsed usedMain initial items = some (initial - sum usedMain items) := by
  induction items generalizing initial with
  | nil => simp [subtractUsed, sum]
  | cons item items ih =>
    have hfirst := h 1 (by simp)
    simp [sum, Fits64] at hfirst
    have hn : checkedSub64 initial (usedMain item) = some (initial - usedMain item) := by
      simp [checkedSub64, hfirst]
    have ht : ∀ n ≤ items.length,
        Fits64 (initial - usedMain item - sum usedMain (items.take n)) := by
      intro n hn
      have hp := h (n + 1) (by simp; omega)
      simpa [List.take_succ_cons, sum_cons, Int.sub_sub] using hp
    simpa [subtractUsed, hn, sum_cons, Int.sub_sub] using ih (initial - usedMain item) ht

theorem free_space_exact {α : Type} (mbp usedMain : α → Int)
    (inner gaps : Int) (items : List α) (ha : Acquired mbp items)
    (hd : DownstreamFits mbp usedMain inner gaps items) :
    freeSpace mbp usedMain inner gaps items =
      some (inner - (sum mbp items + gaps) - sum usedMain items) := by
  rcases hd with ⟨_, _, _, occupiedRange, prefixes⟩
  have hw := wide_exact mbp items ha
  have hc : checkedAdd min64 max64 (sum mbp items) gaps = some (sum mbp items + gaps) := by
    simp [checkedAdd, occupiedRange.1, occupiedRange.2]
  have hzero := prefixes 0 (by omega)
  simp [sum, Fits64] at hzero
  have hs : checkedSub64 inner (sum mbp items + gaps) = some (inner - (sum mbp items + gaps)) := by
    simp [checkedSub64, hzero]
  simpa [freeSpace, hw, hc, hs] using
    subtractUsed_of_prefixes usedMain items (inner - (sum mbp items + gaps)) prefixes

theorem free_space_target : FreeSpaceTarget := by
  intro α mbp usedMain inner gaps items ha hd
  exact free_space_exact mbp usedMain inner gaps items ha hd

theorem sum_constant {α : Type} (value : Int) (items : List α) :
    sum (fun _ => value) items = value * (items.length : Int) := by
  induction items with
  | nil => simp [sum]
  | cons item items ih => simp [sum_cons, ih, Int.mul_add, Int.add_comm]

end FlexMBP
