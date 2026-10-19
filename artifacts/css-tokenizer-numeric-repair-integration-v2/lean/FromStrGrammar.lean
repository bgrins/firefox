import NumericScanner
set_option maxRecDepth 4096
namespace FromStrGrammar
open NumericDigits NumericEntry NumericParts

def IsDigit (b : Byte) : Prop := b.val ∈ [48,49,50,51,52,53,54,55,56,57]
def Digits (xs : List Byte) : Prop := ∀ b ∈ xs, IsDigit b

inductive Sign : List Byte → Prop where
  | none : Sign []
  | plus : Sign [43]
  | minus : Sign [45]

inductive Mantissa : List Byte → Prop where
  | integer (ds : List Byte) : Digits ds → ds ≠ [] → Mantissa ds
  | decimal (a b : List Byte) : Digits a → Digits b → b ≠ [] → Mantissa (a ++ [46] ++ b)

inductive Exponent : List Byte → Prop where
  | none : Exponent []
  | some (e : Byte) (sg ds : List Byte) : e.val = 69 ∨ e.val = 101 →
      Sign sg → Digits ds → ds ≠ [] → Exponent ([e] ++ sg ++ ds)

inductive FiniteFloat : List Byte → Prop where
  | number (sg mant expo : List Byte) : Sign sg → Mantissa mant → Exponent expo →
      FiniteFloat (sg ++ mant ++ expo)

theorem digit_domain : ∀ b : Byte, digit b = true ↔ IsDigit b := by
  unfold IsDigit
  decide

theorem scan_digits (xs : List Byte) : Digits (scan xs).digits := by
  intro b hb
  exact (digit_domain b).mp (consumed_digits xs b hb)

theorem scan_nonempty (xs : List Byte) (h : xs.head?.any digit = true) : (scan xs).digits ≠ [] := by
  rw [digits_picked]
  exact (picked_nonempty xs).mpr h

theorem sign_admitted (xs : List Byte) : Sign (NumericLexical.signText xs) := by
  cases xs with
  | nil => exact Sign.none
  | cons b bs =>
    cases hs : signByte b
    · simpa [NumericLexical.signText,hasSign,hs] using Sign.none
    · have hb : b.val = 43 ∨ b.val = 45 := by simpa [signByte] using hs
      have hbs : Sign [b] := by
        rcases hb with hb | hb
        · have he : b = 43 := Fin.ext hb
          rw [he]; exact Sign.plus
        · have he : b = 45 := Fin.ext hb
          rw [he]; exact Sign.minus
      simpa [NumericLexical.signText,hasSign,hs] using hbs

theorem empty_integral_fraction (xs : List Byte) (h : nativeStart xs = true)
    (hi : (scan (stripSign xs)).digits = []) : dotDigit (scan (stripSign xs)).rest = true := by
  have hr := NumericLexical.scan_empty_rest _ hi
  have hd : (stripSign xs).head?.any digit = false := by
    cases hz : (stripSign xs).head?.any digit
    · rfl
    · exact False.elim (scan_nonempty _ hz hi)
  have he := entry_first_digit_or_fraction xs h
  simpa [hr,hd] using he

theorem mantissa_admitted (xs : List Byte) (h : nativeStart xs = true) :
    Mantissa ((scan (stripSign xs)).digits ++ (fraction (scan (stripSign xs)).rest).text) := by
  cases hf : dotDigit (scan (stripSign xs)).rest
  · have hn : (scan (stripSign xs)).digits ≠ [] := by
      intro hi
      have hc := empty_integral_fraction xs h hi
      simp [hf] at hc
    simpa [fraction,hf,emptyPart] using Mantissa.integer _ (scan_digits _) hn
  · have he := fraction_entry _ hf
    have hn := scan_nonempty _ he.1
    cases hr : (scan (stripSign xs)).rest with
    | nil => simp [hr,dotDigit] at hf
    | cons b bs =>
      have hb : b = 46 := by
        apply Fin.ext
        change b.val = 46
        cases bs <;> simp_all [dotDigit]
      have hg : (scan bs).digits ≠ [] := by simpa [hr] using hn
      have hm := Mantissa.decimal (scan (stripSign xs)).digits (scan bs).digits (scan_digits _) (scan_digits _) hg
      have hf' : dotDigit (46::bs) = true := by simpa [hr,hb] using hf
      simpa [fraction,hr,hb,hf'] using hm

theorem exponent_admitted (xs : List Byte) : Exponent (exponent xs).text := by
  cases hg : exponentGuard xs
  · simpa [exponent,hg,emptyPart] using Exponent.none
  · have he := exponent_entry xs hg
    have hn := scan_nonempty _ he.1
    cases xs with
    | nil => simp [exponentGuard] at hg
    | cons b bs =>
      have hb : b.val = 69 ∨ b.val = 101 := by cases bs <;> simp_all [exponentGuard,exponentByte]
      have hd : (scan (stripSign bs)).digits ≠ [] := by simpa using hn
      have hm := Exponent.some b (NumericLexical.signText bs) (scan (stripSign bs)).digits hb
        (sign_admitted bs) (scan_digits _) hd
      simpa [exponent,hg,NumericLexical.signText,List.append_assoc] using hm

theorem numeric_grammar (xs : List Byte) (h : nativeStart xs = true) :
    FiniteFloat (NumericLexical.native xs).text := by
  have hm := mantissa_admitted xs h
  have he := exponent_admitted (fraction (scan (stripSign xs)).rest).rest
  have hg := FiniteFloat.number (NumericLexical.signText xs) _ _ (sign_admitted xs) hm he
  simpa [NumericLexical.native,List.append_assoc] using hg

inductive RustMantissa : List Byte → Prop where
  | integer (ds : List Byte) : Digits ds → ds ≠ [] → RustMantissa ds
  | trailing (a b : List Byte) : Digits a → a ≠ [] → Digits b → RustMantissa (a ++ [46] ++ b)
  | fractional (a b : List Byte) : Digits a → Digits b → b ≠ [] → RustMantissa (a ++ [46] ++ b)

inductive RustFiniteNumber : List Byte → Prop where
  | number (sg mant expo : List Byte) : Sign sg → RustMantissa mant → Exponent expo →
      RustFiniteNumber (sg ++ mant ++ expo)

theorem subset (bytes : List Byte) (h : FiniteFloat bytes) : RustFiniteNumber bytes := by
  cases h with
  | number sg mant expo hs hm he =>
    apply RustFiniteNumber.number sg mant expo hs _ he
    cases hm with
    | integer ds hd hn => exact RustMantissa.integer _ hd hn
    | decimal a b ha hb hn => exact RustMantissa.fractional a b ha hb hn

theorem rust_grammar (xs : List Byte) (h : nativeStart xs = true) :
    RustFiniteNumber (NumericLexical.native xs).text := subset _ (numeric_grammar xs h)

#print axioms subset

#print axioms rust_grammar

#print axioms digit_domain
#print axioms scan_digits
#print axioms scan_nonempty
#print axioms sign_admitted
#print axioms empty_integral_fraction
#print axioms mantissa_admitted
#print axioms exponent_admitted
#print axioms numeric_grammar
end FromStrGrammar
