import FlexCollect.Model

namespace FlexCollect

variable {α : Type} (size : α → Rat) (threshold gap : Rat)

def TrailFits (used : Rat) : List α → Prop
  | [] => used ≤ threshold
  | x :: xs => used ≤ threshold ∧ TrailFits (used + gap + size x) xs

theorem trail_start {used : Rat} {xs : List α}
    (h : TrailFits size threshold gap used xs) : used ≤ threshold := by
  cases xs <;> simp_all [TrailFits]

theorem trail_iff (used : Rat) (xs : List α) :
    TrailFits size threshold gap used xs ↔
      ∀ pre suffix, xs = pre ++ suffix →
        pre.foldl (fun v x => v + gap + size x) used ≤ threshold := by
  induction xs generalizing used with
  | nil =>
    constructor
    · intro h pre suffix heq
      have : pre = [] := (List.append_eq_nil_iff.mp heq.symm).1
      subst pre
      exact h
    · intro h
      exact h [] [] rfl
  | cons x xs ih =>
    constructor
    · rintro ⟨hstart, htail⟩ pre suffix heq
      cases pre with
      | nil => exact hstart
      | cons y ys =>
        have eqs : x = y ∧ xs = ys ++ suffix := List.cons.inj heq
        subst y
        exact (ih _).mp htail ys suffix eqs.2
    · intro h
      refine ⟨h [] (x :: xs) rfl, (ih _).mpr ?_⟩
      intro pre suffix heq
      exact h (x :: pre) suffix (by simp [heq])

theorem prefixes_cons (x : α) (xs : List α) :
    PrefixesFit size threshold gap (x :: xs) ↔
      TrailFits size threshold gap (size x) xs := by
  rw [trail_iff]
  constructor
  · intro h pre suffix heq
    exact h (x :: pre) suffix (by simp [heq]) (List.cons_ne_nil _ _)
  · intro h pre suffix heq hne
    cases pre with
    | nil => exact False.elim (hne rfl)
    | cons y ys =>
      have eqs : x = y ∧ xs = ys ++ suffix := List.cons.inj heq
      subst y
      exact h ys suffix eqs.2

theorem span_append (line tail : List α) (hne : line ≠ []) :
    span size gap (line ++ tail) =
      tail.foldl (fun used x => used + gap + size x) (span size gap line) := by
  cases line with
  | nil => exact False.elim (hne rfl)
  | cons x xs => simp [span, List.foldl_append]

theorem takeMore_spec (used : Rat) (xs : List α) (hused : used ≤ threshold) :
    let p := takeMore size threshold gap used xs
    xs = p.1 ++ p.2 ∧ TrailFits size threshold gap used p.1 ∧
      match p.2 with
      | [] => True
      | x :: _ => threshold < p.1.foldl (fun v y => v + gap + size y) used + gap + size x := by
  induction xs generalizing used with
  | nil => simp [takeMore, TrailFits, hused]
  | cons x xs ih =>
    simp only [takeMore]
    split
    · rename_i h
      obtain ⟨hsplit, hfits, hstop⟩ := ih _ h
      exact ⟨by simp [hsplit], ⟨hused, hfits⟩, hstop⟩
    · rename_i h
      exact ⟨rfl, hused, by simpa using h⟩

theorem takeMore_complete (used : Rat) (taken rest : List α)
    (hfits : TrailFits size threshold gap used taken)
    (hstop : match rest with
      | [] => True
      | x :: _ => threshold < taken.foldl (fun v y => v + gap + size y) used + gap + size x) :
    takeMore size threshold gap used (taken ++ rest) = (taken, rest) := by
  induction taken generalizing used with
  | nil =>
    cases rest with
    | nil => rfl
    | cons x xs => simp only [List.nil_append, takeMore]; split <;> simp_all
  | cons x xs ih =>
    have h := trail_start size threshold gap hfits.2
    simp only [List.cons_append, takeMore, if_pos h]
    rw [ih _ hfits.2 hstop]

end FlexCollect
