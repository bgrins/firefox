import CssDerivation.NumberLexical.ByteAdapter

namespace CssNumberLexicalBridge
open NumericDigits CssSemantics.CssNumberParts

theorem unsigned_entry_bridge (source : List Byte) :
    unsignedStart (scalars source) = (source.head?.any NumericDigits.digit || NumericEntry.dotDigit source) := by
  cases source with
  | nil => rfl
  | cons b bs =>
    by_cases dot : b.val = 46
    · have dc := (scalar_dot b).mpr dot
      have nd := NumericEntry.dot_not_digit b dot
      cases bs <;> simp [unsignedStart, NumericEntry.dotDigit, scalar_digit, dc, dot, nd]
    · have dc : scalar b ≠ '.' := by simpa [scalar_dot] using dot
      cases bs <;> simp [unsignedStart, NumericEntry.dotDigit, scalar_digit, dc, dot]

theorem entry_bridge (source : List Byte) :
    startsNumber (scalars source) = NumericEntry.nativeStart source := by
  rw [startsNumber_sign, sign_bridge, NumericEntry.entry_reference]
  simp only [unsigned_entry_bridge, NumericEntry.dot_head_shape, NumericEntry.referenceStart]
  have classifiers : NumericDigits.referenceDigit = NumericDigits.digit :=
    funext (fun b => (NumericDigits.classifier b).symm)
  cases NumericEntry.stripSign source <;> simp [classifiers]

theorem caller_domain (source : List Byte) :
    StartsNumber (scalars source) ↔ NumericEntry.nativeStart source = true := by
  rw [← startsNumber_iff, entry_bridge]

end CssNumberLexicalBridge
