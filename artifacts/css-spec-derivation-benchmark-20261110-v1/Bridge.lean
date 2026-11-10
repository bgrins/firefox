import GeneratedValidEscape
import GeneratedNumberStart
import CssSemantics.CssEscape
import CssSemantics.CssNumberParts

namespace CssDerivation

theorem escape_equivalent (source : List Char) :
    validEscape (some '\\') source.head? none = CssSemantics.CssEscape.validAfter source := by
  cases source with
  | nil => rfl
  | cons c rest =>
      by_cases h : c = '\n'
      · subst c; rfl
      · simp [validEscape, CssSemantics.CssEscape.validAfter, h]

theorem escape_spec (source : List Char) :
    validEscape (some '\\') source.head? none = true ↔ CssSemantics.CssEscape.ValidAfter source := by
  rw [escape_equivalent]
  exact CssSemantics.CssEscape.validAfter_iff source

theorem number_expression (a b c : Option Char) :
    numberStart a b c =
      if a == some '+' || a == some '-' then
        b.any Char.isDigit || (b == some '.' && c.any Char.isDigit)
      else if a == some '.' then b.any Char.isDigit else a.any Char.isDigit := by
  change (if a == some '+' || a == some '-' then
      (if b.any Char.isDigit then true else
        (if b == some '.' && c.any Char.isDigit then true else false))
    else if a == some '.' then (if b.any Char.isDigit then true else false)
    else if a.any Char.isDigit then true else false) = _
  cases ha : (a == some '+' || a == some '-') <;>
    cases hd : (a == some '.') <;>
    cases hb : b.any Char.isDigit <;>
    cases hbd : (b == some '.') <;> simp_all

theorem number_equivalent (source : List Char) :
    (observeNumberStart source).1 = CssSemantics.CssNumberParts.startsNumber source := by
  cases source with
  | nil => rfl
  | cons a rest =>
      cases rest with
      | nil =>
          by_cases hp : a = '+' <;> by_cases hm : a = '-' <;> by_cases hd : a = '.' <;>
            simp_all [observeNumberStart, number_expression, CssSemantics.CssNumberParts.startsNumber,
              CssSemantics.CssNumberParts.unsignedStart]
      | cons b tail =>
          cases tail with
          | nil =>
              by_cases hp : a = '+' <;> by_cases hm : a = '-' <;> by_cases hd : a = '.' <;>
                by_cases hb : b = '.' <;>
                simp_all [observeNumberStart, number_expression, CssSemantics.CssNumberParts.startsNumber,
                  CssSemantics.CssNumberParts.unsignedStart, Char.isDigit]
          | cons c tail =>
              by_cases hp : a = '+' <;> by_cases hm : a = '-' <;> by_cases hd : a = '.' <;>
                by_cases hb : b = '.' <;>
                simp_all [observeNumberStart, number_expression, CssSemantics.CssNumberParts.startsNumber,
                  CssSemantics.CssNumberParts.unsignedStart, Char.isDigit]

theorem number_spec (source : List Char) :
    (observeNumberStart source).1 = true ↔ CssSemantics.CssNumberParts.StartsNumber source := by
  rw [number_equivalent]
  exact CssSemantics.CssNumberParts.startsNumber_iff source

theorem escape_preserves (source : List Char) : (observeValidEscape source).2 = source := rfl
theorem number_preserves (source : List Char) : (observeNumberStart source).2 = source := rfl

example : validEscape (some '\\') none none = true := by decide
example : validEscape (some '\\') (some '\n') none = false := by decide
example : (observeNumberStart "+.0".toList).1 = true := by decide
example : (observeNumberStart "-.9".toList).1 = true := by decide
example : (observeNumberStart "9".toList).1 = true := by decide
example : (observeNumberStart "+.".toList).1 = false := by decide
example : (observeNumberStart "٠".toList).1 = false := by decide
example : (observeNumberStart "0x".toList).2 = "0x".toList := by decide

#print axioms escape_equivalent
#print axioms escape_spec
#print axioms number_equivalent
#print axioms number_spec
#print axioms escape_preserves
#print axioms number_preserves

end CssDerivation
