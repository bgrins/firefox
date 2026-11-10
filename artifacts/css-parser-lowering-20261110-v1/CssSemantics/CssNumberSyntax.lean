import CssSemantics.CssNumberParts

namespace CssSemantics.CssNumberSyntax

open CssNumberParts

def nonemptyDigits (source : List Char) : Option (List Char × List Char) :=
  let result := takeDigits source
  if result.1 = [] then none else some result

def NonemptyDigits (source digits rest : List Char) : Prop := Digits source digits rest ∧ digits ≠ []

theorem nonemptyDigits_iff (source digits rest : List Char) :
    nonemptyDigits source = some (digits, rest) ↔ NonemptyDigits source digits rest := by
  unfold nonemptyDigits NonemptyDigits
  dsimp only
  split
  next empty =>
    constructor
    · intro impossible; cases impossible
    · rintro ⟨parsed, nonempty⟩
      have equal := parsed.result
      simp only [equal] at empty
      contradiction
  next nonempty =>
    simp only [Option.some.injEq]
    constructor
    · intro equal; exact ⟨(takeDigits_iff _ _ _).mp equal, by simpa [equal] using nonempty⟩
    · rintro ⟨parsed, _⟩; exact parsed.result

def fraction : List Char → Option (List Char × List Char)
  | '.' :: rest => nonemptyDigits rest
  | _ => none

inductive Fraction : List Char → List Char → List Char → Prop where
  | parsed {source digits rest} : NonemptyDigits source digits rest → Fraction ('.' :: source) digits rest

theorem fraction_iff (source digits rest : List Char) :
    fraction source = some (digits, rest) ↔ Fraction source digits rest := by
  constructor
  · intro accepted
    unfold fraction at accepted
    split at accepted
    · exact .parsed ((nonemptyDigits_iff _ _ _).mp accepted)
    · contradiction
  · intro accepted
    cases accepted with
    | parsed digits => exact (nonemptyDigits_iff _ _ _).mpr digits

def exponent : List Char → Option ((Option Sign × List Char) × List Char)
  | e :: source =>
      if e = 'e' ∨ e = 'E' then
        let signed := sign source
        (nonemptyDigits signed.2).map fun digits => ((signed.1, digits.1), digits.2)
      else none
  | [] => none

inductive Exponent : List Char → (Option Sign × List Char) → List Char → Prop where
  | parsed (e) {source signed sign digits rest} : e = 'e' ∨ e = 'E' →
      Signed source sign signed → NonemptyDigits signed digits rest →
      Exponent (e :: source) (sign, digits) rest

theorem exponent_iff (source : List Char) (value : Option Sign × List Char) (rest : List Char) :
    exponent source = some (value, rest) ↔ Exponent source value rest := by
  constructor
  · intro accepted
    cases source with
    | nil => simp [exponent] at accepted
    | cons e source =>
        simp only [exponent] at accepted
        split at accepted
        next yes =>
          obtain ⟨digits, found, equal⟩ := Option.map_eq_some_iff.mp accepted
          rcases digits with ⟨digits, remaining⟩
          cases equal
          exact .parsed e yes (sign_sound source) ((nonemptyDigits_iff _ _ _).mp found)
        next no => simp at accepted
  · intro accepted
    cases accepted with
    | parsed e yes signed digits =>
        simp only [exponent, yes, ↓reduceIte, signed.result]
        rw [(nonemptyDigits_iff _ _ _).mpr digits]
        rfl

def optional {α : Type} (parser : List Char → Option (α × List Char)) (source : List Char) : Option α × List Char :=
  match parser source with
  | some (value, rest) => (some value, rest)
  | none => (none, source)

inductive Optional {α : Type} (grammar : List Char → α → List Char → Prop) : List Char → Option α → List Char → Prop where
  | absent (source) : (∀ value rest, ¬ grammar source value rest) → Optional grammar source none source
  | present {source value rest} : grammar source value rest → Optional grammar source (some value) rest

theorem optional_iff {α : Type} (parser : List Char → Option (α × List Char))
    (grammar : List Char → α → List Char → Prop)
    (correct : ∀ source value rest, parser source = some (value, rest) ↔ grammar source value rest)
    (source : List Char) (value : Option α) (rest : List Char) :
    optional parser source = (value, rest) ↔ Optional grammar source value rest := by
  constructor
  · intro accepted
    unfold optional at accepted
    split at accepted
    next v r found => cases accepted; exact .present ((correct _ _ _).mp found)
    next missing =>
      cases accepted
      exact .absent source (by intro v r parsed; have := (correct _ _ _).mpr parsed; simp_all)
  · intro accepted
    cases accepted with
    | absent missing =>
        unfold optional
        split
        next v r found => exact False.elim (missing v r ((correct _ _ _).mp found))
        next missing => rfl
    | present parsed => simp [optional, (correct _ _ _).mpr parsed]

structure Decimal where
  sign : Option Sign
  integer : List Char
  fraction : Option (List Char)
  exponent : Option (Option Sign × List Char)
  deriving DecidableEq, Repr

structure Result where
  decimal : Decimal
  rest : List Char
  deriving DecidableEq, Repr

def consume (source : List Char) : Result :=
  let signed := sign source
  let integer := takeDigits signed.2
  let fraction := optional fraction integer.2
  let exponent := optional exponent fraction.2
  ⟨⟨signed.1, integer.1, fraction.1, exponent.1⟩, exponent.2⟩

def Consumed (source : List Char) (result : Result) : Prop :=
  ∃ afterSign afterInteger afterFraction,
    Signed source result.decimal.sign afterSign ∧
    Digits afterSign result.decimal.integer afterInteger ∧
    Optional Fraction afterInteger result.decimal.fraction afterFraction ∧
    Optional Exponent afterFraction result.decimal.exponent result.rest

theorem consume_sound (source : List Char) : Consumed source (consume source) := by
  unfold Consumed consume
  exact ⟨_, _, _, sign_sound source, takeDigits_sound _,
    (optional_iff fraction Fraction fraction_iff _ _ _).mp rfl,
    (optional_iff exponent Exponent exponent_iff _ _ _).mp rfl⟩

theorem Consumed.result {source result} (parsed : Consumed source result) : consume source = result := by
  obtain ⟨afterSign, afterInteger, afterFraction, signed, integer, fraction, exponent⟩ := parsed
  have frac := (optional_iff _ _ fraction_iff _ _ _).mpr fraction
  have exp := (optional_iff _ _ exponent_iff _ _ _).mpr exponent
  simp only [consume, signed.result, integer.result, frac, exp]

def parse (source : List Char) : Option Result := if startsNumber source then some (consume source) else none

def Parsed (source : List Char) (result : Result) : Prop := StartsNumber source ∧ Consumed source result

theorem consume_iff (source : List Char) (result : Result) : consume source = result ↔ Consumed source result :=
  ⟨fun equal => equal ▸ consume_sound source, Consumed.result⟩

theorem parse_iff (source : List Char) (result : Result) : parse source = some result ↔ Parsed source result := by
  unfold parse Parsed
  split
  next yes => simp [consume_iff, (startsNumber_iff source).mp yes]
  next no => simp [show ¬ StartsNumber source from fun yes => no ((startsNumber_iff source).mpr yes)]

end CssSemantics.CssNumberSyntax
