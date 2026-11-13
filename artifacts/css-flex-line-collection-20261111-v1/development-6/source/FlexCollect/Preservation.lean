import FlexCollect.Laws

namespace FlexCollect

variable {α : Type} (size : α → Rat) (threshold gap : Rat)

theorem collected_flatten {input : List α} {lines : List (List α)}
    (h : Collected size threshold gap input lines) : lines.flatten = input := by
  induction h with
  | nil => rfl
  | cons h _ ih => simpa only [List.flatten_cons, ih] using h.1.symm

theorem collected_nonempty {input : List α} {lines : List (List α)}
    (h : Collected size threshold gap input lines) : ∀ line ∈ lines, line ≠ [] := by
  induction h with
  | nil => simp
  | cons h _ ih =>
    intro line hmem
    rcases List.mem_cons.mp hmem with rfl | hmem
    · exact h.2.1
    · exact ih _ hmem

theorem collected_count {input : List α} {lines : List (List α)}
    (h : Collected size threshold gap input lines) : lines.length ≤ input.length := by
  induction h with
  | nil => exact Nat.le_refl _
  | cons h _ ih =>
    have hshort := next_rest_shorter size threshold gap h
    simp only [List.length_cons]
    omega

theorem collected_unique {input : List α} {left right : List (List α)}
    (hl : Collected size threshold gap input left)
    (hr : Collected size threshold gap input right) : left = right :=
  (collected_complete size threshold gap hl).symm.trans
    (collected_complete size threshold gap hr)

theorem collect_flatten (input : List α) :
    (collect size threshold gap input).flatten = input :=
  collected_flatten size threshold gap (collect_sound size threshold gap input)

theorem collect_nonempty (input : List α) (line : List α)
    (hmem : line ∈ collect size threshold gap input) : line ≠ [] :=
  collected_nonempty size threshold gap (collect_sound size threshold gap input) line hmem

theorem collect_count (input : List α) :
    (collect size threshold gap input).length ≤ input.length :=
  collected_count size threshold gap (collect_sound size threshold gap input)

theorem nowrap_flatten (input : List α) : (nowrap input).flatten = input := by
  cases input <;> simp [nowrap]

theorem oversized_singleton (x : α) (xs : List α) (h : threshold < size x) :
    collect size threshold gap (x :: xs) = [x] :: collect size threshold gap xs :=
  collect_step size threshold gap (next_oversized size threshold gap x xs h)

theorem span_snoc (line : List α) (x : α) (hne : line ≠ []) :
    span size gap (line ++ [x]) = span size gap line + gap + size x := by
  rw [span_append size gap line [x] hne]
  rfl

theorem universal : UniversalTarget := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro α size threshold gap input lines; exact collect_iff size threshold gap input lines
  · intro α size threshold gap input; exact collect_flatten size threshold gap input
  · intro α size threshold gap input line; exact collect_nonempty size threshold gap input line
  · intro α size threshold gap input; exact collect_count size threshold gap input
  · intro α size threshold gap input left right; exact collected_unique size threshold gap
  · intro α input; exact nowrap_flatten input

end FlexCollect
