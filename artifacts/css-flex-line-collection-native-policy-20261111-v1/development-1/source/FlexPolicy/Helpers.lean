import FlexPolicy.Target
import FlexCollect.Preservation

namespace FlexPolicy

variable {α : Type} (size : α → Rat) (threshold gap limit : Rat)

theorem bound_implies_over {next : Rat} (h : threshold < limit) (hn : limit ≤ next) :
    threshold < next :=
  Rat.not_le.mp (fun bad => Rat.not_le.mpr h (Rat.le_trans hn bad))

theorem oldBreak_iff (next : Rat) (h : threshold < limit) :
    oldBreak threshold limit next = true ↔ threshold < next := by
  simp only [oldBreak, decide_eq_true_eq]
  exact ⟨fun h' => h'.elim (bound_implies_over threshold limit h) id, Or.inr⟩

theorem patchedBreak_iff (total next : Rat) (h : threshold < limit) :
    patchedBreak threshold limit total next = true ↔ threshold < total ∨ threshold < next := by
  simp only [patchedBreak, decide_eq_true_eq]
  constructor
  · intro hc
    rcases hc with hc | hc | hc
    · exact Or.inl hc
    · exact Or.inr (bound_implies_over threshold limit h hc)
    · exact Or.inr hc
  · intro hc
    exact hc.elim Or.inl (Or.inr ∘ Or.inr)

theorem singleton_ready (x : α) : Ready size threshold gap [x] := by
  refine ⟨List.cons_ne_nil _ _, ?_⟩
  by_cases h : threshold < size x
  · exact Or.inl ⟨x, rfl, h⟩
  · exact Or.inr ((FlexCollect.prefixes_cons size threshold gap x []).mpr (Rat.not_lt.mp h))

theorem prefixes_span {current : List α}
    (h : FlexCollect.PrefixesFit size threshold gap current) (hne : current ≠ []) :
    FlexCollect.span size gap current ≤ threshold :=
  h current [] (List.append_nil _).symm hne

theorem ready_bounded {current : List α} (h : Ready size threshold gap current)
    (hb : FlexCollect.span size gap current ≤ threshold) :
    FlexCollect.PrefixesFit size threshold gap current := by
  rcases h.2 with ⟨x, rfl, hx⟩ | hf
  · exact False.elim (Rat.not_le.mpr hx hb)
  · exact hf

theorem trail_snoc (used : Rat) (xs : List α) (x : α)
    (h : FlexCollect.TrailFits size threshold gap used xs)
    (hn : xs.foldl (fun v y => v + gap + size y) used + gap + size x ≤ threshold) :
    FlexCollect.TrailFits size threshold gap used (xs ++ [x]) := by
  induction xs generalizing used with
  | nil => exact ⟨h, hn⟩
  | cons y ys ih => exact ⟨h.1, ih _ h.2 hn⟩

theorem prefixes_snoc {current : List α} (hne : current ≠ []) (x : α)
    (h : FlexCollect.PrefixesFit size threshold gap current)
    (hn : FlexCollect.span size gap (current ++ [x]) ≤ threshold) :
    FlexCollect.PrefixesFit size threshold gap (current ++ [x]) := by
  cases current with
  | nil => exact False.elim (hne rfl)
  | cons y ys =>
    apply (FlexCollect.prefixes_cons size threshold gap y (ys ++ [x])).mpr
    apply trail_snoc size threshold gap _ _ _ ((FlexCollect.prefixes_cons size threshold gap y ys).mp h)
    simpa only [FlexCollect.span, List.cons_append, List.foldl_append, List.foldl_cons, List.foldl_nil] using hn

theorem next_of_ready {current rest : List α} (h : Ready size threshold gap current)
    (hstop : match rest with
      | [] => True
      | x :: _ => threshold < FlexCollect.span size gap (current ++ [x])) :
    FlexCollect.NextLine size threshold gap (current ++ rest) current rest := by
  refine ⟨rfl, h.1, ?_⟩
  exact h.2.elim Or.inl (fun hf => Or.inr ⟨hf, hstop⟩)

theorem next_of_break {current : List α} (x : α) (xs : List α)
    (h : Ready size threshold gap current)
    (hc : threshold < FlexCollect.span size gap current ∨
      threshold < FlexCollect.span size gap (current ++ [x])) :
    FlexCollect.NextLine size threshold gap (current ++ x :: xs) current (x :: xs) := by
  rcases h.2 with hover | hfit
  · exact ⟨rfl, h.1, Or.inl hover⟩
  · apply next_of_ready size threshold gap h
    exact hc.resolve_left (Rat.not_lt.mpr (prefixes_span size threshold gap hfit h.1))

theorem append_gate {current : List α} (x : α) (h : current ≠ []) :
    (current ++ [x]).length > 1 := by
  have hp := List.length_pos_iff.mpr h
  simp only [List.length_append, List.length_singleton]
  omega

theorem loop_nil (cut : Rat → Rat → Bool) {current : List α} (total : Rat)
    (h : current ≠ []) : loop size gap cut current total [] = [current] := by
  cases current with
  | nil => exact False.elim (h rfl)
  | cons x xs => rfl

theorem loop_start (cut : Rat → Rat → Bool) (total : Rat) (x : α) (xs : List α) :
    loop size gap cut [] total (x :: xs) = loop size gap cut [x] (size x) xs := by
  simp [loop]

theorem loop_step (cut : Rat → Rat → Bool) {current : List α} (total : Rat)
    (x : α) (xs : List α) (h : current ≠ []) :
    loop size gap cut current total (x :: xs) =
      if cut total (total + size x + gap) then
        current :: loop size gap cut [x] (size x) xs
      else loop size gap cut (current ++ [x]) (total + size x + gap) xs := by
  simp only [loop, ite_eq_left (append_gate x h)]

end FlexPolicy
