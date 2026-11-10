import DomString

namespace CssSemantics.DomString

open CodePointInput

theorem pairPoint_range (u v : CodeUnit) (lead : Leading u) (trail : Trailing v) :
    0x10000 ≤ (pairPoint u v lead trail).val ∧ (pairPoint u v lead trail).val ≤ 0x10ffff := by
  obtain ⟨_, _⟩ := lead
  obtain ⟨_, _⟩ := trail
  simp only [pairPoint]
  omega

theorem unitOfNat?_none_iff (n : Nat) : unitOfNat? n = none ↔ 0x10000 ≤ n := by
  simp [unitOfNat?]

theorem next_single (u : CodeUnit) (rest : List CodeUnit) (no : NoPair u rest) :
    next (u :: rest) = some (unitPoint u, rest) := by
  cases rest with
  | nil => rfl
  | cons v tail => simp [next, no v tail rfl]

theorem decode_single (u : CodeUnit) (rest : List CodeUnit) (no : NoPair u rest) :
    decode (u :: rest) = unitPoint u :: decode rest := by
  cases rest with
  | nil => rfl
  | cons v tail => simp [decode, no v tail rfl]

theorem Step.next_result {source p rest} (step : Step source p rest) : next source = some (p, rest) := by
  cases step with
  | pair u v p rest lead trail value =>
      have equal : pairPoint u v lead trail = p := Fin.ext value.symm
      simpa only [next, dite_eq_left (And.intro lead trail)] using congrArg (fun x => some (x, rest)) equal
  | single u p rest no value =>
      have equal : unitPoint u = p := Fin.ext value.symm
      simpa [equal] using next_single u rest no

theorem next_sound {source p rest} (value : next source = some (p, rest)) : Step source p rest := by
  cases source with
  | nil => simp [next] at value
  | cons u tail =>
      cases tail with
      | nil =>
          simp only [next, Option.some.injEq, Prod.mk.injEq] at value
          rcases value with ⟨rfl, rfl⟩
          exact .single u (unitPoint u) [] (by simp [NoPair]) rfl
      | cons v tail =>
          by_cases pair : Leading u ∧ Trailing v
          · simp only [next, dite_eq_left pair, Option.some.injEq, Prod.mk.injEq] at value
            rcases value with ⟨rfl, rfl⟩
            exact .pair u v _ _ pair.1 pair.2 rfl
          · simp only [next, dite_eq_right pair, Option.some.injEq, Prod.mk.injEq] at value
            rcases value with ⟨rfl, rfl⟩
            exact .single u _ _ (by simpa [NoPair] using pair) rfl

theorem next_iff (source : List CodeUnit) (p : CodePoint) (rest : List CodeUnit) :
    next source = some (p, rest) ↔ Step source p rest := ⟨next_sound, Step.next_result⟩

theorem next_none_iff (source : List CodeUnit) : next source = none ↔ source = [] := by
  cases source with
  | nil => simp [next]
  | cons u tail => cases tail <;> simp [next]; split <;> simp

theorem Step.exact_suffix {source p rest} (step : Step source p rest) :
    (source.length = rest.length + 1 ∧ ∃ u, source = u :: rest ∧ p.val = u.val) ∨
    (source.length = rest.length + 2 ∧ ∃ u v, source = u :: v :: rest ∧
      Leading u ∧ Trailing v ∧ p.val = (u.val - 0xd800) * 0x400 + (v.val - 0xdc00) + 0x10000) := by
  cases step with
  | pair u v p rest lead trail value => exact .inr ⟨by simp, u, v, rfl, lead, trail, value⟩
  | single u p rest no value => exact .inl ⟨by simp, u, rfl, value⟩

theorem Step.progress {source p rest} (step : Step source p rest) : rest.length < source.length := by
  cases step <;> simp <;> omega

theorem Step.decode_result {source p rest} (step : Step source p rest) : decode source = p :: decode rest := by
  cases step with
  | pair u v p rest lead trail value =>
      have equal : pairPoint u v lead trail = p := Fin.ext value.symm
      simpa only [decode, dite_eq_left (And.intro lead trail)] using congrArg (fun x => x :: decode rest) equal
  | single u p rest no value =>
      have equal : unitPoint u = p := Fin.ext value.symm
      simpa [equal] using decode_single u rest no

theorem Decoded.result {source output} (parsed : Decoded source output) : decode source = output := by
  induction parsed with
  | empty => rfl
  | cons step parsed ih => rw [step.decode_result, ih]

theorem decode_sound (source : List CodeUnit) : Decoded source (decode source) := by
  cases source with
  | nil => exact .empty
  | cons u tail =>
      cases tail with
      | nil => exact .cons (.single u _ [] (by simp [NoPair]) rfl) .empty
      | cons v tail =>
          by_cases pair : Leading u ∧ Trailing v
          · simp only [decode, dite_eq_left pair]
            exact .cons (.pair u v _ _ pair.1 pair.2 rfl) (decode_sound tail)
          · simp only [decode, dite_eq_right pair]
            exact .cons (.single u _ _ (by simpa [NoPair] using pair) rfl) (decode_sound (v :: tail))
termination_by source.length

theorem decode_iff (source : List CodeUnit) (output : List CodePoint) :
    decode source = output ↔ Decoded source output := by
  constructor
  · intro same; rw [← same]; exact decode_sound source
  · exact Decoded.result

theorem Decoded.unique {source left right} (hl : Decoded source left) (hr : Decoded source right) :
    left = right := hl.result.symm.trans hr.result

theorem Decoded.length_bounds {source output} (parsed : Decoded source output) :
    output.length ≤ source.length ∧ source.length ≤ 2 * output.length := by
  induction parsed with
  | empty => simp
  | cons step parsed ih =>
      have sizes := step.exact_suffix
      simp only [List.length_cons]
      rcases sizes with ⟨size, _⟩ | ⟨size, _⟩ <;> omega

theorem preprocess_iff (source : List CodeUnit) (output : List Char) :
    preprocess source = output ↔ Prepared source output := by
  constructor
  · intro same
    exact ⟨decode source, decode_sound source, (CodePointInput.preprocess_iff _ _).mp same⟩
  · rintro ⟨points, parsed, filtered⟩
    unfold preprocess
    rw [parsed.result]
    exact filtered.result

theorem preprocess_normalized (source : List CodeUnit) : CodePointInput.Normalized (preprocess source) :=
  CodePointInput.preprocess_normalized (decode source)

theorem preprocess_length_le (source : List CodeUnit) : (preprocess source).length ≤ source.length :=
  Nat.le_trans (CodePointInput.preprocess_length_le (decode source)) (decode_sound source).length_bounds.1

theorem unpaired_preserved (u : CodeUnit) (rest : List CodeUnit) (no : NoPair u rest) :
    decode (u :: rest) = unitPoint u :: decode rest := decode_single u rest no

theorem unpaired_replaced (u : CodeUnit) (rest : List CodeUnit) (no : NoPair u rest)
    (surrogate : 0xd800 ≤ u.val ∧ u.val ≤ 0xdfff) :
    preprocess (u :: rest) = '�' :: preprocess rest := by
  unfold preprocess
  rw [decode_single u rest no]
  exact CodePointInput.surrogate_cons (unitPoint u) (decode rest) surrogate

end CssSemantics.DomString
