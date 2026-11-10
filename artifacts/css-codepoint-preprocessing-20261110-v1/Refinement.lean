import Correctness
import CssSemantics.CssInput

namespace CssSemantics.CodePointInput

theorem point_embed (c : Char) : point (embed c) = CssInput.point c := by
  have noSurrogate := scalar_not_surrogate (embed c) c rfl
  change ¬ (0xd800 ≤ c.toNat ∧ c.toNat ≤ 0xdfff) at noSurrogate
  have cr : c.toNat = 0x0d ↔ c = '\r' := Char.toNat_inj (c := c) (d := '\r')
  have ff : c.toNat = 0x0c ↔ c = '\x0c' := Char.toNat_inj (c := c) (d := '\x0c')
  have nul : c.toNat = 0 ↔ c = '\x00' := Char.toNat_inj (c := c) (d := '\x00')
  simp [point, embed, Surrogate, noSurrogate, cr, ff, nul, CssInput.point]

theorem notPair_embed {c rest} (noPair : CssInput.NotPair c rest) : NotPair (embed c) (rest.map embed) := by
  cases rest with
  | nil => simp [NotPair]
  | cons d tail =>
      have no : ¬ (c = '\r' ∧ d = '\n') := by
        rintro ⟨cr, lf⟩
        exact noPair tail ⟨cr, by simp [lf]⟩
      simpa [NotPair, embed, ← Char.toNat_inj] using no

theorem lift_preprocess {source output} (parsed : CssInput.Preprocess source output) :
    Preprocess (source.map embed) output := by
  induction parsed with
  | empty => exact .empty
  | crlf parsed ih => exact .crlf rfl rfl ih
  | single noPair converted parsed ih =>
      apply Preprocess.single (notPair_embed noPair) _ ih
      apply (point_iff _ _).mp
      rw [point_embed]
      exact (CssInput.point_iff _ _).mpr converted

theorem scalar_refinement (source : List Char) :
    preprocess (source.map embed) = CssInput.preprocess source :=
  (lift_preprocess (CssInput.preprocess_sound source)).result

theorem normalized_fixed {source : List Char} (normal : Normalized source) :
    preprocess (source.map embed) = source := by
  rw [scalar_refinement]
  exact CssInput.normalized_fixed normal

theorem normalized_iff_fixed (source : List Char) :
    preprocess (source.map embed) = source ↔ Normalized source := by
  rw [scalar_refinement]
  exact CssInput.fixed_iff source

theorem preprocess_idempotent (source : List CodePoint) :
    preprocess ((preprocess source).map embed) = preprocess source :=
  normalized_fixed (preprocess_normalized source)

theorem preserve_ordinary (source : List Char) (normal : Normalized source) :
    Preprocess (source.map embed) source := (preprocess_iff _ _).mp (normalized_fixed normal)

#print axioms scalar_refinement
#print axioms normalized_iff_fixed
#print axioms preprocess_idempotent
#print axioms preserve_ordinary

end CssSemantics.CodePointInput
