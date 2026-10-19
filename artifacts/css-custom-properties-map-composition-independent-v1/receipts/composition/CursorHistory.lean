import Contracts

namespace MapIterator

variable {K V : Type} [DecidableEq K]

def Coherent (c : Chain K V) (s : Cursor K V) : Prop :=
  c = s.descendants ++ s.current :: s.parents ∧
  ∃ consumed, s.current = consumed ++ s.suffix

omit [DecidableEq K] in
theorem start_coherent (n : Node K V) (ps : Chain K V) :
    Coherent (n :: ps) (start (n :: ps)) := by
  exact ⟨rfl, [], rfl⟩

theorem step_coherent (c : Chain K V) (s t : Cursor K V)
    (hc : Coherent c s) (h : step s = .skip t ∨ ∃ e, step s = .yield e t) :
    Coherent c t := by
  rcases s with ⟨cur, suf, ps, ds⟩
  rcases hc with ⟨hc, consumed, hcur⟩
  cases suf with
  | nil =>
    cases ps with
    | nil => simp [step] at h
    | cons p ps =>
      simp [step] at h
      subst t
      constructor
      · simpa [List.append_assoc] using hc
      · exact ⟨[], rfl⟩
  | cons e rest =>
    simp only [step] at h
    have ready : Coherent c ⟨cur, rest, ps, ds⟩ := by
      refine ⟨hc, consumed ++ [e], ?_⟩
      simpa [List.append_assoc] using hcur
    split at h
    · rcases h with h | ⟨a,h⟩
      · cases h; exact ready
      · cases h
    · rcases h with h | ⟨a,h⟩
      · cases h
      · cases h; exact ready

inductive Reached : Cursor K V → Cursor K V → Prop where
  | initial : Reached s s
  | advance (prior : Reached s t)
      (h : step t = .skip u ∨ ∃ e, step t = .yield e u) : Reached s u

theorem reached_coherent {c : Chain K V} {s t : Cursor K V}
    (hc : Coherent c s) (h : Reached s t) : Coherent c t := by
  induction h with
  | initial => exact hc
  | advance prior h ih => exact step_coherent _ _ _ ih h

inductive Next : Cursor K V → Option (Entry K V × Cursor K V) → Prop where
  | done (h : step s = .done) : Next s none
  | skip (h : step s = .skip t) (tail : Next t result) : Next s result
  | yield (h : step s = .yield e t) : Next s (some (e,t))

theorem next_suffix {s : Cursor K V} {result : Option (Entry K V × Cursor K V)}
    (h : Next s result) :
    match result with
    | none => drain s = []
    | some (e,t) => drain s = e :: drain t := by
  induction h with
  | @done s h => have hs := step_drain s; simpa [h] using hs
  | @skip s t result h tail ih =>
    have hs := step_drain s
    simp only [h] at hs
    cases result with
    | none => simpa only [hs] using ih
    | some pair => rcases pair with ⟨e,u⟩; simpa only [hs] using ih
  | @yield s e t h => have hs := step_drain s; simpa [h] using hs

theorem next_terminates (s : Cursor K V) : ∃ result, Next s result := by
  cases hs : step s with
  | done => exact ⟨none, .done hs⟩
  | skip t =>
    obtain ⟨r,hr⟩ := next_terminates t
    exact ⟨r, .skip hs hr⟩
  | yield e t => exact ⟨some (e,t), .yield hs⟩
termination_by rank s
decreasing_by exact step_rank s t (Or.inl hs)

theorem reached_trans {s t u : Cursor K V} (a : Reached s t) (b : Reached t u) :
    Reached s u := by
  induction b with
  | initial => exact a
  | advance prior h ih => exact .advance ih h

theorem next_reached {s t : Cursor K V} {e : Entry K V}
    (h : Next s (some (e,t))) : Reached s t := by
  generalize hr : some (e,t) = r at h
  induction h with
  | done h => cases hr
  | @yield s a u h => cases hr; exact .advance .initial (Or.inr ⟨e,h⟩)
  | @skip s u result h tail ih =>
    have prior : Reached s u := .advance .initial (Or.inl h)
    exact reached_trans prior (ih hr)

theorem next_preserves_cursor {c : Chain K V} {s t : Cursor K V} {e : Entry K V}
    (hc : Coherent c s) (h : Next s (some (e,t))) : Coherent c t :=
  reached_coherent hc (next_reached h)

end MapIterator
