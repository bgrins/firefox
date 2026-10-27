import CssSemantics.CssNumericCensorship

namespace CssSemantics.IntermediateCensorshipBoundary

open CssNumericClipping CssNumericCensorship CssExtendedScalar

def censoredLeaf (bounds : Bounds) (value : Value) : Value :=
  .finite (CssFiniteScalar.source (censor bounds value))

theorem late_nan_offset {bounds : Bounds} (offset : Rat)
    (lower : bounds.lower ≤ 0) (upper : 0 ≤ bounds.upper) :
    complete bounds (add .nan (.finite (CssFiniteScalar.source offset))) = 0 :=
  clip_fixed lower upper

theorem early_nan_offset (inner : Bounds) {outer : Bounds} (offset : Rat)
    (lower : outer.lower ≤ offset) (upper : offset ≤ outer.upper) :
    complete outer (add (censoredLeaf inner .nan)
      (.finite (CssFiniteScalar.source offset))) = offset := by
  change clip outer (0 + offset) = offset
  rw [Rat.zero_add]
  exact clip_fixed lower upper

theorem final_equivalence_not_contextual {bounds : Bounds} (offset : Rat)
    (zeroLower : bounds.lower ≤ 0) (zeroUpper : 0 ≤ bounds.upper)
    (lower : bounds.lower ≤ offset) (upper : offset ≤ bounds.upper)
    (nonzero : offset ≠ 0) :
    complete bounds .nan = complete bounds (zero false) ∧
    complete bounds (add .nan (.finite (CssFiniteScalar.source offset))) ≠
      complete bounds (add (censoredLeaf bounds .nan)
        (.finite (CssFiniteScalar.source offset))) := by
  constructor
  · rfl
  · rw [late_nan_offset offset zeroLower zeroUpper,
        early_nan_offset bounds offset lower upper]
    exact Ne.symm nonzero

theorem zero_basis_infinity_offset (inner : Bounds) {outer : Bounds}
    (negative negativeZero : Bool) (offset : Rat)
    (zeroLower : outer.lower ≤ 0) (zeroUpper : 0 ≤ outer.upper)
    (lower : outer.lower ≤ offset) (upper : offset ≤ outer.upper)
    (nonzero : offset ≠ 0) :
    complete outer (add (multiply (.infinity negative) (zero negativeZero))
      (.finite (CssFiniteScalar.source offset))) ≠
    complete outer (add (censoredLeaf inner
      (multiply (.infinity negative) (zero negativeZero)))
      (.finite (CssFiniteScalar.source offset))) := by
  change complete outer (add .nan (.finite (CssFiniteScalar.source offset))) ≠
    complete outer (add (censoredLeaf inner .nan) (.finite (CssFiniteScalar.source offset)))
  rw [late_nan_offset offset zeroLower zeroUpper,
      early_nan_offset inner offset lower upper]
  exact Ne.symm nonzero

#print axioms late_nan_offset
#print axioms early_nan_offset
#print axioms final_equivalence_not_contextual
#print axioms zero_basis_infinity_offset

end CssSemantics.IntermediateCensorshipBoundary
