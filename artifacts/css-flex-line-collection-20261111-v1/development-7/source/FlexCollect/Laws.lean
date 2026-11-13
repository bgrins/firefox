import FlexCollect.Prefixes
import FlexCollect.Target

namespace FlexCollect

variable {α : Type} (size : α → Rat) (threshold gap : Rat)

def firstLine : List α → List α × List α
  | [] => ([], [])
  | x :: xs =>
    if threshold < size x then ([x], xs)
    else
      let p := takeMore size threshold gap (size x) xs
      (x :: p.1, p.2)

theorem next_oversized (x : α) (xs : List α) (h : threshold < size x) :
    NextLine size threshold gap (x :: xs) [x] xs :=
  ⟨rfl, List.cons_ne_nil _ _, Or.inl ⟨x, rfl, h⟩⟩

theorem next_ordinary (x : α) (xs : List α) (h : size x ≤ threshold) :
    let p := takeMore size threshold gap (size x) xs
    NextLine size threshold gap (x :: xs) (x :: p.1) p.2 := by
  obtain ⟨hsplit, hfits, hstop⟩ := takeMore_spec size threshold gap (size x) xs h
  refine ⟨congrArg (List.cons x) hsplit, List.cons_ne_nil _ _, Or.inr ?_⟩
  refine ⟨(prefixes_cons size threshold gap _ _).mpr hfits, ?_⟩
  cases heq : (takeMore size threshold gap (size x) xs).2 with
  | nil => trivial
  | cons y ys => simpa only [heq, List.cons_append, span, List.foldl_append, List.foldl_cons, List.foldl_nil] using hstop

theorem firstLine_sound (x : α) (xs : List α) :
    NextLine size threshold gap (x :: xs)
      (firstLine size threshold gap (x :: xs)).1
      (firstLine size threshold gap (x :: xs)).2 := by
  simp only [firstLine]
  split
  · exact next_oversized size threshold gap x xs ‹_›
  · exact next_ordinary size threshold gap x xs (Rat.not_lt.mp ‹_›)

theorem firstLine_complete {input line rest : List α}
    (h : NextLine size threshold gap input line rest) :
    firstLine size threshold gap input = (line, rest) := by
  obtain ⟨rfl, hne, hcase⟩ := h
  cases line with
  | nil => exact False.elim (hne rfl)
  | cons x xs =>
    rcases hcase with ⟨y, heq, hover⟩ | ⟨hfits, hstop⟩
    · obtain ⟨rfl, rfl⟩ := List.cons.inj heq
      simp [firstLine, hover]
    · have htrail := (prefixes_cons size threshold gap x xs).mp hfits
      have hstart := trail_start size threshold gap htrail
      simp only [List.cons_append, firstLine, ite_eq_right (Rat.not_lt.mpr hstart)]
      have hstop' := hstop
      simp only [List.cons_append, span, List.foldl_append, List.foldl_cons, List.foldl_nil] at hstop'
      rw [takeMore_complete size threshold gap _ _ _ htrail hstop']

theorem next_unique {input line rest line' rest' : List α}
    (h : NextLine size threshold gap input line rest)
    (h' : NextLine size threshold gap input line' rest') : line = line' ∧ rest = rest' := by
  exact Prod.mk.inj ((firstLine_complete size threshold gap h).symm.trans
    (firstLine_complete size threshold gap h'))

theorem next_rest_shorter {input line rest : List α}
    (h : NextLine size threshold gap input line rest) : rest.length < input.length := by
  obtain ⟨rfl, hne, _⟩ := h
  have hpos := List.length_pos_iff.mpr hne
  simp only [List.length_append]
  omega

theorem collect_step {input line rest : List α}
    (h : NextLine size threshold gap input line rest) :
    collect size threshold gap input = line :: collect size threshold gap rest := by
  have heq := firstLine_complete size threshold gap h
  cases input with
  | nil =>
    have : line = [] := (List.append_eq_nil_iff.mp h.1.symm).1
    exact False.elim (h.2.1 this)
  | cons x xs =>
    rw [collect]
    simp only [firstLine] at heq
    split <;> simp_all

theorem collect_sound (input : List α) :
    Collected size threshold gap input (collect size threshold gap input) := by
  induction input using (measure List.length).wf.induction with
  | h input ih =>
    cases input with
    | nil => simp only [collect]; exact Collected.nil
    | cons x xs =>
      have h := firstLine_sound size threshold gap x xs
      rw [collect_step size threshold gap h]
      exact Collected.cons h (ih _ (next_rest_shorter size threshold gap h))

theorem collected_complete {input : List α} {lines : List (List α)}
    (h : Collected size threshold gap input lines) :
    collect size threshold gap input = lines := by
  induction h with
  | nil => rw [collect]
  | cons h _ ih => rw [collect_step size threshold gap h, ih]

theorem collect_iff (input : List α) (lines : List (List α)) :
    collect size threshold gap input = lines ↔ Collected size threshold gap input lines := by
  constructor
  · rintro rfl; exact collect_sound size threshold gap input
  · exact collected_complete size threshold gap

end FlexCollect
