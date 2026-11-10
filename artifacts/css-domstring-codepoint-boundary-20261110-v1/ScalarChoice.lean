import Correctness

namespace CssSemantics.DomString

open CodePointInput

def scalarizePoint (p : CodePoint) : CodePoint :=
  if Surrogate p then ⟨0xfffd, by decide⟩ else p

def scalarize (source : List CodePoint) : List CodePoint := source.map scalarizePoint

theorem scalarize_ascii (p : CodePoint) (n : Nat) (small : n < 0xd800) :
    (scalarizePoint p).val = n ↔ p.val = n := by
  by_cases surrogate : Surrogate p
  · have lo := surrogate.1
    have hi := surrogate.2
    simp only [scalarizePoint, ite_eq_left surrogate]
    omega
  · simp [scalarizePoint, surrogate]

theorem point_scalarize (p : CodePoint) : point (scalarizePoint p) = point p := by
  by_cases surrogate : Surrogate p
  · have cr : p.val ≠ 0x0d := by obtain ⟨_, _⟩ := surrogate; omega
    have ff : p.val ≠ 0x0c := by obtain ⟨_, _⟩ := surrogate; omega
    have replacement : point (⟨0xfffd, by decide⟩ : CodePoint) = '�' := by decide
    rw [scalarizePoint, ite_eq_left surrogate, replacement]
    simp [point, cr, ff, surrogate]
  · simp [scalarizePoint, surrogate]

theorem notPair_scalarize (p : CodePoint) (rest : List CodePoint) (no : NotPair p rest) :
    NotPair (scalarizePoint p) (scalarize rest) := by
  cases rest with
  | nil => simp [scalarize, NotPair]
  | cons q tail =>
      have cr := scalarize_ascii p 0x0d (by decide)
      have lf := scalarize_ascii q 0x0a (by decide)
      simpa [scalarize, NotPair, cr, lf] using no

theorem Preprocess.scalarized {source output} (parsed : CodePointInput.Preprocess source output) :
    CodePointInput.Preprocess (scalarize source) output := by
  induction parsed with
  | empty => exact .empty
  | @crlf p q rest output cr lf parsed ih =>
      exact .crlf ((scalarize_ascii p 0x0d (by decide)).mpr cr)
        ((scalarize_ascii q 0x0a (by decide)).mpr lf) ih
  | @single p c rest output no converted parsed ih =>
      apply CodePointInput.Preprocess.single (notPair_scalarize p rest no) _ ih
      apply (CodePointInput.point_iff _ _).mp
      rw [point_scalarize]
      exact converted.result

theorem filter_scalarize (source : List CodePoint) :
    CodePointInput.preprocess (scalarize source) = CodePointInput.preprocess source :=
  (Preprocess.scalarized (CodePointInput.preprocess_sound source)).result

theorem choice_filter_equivalent (source : List CodeUnit) :
    CodePointInput.preprocess (scalarize (decode source)) = preprocess source :=
  filter_scalarize (decode source)

end CssSemantics.DomString
