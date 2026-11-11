import CssSemantics.AnBTokens

namespace CssSemantics.CssNumberParts

abbrev Sign := AnBTokens.Sign

def Sign.char : Sign → Char
  | .plus => '+'
  | .minus => '-'

def sign : List Char → Option Sign × List Char
  | '+' :: rest => (some .plus, rest)
  | '-' :: rest => (some .minus, rest)
  | source => (none, source)

inductive Signed : List Char → Option Sign → List Char → Prop where
  | plus (rest) : Signed ('+' :: rest) (some .plus) rest
  | minus (rest) : Signed ('-' :: rest) (some .minus) rest
  | absent (source) : (∀ rest, source ≠ '+' :: rest) → (∀ rest, source ≠ '-' :: rest) →
      Signed source none source

theorem Signed.result {source value rest} (parsed : Signed source value rest) : sign source = (value, rest) := by
  cases parsed with
  | plus => rfl
  | minus => rfl
  | absent source noPlus noMinus => unfold sign; split <;> simp_all

theorem sign_sound (source : List Char) : Signed source (sign source).1 (sign source).2 := by
  unfold sign
  split
  · exact .plus _
  · exact .minus _
  · exact .absent _ ‹_› ‹_›

theorem sign_iff (source : List Char) (value : Option Sign) (rest : List Char) :
    sign source = (value, rest) ↔ Signed source value rest := by
  constructor
  · intro equal; have parsed := sign_sound source; simpa [equal] using parsed
  · exact Signed.result

def takeDigits : List Char → List Char × List Char
  | [] => ([], [])
  | c :: rest =>
      if c.isDigit then
        let later := takeDigits rest
        (c :: later.1, later.2)
      else ([], c :: rest)

inductive Digits : List Char → List Char → List Char → Prop where
  | eof : Digits [] [] []
  | stop (c rest) : c.isDigit = false → Digits (c :: rest) [] (c :: rest)
  | next (c) {source value rest} : c.isDigit = true → Digits source value rest →
      Digits (c :: source) (c :: value) rest

theorem Digits.result {source value rest} (parsed : Digits source value rest) : takeDigits source = (value, rest) := by
  induction parsed with
  | eof => rfl
  | stop c rest noDigit => simp [takeDigits, noDigit]
  | next c yes tail ih => simp [takeDigits, yes, ih]

theorem takeDigits_sound (source : List Char) : Digits source (takeDigits source).1 (takeDigits source).2 := by
  induction source with
  | nil => exact .eof
  | cons c rest ih =>
      simp only [takeDigits]
      split
      · exact .next c ‹_› ih
      · exact .stop c rest (by simpa using ‹¬ c.isDigit = true›)

theorem takeDigits_iff (source value rest : List Char) : takeDigits source = (value, rest) ↔ Digits source value rest := by
  constructor
  · intro equal; have parsed := takeDigits_sound source; simpa [equal] using parsed
  · exact Digits.result

theorem Digits.decomposition {source value rest} (parsed : Digits source value rest) : source = value ++ rest := by
  induction parsed with
  | eof => rfl
  | stop => rfl
  | next c yes tail ih => simp [ih]

theorem Digits.digits {source value rest} (parsed : Digits source value rest) : ∀ c ∈ value, c.isDigit = true := by
  induction parsed with
  | eof => simp
  | stop => simp
  | next c yes tail ih => simpa using And.intro yes ih

theorem Digits.boundary {source value rest} (parsed : Digits source value rest) : ∀ c tail, rest = c :: tail → c.isDigit = false := by
  induction parsed with
  | eof => simp
  | stop c tail noDigit => simpa using noDigit
  | next c yes tail ih => exact ih

theorem Digits.length_le {source value rest} (parsed : Digits source value rest) : rest.length ≤ source.length := by
  rw [parsed.decomposition]
  simp

def unsignedStart : List Char → Bool
  | '.' :: c :: _ => c.isDigit
  | c :: _ => c.isDigit
  | [] => false

def startsNumber : List Char → Bool
  | '+' :: rest | '-' :: rest => unsignedStart rest
  | source => unsignedStart source

inductive UnsignedStart : List Char → Prop where
  | digit (c rest) : c.isDigit = true → UnsignedStart (c :: rest)
  | fraction (c rest) : c.isDigit = true → UnsignedStart ('.' :: c :: rest)

def StartsNumber (source : List Char) : Prop :=
  ∃ sign rest, Signed source sign rest ∧ UnsignedStart rest

theorem unsignedStart_iff (source : List Char) : unsignedStart source = true ↔ UnsignedStart source := by
  constructor
  · intro accepted
    unfold unsignedStart at accepted
    split at accepted
    · exact .fraction _ _ accepted
    · exact .digit _ _ accepted
    · contradiction
  · intro accepted
    cases accepted with
    | digit c rest yes =>
        cases rest with
        | nil => simpa [unsignedStart] using yes
        | cons d tail =>
            by_cases dot : c = '.'
            · subst c; contradiction
            · simpa [unsignedStart, dot] using yes
    | fraction c rest yes => simpa [unsignedStart] using yes

theorem startsNumber_sign (source : List Char) : startsNumber source = unsignedStart (sign source).2 := by
  unfold sign startsNumber
  split <;> rfl

theorem startsNumber_iff (source : List Char) : startsNumber source = true ↔ StartsNumber source := by
  rw [startsNumber_sign, unsignedStart_iff]
  constructor
  · intro accepted; exact ⟨_, _, sign_sound source, accepted⟩
  · rintro ⟨value, rest, parsed, accepted⟩; simpa [parsed.result] using accepted

end CssSemantics.CssNumberParts
