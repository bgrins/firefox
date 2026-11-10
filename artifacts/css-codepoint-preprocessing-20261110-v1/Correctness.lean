import CodePointInput

namespace CssSemantics.CodePointInput

theorem ofNat_value (n : Nat) (valid : n.isValidChar) : (Char.ofNat n).toNat = n := by
  rw [Char.ofNat, dite_eq_left valid]
  rfl

theorem scalar_valid (p : CodePoint) (notSurrogate : ¬ Surrogate p) : p.val.isValidChar := by
  change p.val < 0xd800 ∨ (0xdfff < p.val ∧ p.val < 0x110000)
  have bound := p.isLt
  unfold Surrogate at notSurrogate
  omega

theorem scalar_not_surrogate (p : CodePoint) (c : Char) (same : c.toNat = p.val) : ¬ Surrogate p := by
  have valid := c.valid
  change c.toNat < 0xd800 ∨ (0xdfff < c.toNat ∧ c.toNat < 0x110000) at valid
  unfold Surrogate
  omega

theorem Point.result {p c} (converted : Point p c) : point p = c := by
  cases converted with
  | carriageReturn equal => simp [point, equal]
  | formFeed equal => simp [point, equal]
  | null equal => simp [point, equal]
  | surrogate surrogate =>
      have cr : p.val ≠ 0x0d := by unfold Surrogate at surrogate; omega
      have ff : p.val ≠ 0x0c := by unfold Surrogate at surrogate; omega
      rw [point, ite_eq_right (not_or_intro cr ff), ite_eq_left (Or.inr surrogate)]
  | ordinary p same cr ff nul =>
      have noSurrogate := scalar_not_surrogate p c same
      rw [point, ite_eq_right (not_or_intro cr ff), ite_eq_right (not_or_intro nul noSurrogate), ← same, Char.ofNat_toNat]

theorem point_sound (p : CodePoint) : Point p (point p) := by
  by_cases cr : p.val = 0x0d
  · simpa [point, cr] using Point.carriageReturn p cr
  by_cases ff : p.val = 0x0c
  · simpa [point, ff] using Point.formFeed p ff
  by_cases nul : p.val = 0
  · simpa [point, nul] using Point.null p nul
  by_cases surrogate : Surrogate p
  · rw [point, ite_eq_right (not_or_intro cr ff), ite_eq_left (Or.inr surrogate)]
    exact Point.surrogate p surrogate
  · have same := ofNat_value p.val (scalar_valid p surrogate)
    simpa [point, cr, ff, nul, surrogate] using Point.ordinary p (Char.ofNat p.val) same cr ff nul

theorem point_iff (p : CodePoint) (c : Char) : point p = c ↔ Point p c :=
  ⟨fun equal => equal ▸ point_sound p, Point.result⟩

theorem preprocess_cons {p rest} (notPair : NotPair p rest) :
    preprocess (p :: rest) = point p :: preprocess rest := by
  cases rest with
  | nil => rfl
  | cons q tail =>
      have no := notPair q tail rfl
      simp [preprocess, no]

theorem Preprocess.result {source output} (parsed : Preprocess source output) : preprocess source = output := by
  induction parsed with
  | empty => rfl
  | crlf cr lf tail ih => simp [preprocess, cr, lf, ih]
  | single noPair converted tail ih => rw [preprocess_cons noPair, converted.result, ih]

theorem preprocess_sound (source : List CodePoint) : Preprocess source (preprocess source) := by
  cases source with
  | nil => exact .empty
  | cons p rest =>
      cases rest with
      | nil => exact .single (by simp [NotPair]) (point_sound p) .empty
      | cons q tail =>
          by_cases pair : p.val = 0x0d ∧ q.val = 0x0a
          · simpa [preprocess, pair] using Preprocess.crlf pair.1 pair.2 (preprocess_sound tail)
          · have noPair : NotPair p (q :: tail) := by
              intro d remaining equal
              rcases List.cons.inj equal with ⟨rfl, rfl⟩
              exact pair
            rw [preprocess_cons noPair]
            exact .single noPair (point_sound p) (preprocess_sound (q :: tail))
termination_by source.length

theorem preprocess_iff (source : List CodePoint) (output : List Char) :
    preprocess source = output ↔ Preprocess source output :=
  ⟨fun equal => equal ▸ preprocess_sound source, Preprocess.result⟩

theorem Preprocess.unique {source left right} (hl : Preprocess source left) (hr : Preprocess source right) :
    left = right := hl.result.symm.trans hr.result

theorem Point.normalized {p c} (converted : Point p c) : c ≠ '\r' ∧ c ≠ '\x0c' ∧ c ≠ '\x00' := by
  cases converted with
  | carriageReturn | formFeed | null | surrogate => decide
  | ordinary p same cr ff nul =>
      constructor
      · intro equal; subst c; simp at same; omega
      constructor
      · intro equal; subst c; simp at same; omega
      · intro equal; subst c; simp at same; omega

theorem Preprocess.normalized {source output} (parsed : Preprocess source output) : Normalized output := by
  induction parsed with
  | empty => simp [Normalized]
  | crlf cr lf tail ih => simpa [Normalized] using ih
  | single noPair converted tail ih => simpa [Normalized] using And.intro converted.normalized ih

theorem preprocess_normalized (source : List CodePoint) : Normalized (preprocess source) :=
  (preprocess_sound source).normalized

theorem Preprocess.length_le {source output} (parsed : Preprocess source output) : output.length ≤ source.length := by
  induction parsed with
  | empty => simp
  | crlf cr lf tail ih => simp; omega
  | single noPair converted tail ih => simpa using ih

theorem preprocess_length_le (source : List CodePoint) : (preprocess source).length ≤ source.length :=
  (preprocess_sound source).length_le

theorem surrogate_cons (p : CodePoint) (rest : List CodePoint) (surrogate : Surrogate p) :
    preprocess (p :: rest) = '�' :: preprocess rest := by
  have cr : p.val ≠ 0x0d := by unfold Surrogate at surrogate; omega
  have noPair : NotPair p rest := by
    intro q tail equal pair
    exact cr pair.1
  rw [preprocess_cons noPair, (Point.surrogate p surrogate).result]

theorem ofNat?_none_iff (n : Nat) : ofNat? n = none ↔ 0x110000 ≤ n := by
  unfold ofNat?
  split <;> simp_all

#print axioms preprocess_iff
#print axioms preprocess_normalized
#print axioms preprocess_length_le
#print axioms surrogate_cons
#print axioms ofNat?_none_iff

end CssSemantics.CodePointInput
