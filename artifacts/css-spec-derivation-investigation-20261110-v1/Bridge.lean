import Generated
import CssSemantics.CssEscape
import CssSemantics.CssInput

namespace CssDerivation

theorem afterBackslash (source : List Char) :
    validEscape (some '\\') source.head? = CssSemantics.CssEscape.validAfter source := by
  cases source with
  | nil => rfl
  | cons c rest =>
      by_cases h : c = '\n'
      · subst c; rfl
      · simp [validEscape, CssSemantics.CssEscape.validAfter, h]

theorem afterBackslash_spec (source : List Char) :
    validEscape (some '\\') source.head? = true ↔ CssSemantics.CssEscape.ValidAfter source := by
  rw [afterBackslash]
  exact CssSemantics.CssEscape.validAfter_iff source

example : validEscape (some '\\') none = true := by decide
example : validEscape (some '\\') (some '\n') = false := by decide
example : validEscape (some 'a') (some 'b') = false := by decide
example : validEscape (some '\\') (some '\r') = true := by decide
example : validEscape (some '\\') (CssSemantics.CssInput.preprocess ['\r']).head? = false := by decide

#print axioms afterBackslash
#print axioms afterBackslash_spec

end CssDerivation
