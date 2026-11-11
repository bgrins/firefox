import Grammar

namespace CssGrammar

theorem keyword_iff : Matches (.keyword word) input rest ↔ input = word :: rest := by
  constructor
  · intro h; cases h; rfl
  · intro h; subst input; exact .keyword

theorem alt_iff : Matches (.alt left right) input rest ↔
    Matches left input rest ∨ Matches right input rest := by
  constructor
  · intro h; cases h with
    | left h => exact Or.inl h
    | right h => exact Or.inr h
  · intro h; cases h with
    | inl h => exact .left h
    | inr h => exact .right h

theorem seq_iff : Matches (.seq left right) input rest ↔
    ∃ middle, Matches left input middle ∧ Matches right middle rest := by
  constructor
  · intro h; cases h with | seq a b => exact ⟨_, a, b⟩
  · rintro ⟨middle, a, b⟩; exact .seq a b

theorem optional_iff : Matches (.optional body) input rest ↔
    input = rest ∨ Matches body input rest := by
  constructor
  · intro h; cases h with
    | absent => exact Or.inl rfl
    | present h => exact Or.inr h
  · intro h; cases h with
    | inl h => subst rest; exact .absent
    | inr h => exact .present h

theorem run_iff (grammar : Grammar) (input rest : List String) :
    rest ∈ run grammar input ↔ Matches grammar input rest := by
  induction grammar generalizing input rest with
  | keyword word =>
    rw [keyword_iff]
    cases input with
    | nil => simp [run]
    | cons first tail =>
      by_cases h : first = word
      · subst first; simp [run, eq_comm]
      · simp [run, h]
  | alt left right ihL ihR => simp [run, alt_iff, ihL, ihR]
  | seq left right ihL ihR => simp [run, seq_iff, ihL, ihR]
  | optional body ih => simp [run, optional_iff, ih, eq_comm]

theorem accepts_iff (grammar : Grammar) (input : List String) :
    accepts grammar input = true ↔ Matches grammar input [] := by
  simp [accepts, run_iff]

theorem remainder_suffix (h : Matches grammar input rest) :
    ∃ consumed, input = consumed ++ rest := by
  induction h with
  | keyword => exact ⟨[_], rfl⟩
  | left h ih => exact ih
  | right h ih => exact ih
  | seq a b ia ib =>
    obtain ⟨x, hx⟩ := ia
    obtain ⟨y, hy⟩ := ib
    exact ⟨x ++ y, by simp [hx, hy, List.append_assoc]⟩
  | absent => exact ⟨[], rfl⟩
  | present h ih => exact ih

end CssGrammar

namespace CssGrammar

def language : Grammar → List (List String)
  | .keyword word => [[word]]
  | .alt left right => language left ++ language right
  | .seq left right => (language left).flatMap fun x => (language right).map (x ++ ·)
  | .optional body => [] :: language body

theorem matches_append (h : Matches grammar input rest) (tail : List String) :
    Matches grammar (input ++ tail) (rest ++ tail) := by
  induction h with
  | keyword => exact .keyword
  | left h ih => exact .left ih
  | right h ih => exact .right ih
  | seq a b ia ib => exact .seq ia ib
  | absent => exact .absent
  | present h ih => exact .present ih

theorem language_complete (grammar : Grammar) (words : List String)
    (member : words ∈ language grammar) : Matches grammar words [] := by
  induction grammar generalizing words with
  | keyword word => simp [language] at member; subst words; exact .keyword
  | alt left right ihL ihR =>
    simp only [language, List.mem_append] at member
    rcases member with h | h
    · exact .left (ihL words h)
    · exact .right (ihR words h)
  | seq left right ihL ihR =>
    simp only [language, List.mem_flatMap, List.mem_map] at member
    obtain ⟨a, ha, b, hb, equal⟩ := member
    subst words
    exact .seq (by simpa using matches_append (ihL a ha) b) (ihR b hb)
  | optional body ih =>
    simp only [language, List.mem_cons] at member
    rcases member with h | h
    · subst words; exact .absent
    · exact .present (ih words h)

theorem language_sound (h : Matches grammar input rest) :
    ∃ consumed ∈ language grammar, input = consumed ++ rest := by
  induction h with
  | keyword => exact ⟨[_], by simp [language], rfl⟩
  | left h ih => obtain ⟨x, hx, eq⟩ := ih; exact ⟨x, by simp [language, hx], eq⟩
  | right h ih => obtain ⟨x, hx, eq⟩ := ih; exact ⟨x, by simp [language, hx], eq⟩
  | seq a b ia ib =>
    obtain ⟨x, hx, ex⟩ := ia
    obtain ⟨y, hy, ey⟩ := ib
    refine ⟨x ++ y, ?_, ?_⟩
    · simp only [language, List.mem_flatMap, List.mem_map]
      exact ⟨x, hx, y, hy, rfl⟩
    · simp [ex, ey, List.append_assoc]
  | absent => exact ⟨[], by simp [language], rfl⟩
  | present h ih => obtain ⟨x, hx, eq⟩ := ih; exact ⟨x, by simp [language, hx], eq⟩

theorem accepts_language (grammar : Grammar) (words : List String) :
    accepts grammar words = true ↔ words ∈ language grammar := by
  rw [accepts_iff]
  constructor
  · intro h
    obtain ⟨consumed, member, equal⟩ := language_sound h
    simpa [equal] using member
  · exact language_complete grammar words

end CssGrammar
