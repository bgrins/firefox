import FlexMBP.Target

namespace FlexMBP

theorem sum_nil {α : Type} (mbp : α → Int) : sum mbp [] = 0 := by
  simp [sum]

theorem sum_cons {α : Type} (mbp : α → Int) (item : α) (items : List α) :
    sum mbp (item :: items) = mbp item + sum mbp items := by
  simp [sum]

theorem sum_append {α : Type} (mbp : α → Int) (xs ys : List α) :
    sum mbp (xs ++ ys) = sum mbp xs + sum mbp ys := by
  simp [sum, List.sum_append]

theorem sum_bounds {α : Type} (mbp : α → Int) (items : List α)
    (lower upper : Int) (h : ∀ item ∈ items, lower ≤ mbp item ∧ mbp item ≤ upper) :
    lower * (items.length : Int) ≤ sum mbp items ∧
      sum mbp items ≤ upper * (items.length : Int) := by
  induction items with
  | nil => simp [sum]
  | cons item items ih =>
    have hx := h item (by simp)
    have ht := ih (fun y hy => h y (by simp [hy]))
    simp only [sum_cons, List.length_cons, Int.natCast_add, Int.natCast_one]
    constructor
    · calc
        lower * ((items.length : Int) + 1) = lower + lower * (items.length : Int) := by omega
        _ ≤ mbp item + sum mbp items := Int.add_le_add hx.1 ht.1
    · calc
        mbp item + sum mbp items ≤ upper + upper * (items.length : Int) := Int.add_le_add hx.2 ht.2
        _ = upper * ((items.length : Int) + 1) := by omega

theorem prefix_bounds {α : Type} (mbp : α → Int) (items : List α)
    (h : ∀ item ∈ items, Fits32 (mbp item)) (n : Nat) (hn : n ≤ items.length) :
    min32 * (n : Int) ≤ sum mbp (items.take n) ∧
      sum mbp (items.take n) ≤ max32 * (n : Int) := by
  have hb := sum_bounds mbp (items.take n) min32 max32
    (fun item hi => h item (List.mem_of_mem_take hi))
  simpa [List.length_take, Nat.min_eq_left hn] using hb

theorem range_from_count (n : Nat) (total : Int) (hn : n ≤ maxCount)
    (hl : min32 * (n : Int) ≤ total) (hu : total ≤ max32 * (n : Int)) : Fits64 total := by
  simp [min32, max32, maxCount, Fits64, min64, max64] at *
  omega

theorem prefix_range {α : Type} (mbp : α → Int) (items : List α)
    (h : Acquired mbp items) (n : Nat) (hn : n ≤ items.length) :
    Fits64 (sum mbp (items.take n)) := by
  have hb := prefix_bounds mbp items h.2 n hn
  exact range_from_count n _ (Nat.le_trans hn h.1) hb.1 hb.2

theorem prefix_target : PrefixTarget := by
  intro α mbp items h n hn
  exact ⟨(prefix_bounds mbp items h.2 n hn).1,
    (prefix_bounds mbp items h.2 n hn).2, prefix_range mbp items h n hn⟩

end FlexMBP
