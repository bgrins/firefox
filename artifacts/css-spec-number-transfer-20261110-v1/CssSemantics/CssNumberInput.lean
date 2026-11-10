import CssSemantics.CssNumberLaws
import CssSemantics.CssInput

namespace CssSemantics.CssNumberSyntax

open CssNumberParts

def Decimal.Valid (decimal : Decimal) : Prop :=
  (∀ c ∈ decimal.integer, c.isDigit = true) ∧
  (∀ digits, decimal.fraction = some digits → digits ≠ [] ∧ ∀ c ∈ digits, c.isDigit = true) ∧
  (∀ value, decimal.exponent = some value → value.2 ≠ [] ∧ ∀ c ∈ value.2, c.isDigit = true) ∧
  (decimal.integer ≠ [] ∨ decimal.fraction ≠ none)

theorem Parsed.valid {source result} (parsed : Parsed source result) : result.decimal.Valid := by
  rcases result with ⟨⟨signValue, integerValue, fractionValue, exponentValue⟩, remainder⟩
  obtain ⟨⟨startSign, startRest, startSigned, start⟩, afterSign, afterInteger, afterFraction,
    signed, integer, fraction, exponent⟩ := parsed
  have same := startSigned.result.symm.trans signed.result
  cases same
  refine ⟨integer.digits, ?_, ?_, ?_⟩
  · intro digits equal
    cases fraction with
    | absent => contradiction
    | present parsed =>
        cases equal
        cases parsed with
        | parsed digits => exact ⟨digits.2, digits.1.digits⟩
  · intro value equal
    cases exponent with
    | absent => contradiction
    | present parsed =>
        cases equal
        cases parsed with
        | parsed _ _ _ digits => exact ⟨digits.2, digits.1.digits⟩
  · cases start with
    | digit c tail yes => exact Or.inl (integer.nonempty_of_head yes)
    | fraction c tail yes =>
        cases integer with
        | stop _ _ _ =>
            cases fraction with
            | absent missing =>
                have digits := takeDigits_sound (c :: tail)
                exact False.elim (missing _ _ (.parsed ⟨digits, digits.nonempty_of_head yes⟩))
            | present => exact Or.inr (by simp)
        | next c yes tail => contradiction

def parseInput (source : List Char) : Option Result := parse (CssInput.preprocess source)

def InputParsed (source : List Char) (result : Result) : Prop :=
  ∃ normalized, CssInput.Preprocess source normalized ∧ Parsed normalized result

theorem parseInput_iff (source : List Char) (result : Result) : parseInput source = some result ↔ InputParsed source result := by
  rw [parseInput, parse_iff]
  constructor
  · intro parsed; exact ⟨_, CssInput.preprocess_sound source, parsed⟩
  · rintro ⟨normalized, processed, parsed⟩; simpa [processed.result] using parsed

theorem InputParsed.valid {source result} (parsed : InputParsed source result) : result.decimal.Valid := by
  obtain ⟨normalized, processed, parsed⟩ := parsed
  exact parsed.valid

theorem InputParsed.progress {source result} (parsed : InputParsed source result) : result.rest.length < source.length := by
  obtain ⟨normalized, processed, parsed⟩ := parsed
  have progress := parsed.progress
  have bounded := processed.length_le
  omega

theorem InputParsed.rest_normalized {source result} (parsed : InputParsed source result) : CssInput.Normalized result.rest := by
  obtain ⟨normalized, processed, parsed⟩ := parsed
  obtain ⟨consumed, equal⟩ := parsed.2.decomposition
  have normal := processed.normalized
  rw [equal] at normal
  exact fun c member => normal c (by simp [member])

end CssSemantics.CssNumberSyntax
