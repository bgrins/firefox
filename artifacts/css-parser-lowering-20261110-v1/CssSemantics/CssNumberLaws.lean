import CssSemantics.CssNumberSyntax

namespace CssSemantics.CssNumberParts

theorem Signed.decomposition {source value rest} (parsed : Signed source value rest) :
    ∃ consumed, source = consumed ++ rest := by
  cases parsed with
  | plus => exact ⟨['+'], rfl⟩
  | minus => exact ⟨['-'], rfl⟩
  | absent => exact ⟨[], rfl⟩

theorem Digits.nonempty_of_head {c tail digits rest} (parsed : Digits (c :: tail) digits rest)
    (yes : c.isDigit = true) : digits ≠ [] := by
  cases parsed with
  | stop _ _ no => simp_all
  | next => simp

end CssSemantics.CssNumberParts

namespace CssSemantics.CssNumberSyntax

open CssNumberParts

theorem Fraction.decomposition {source digits rest} (parsed : Fraction source digits rest) :
    source = '.' :: (digits ++ rest) ∧ digits ≠ [] := by
  cases parsed with
  | parsed digits => exact ⟨by rw [digits.1.decomposition], digits.2⟩

theorem Exponent.decomposition {source value rest} (parsed : Exponent source value rest) :
    ∃ consumed, source = consumed ++ rest ∧ consumed ≠ [] := by
  cases parsed with
  | @parsed e source signedInput signValue digitChars rest yes signed digits =>
      obtain ⟨sign, equal⟩ := signed.decomposition
      exact ⟨e :: (sign ++ digitChars), by simp [equal, digits.1.decomposition, List.append_assoc], by simp⟩

theorem Optional.decomposition {α : Type} {grammar : List Char → α → List Char → Prop}
    (decompose : ∀ source value rest, grammar source value rest → ∃ consumed, source = consumed ++ rest)
    {source value rest} (parsed : Optional grammar source value rest) :
    ∃ consumed, source = consumed ++ rest := by
  cases parsed with
  | absent => exact ⟨[], rfl⟩
  | present parsed => exact decompose _ _ _ parsed

theorem Optional.fraction_decomposition {source value rest} (parsed : Optional Fraction source value rest) :
    ∃ consumed, source = consumed ++ rest :=
  parsed.decomposition fun _ _ _ parsed => ⟨'.' :: _, by simpa using parsed.decomposition.1⟩

theorem Optional.exponent_decomposition {source value rest} (parsed : Optional Exponent source value rest) :
    ∃ consumed, source = consumed ++ rest := by
  apply parsed.decomposition
  intro source value rest parsed
  obtain ⟨consumed, equal, _⟩ := parsed.decomposition
  exact ⟨consumed, equal⟩

theorem Consumed.decomposition {source result} (parsed : Consumed source result) :
    ∃ consumed, source = consumed ++ result.rest := by
  obtain ⟨afterSign, afterInteger, afterFraction, signed, integer, fraction, exponent⟩ := parsed
  obtain ⟨sign, signEqual⟩ := signed.decomposition
  obtain ⟨frac, fracEqual⟩ := fraction.fraction_decomposition
  obtain ⟨exp, expEqual⟩ := exponent.exponent_decomposition
  exact ⟨sign ++ result.decimal.integer ++ frac ++ exp,
    by simp [signEqual, integer.decomposition, fracEqual, expEqual, List.append_assoc]⟩

theorem Consumed.rest_length_le {source result} (parsed : Consumed source result) :
    result.rest.length ≤ source.length := by
  obtain ⟨consumed, rfl⟩ := parsed.decomposition
  simp

theorem Parsed.progress {source result} (parsed : Parsed source result) :
    result.rest.length < source.length := by
  rcases result with ⟨⟨signValue, integerValue, fractionValue, exponentValue⟩, remainder⟩
  obtain ⟨⟨startSign, startRest, startSigned, start⟩, afterSign, afterInteger, afterFraction,
    signed, integer, fraction, exponent⟩ := parsed
  have same := startSigned.result.symm.trans signed.result
  cases same
  obtain ⟨sign, signEqual⟩ := signed.decomposition
  obtain ⟨exp, expEqual⟩ := exponent.exponent_decomposition
  cases start with
  | digit c tail yes =>
      have nonempty := integer.nonempty_of_head yes
      obtain ⟨frac, fracEqual⟩ := fraction.fraction_decomposition
      have equal := integer.decomposition
      have lengths := congrArg List.length signEqual
      have iLengths := congrArg List.length equal
      have fLengths := congrArg List.length fracEqual
      have eLengths := congrArg List.length expEqual
      simp only [List.length_append] at *
      have : integerValue.length > 0 := List.length_pos_iff.mpr nonempty
      omega
  | fraction c tail yes =>
      cases integer with
      | stop _ _ _ =>
          cases fraction with
          | absent missing =>
              have digits := takeDigits_sound (c :: tail)
              exact False.elim (missing _ _ (.parsed ⟨digits, digits.nonempty_of_head yes⟩))
          | present frac =>
              have equal := frac.decomposition.1
              have lengths := congrArg List.length signEqual
              have fLengths := congrArg List.length equal
              have eLengths := congrArg List.length expEqual
              simp only [List.length_append, List.length_cons] at *
              omega
      | next c yes tail => contradiction

def spelling (source : List Char) (result : Result) : List Char := source.take (source.length - result.rest.length)

theorem Consumed.spelling {source result} (parsed : Consumed source result) :
    source = spelling source result ++ result.rest := by
  obtain ⟨consumed, rfl⟩ := parsed.decomposition
  simp [CssNumberSyntax.spelling]

end CssSemantics.CssNumberSyntax
