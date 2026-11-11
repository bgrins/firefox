import ByteAdapter

namespace CssNumberLexicalBridge
open NumericDigits CssSemantics.CssNumberParts CssSemantics.CssNumberSyntax

theorem fraction_bridge (source : List Byte) :
    CssSemantics.CssNumberSyntax.optional fraction (scalars source) =
      (if (NumericParts.fraction source).used then some (scalars (NumericParts.fraction source).digits) else none,
        scalars (NumericParts.fraction source).rest) := by
  rw [NumericParts.fraction_reference]
  cases source with
  | nil => rfl
  | cons b bs =>
    by_cases dot : b.val = 46
    · have dc := (scalar_dot b).mpr dot
      by_cases empty : NumericParts.picked bs = []
      · simp [ dc, CssSemantics.CssNumberSyntax.optional, fraction, nonemptyDigits, picked_bridge,
          NumericParts.refFraction, NumericParts.emptyPart, dot, empty]
      · simp [ dc, CssSemantics.CssNumberSyntax.optional, fraction, nonemptyDigits, picked_bridge,
          NumericParts.refFraction, dot, empty]
    · have dc : scalar b ≠ '.' := by simpa [scalar_dot] using dot
      simp [ CssSemantics.CssNumberSyntax.optional, fraction, NumericParts.refFraction, NumericParts.emptyPart, dot, dc]

theorem exponent_bridge (source : List Byte) :
    CssSemantics.CssNumberSyntax.optional exponent (scalars source) =
      (if (NumericParts.exponent source).used then
        some (outerSign (source.drop 1), scalars (NumericParts.exponent source).digits) else none,
        scalars (NumericParts.exponent source).rest) := by
  rw [NumericParts.exponent_reference]
  cases source with
  | nil => rfl
  | cons b bs =>
    by_cases marker : b.val = 69 ∨ b.val = 101
    · have mc := (scalar_exponent b).mpr marker
      by_cases empty : NumericParts.picked (NumericEntry.stripSign bs) = []
      · simp [ CssSemantics.CssNumberSyntax.optional, exponent, mc, sign_bridge, nonemptyDigits,
          picked_bridge, NumericParts.refExponent, NumericParts.emptyPart, marker, empty]
      · simp [ CssSemantics.CssNumberSyntax.optional, exponent, mc, sign_bridge, nonemptyDigits,
          picked_bridge, NumericParts.refExponent, marker, empty]
    · have mc : ¬ (scalar b = 'e' ∨ scalar b = 'E') := by simpa [scalar_exponent] using marker
      simp [ CssSemantics.CssNumberSyntax.optional, exponent, mc, NumericParts.refExponent, NumericParts.emptyPart, marker]

theorem fraction_selected_digits (source : List Byte) :
    (if (NumericParts.fraction source).used then some (scalars (NumericParts.fraction source).digits) else none).getD [] =
      scalars (NumericParts.fraction source).digits := by
  unfold NumericParts.fraction
  split <;> rfl

theorem exponent_selected_digits (source : List Byte) :
    ((if (NumericParts.exponent source).used then
      some (outerSign (source.drop 1), scalars (NumericParts.exponent source).digits) else none).map Prod.snd).getD [] =
      scalars (NumericParts.exponent source).digits := by
  unfold NumericParts.exponent
  split <;> rfl

theorem optional_isNone (flag : Bool) (value : α) :
    (if flag then some value else none).isNone = !flag := by cases flag <;> rfl

end CssNumberLexicalBridge
