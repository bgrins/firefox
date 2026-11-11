import NumberTree
import CssSemantics.CssNumberValue

namespace CssDerivation.NumberTransfer

open ParserIR CssSemantics CssNumberParts CssNumberSyntax

def signChars (sign : Option Sign) : Option Char := sign.map Sign.char

def exponentChars (value : Option Sign × List Char) : ExponentShape.Value := (signChars value.1, value.2)

def rawParts (decimal : Decimal) : NumberShape.Value :=
  (signChars decimal.sign, (decimal.integer, (decimal.fraction, decimal.exponent.map exponentChars)))

theorem digit_meaning (c : Char) : accepts digitPredicate c = c.isDigit := rfl

theorem scan_digits (source : List Char) : scanWhile digitPredicate source = takeDigits source := by
  induction source with
  | nil => rfl
  | cons c rest ih => simp [scanWhile, digit_meaning, takeDigits, ih]

theorem sign_run (state : State) :
    ParserIR.run signTree state = some (signChars (sign state.input).1, { state with input := (sign state.input).2 }) := by
  cases input : state.input with
  | nil =>
      simp [signTree, ParserIR.run, input, sign, signChars]
      cases state; simp_all
  | cons c rest =>
      by_cases plus : c = '+'
      · subst c; simp [signTree, ParserIR.run, input, accepts, signPredicate, FirstOrder.eval, FirstOrder.lookup, sign, signChars, Sign.char]
      by_cases minus : c = '-'
      · subst c; simp [signTree, ParserIR.run, input, accepts, signPredicate, FirstOrder.eval, FirstOrder.lookup, sign, signChars, Sign.char]
      · simp [signTree, ParserIR.run, input, accepts, signPredicate, FirstOrder.eval, FirstOrder.lookup, plus, minus, sign, signChars]
        cases state; simp_all

theorem digits_run (state : State) :
    ParserIR.run digitsTree state = some ((takeDigits state.input).1, { state with input := (takeDigits state.input).2 }) := by
  simp [digitsTree, ParserIR.run, scan_digits]

theorem nonempty_digits_run (state : State) :
    ParserIR.run nonemptyDigitsTree state = (nonemptyDigits state.input).map
      (fun (chars, rest) => (chars, { state with input := rest })) := by
  simp only [nonemptyDigitsTree, ParserIR.run, digitsTree, scan_digits, nonemptyDigits]
  cases taken : takeDigits state.input with
  | mk chars rest => cases chars <;> simp

theorem fraction_run (state : State) :
    ParserIR.run fractionTree state = (fraction state.input).map
      (fun (chars, rest) => (chars, { state with input := rest })) := by
  cases input : state.input with
  | nil => simp [fractionTree, ParserIR.run, input, fraction]
  | cons c rest =>
      by_cases dot : c = '.'
      · subst c
        simp [fractionTree, ParserIR.run, input, accepts, dotPredicate, FirstOrder.eval,
          FirstOrder.lookup, fraction, nonemptyDigitsTree, digitsTree, scan_digits, nonemptyDigits]
        cases taken : takeDigits rest with
        | mk chars remaining => cases chars <;> simp_all
      · simp [fractionTree, ParserIR.run, input, accepts, dotPredicate, FirstOrder.eval,
          FirstOrder.lookup, fraction, dot]

theorem exponent_run (state : State) :
    ParserIR.run exponentTree state = (exponent state.input).map
      (fun (value, rest) => (exponentChars value, { state with input := rest })) := by
  cases input : state.input with
  | nil => simp [exponentTree, ParserIR.run, input, exponent]
  | cons c rest =>
      by_cases marker : c = 'e' ∨ c = 'E'
      · simp only [exponentTree, ParserIR.run]
        simp only [input, accepts, exponentPredicate, FirstOrder.eval, FirstOrder.lookup]
        have yes : (c == 'e' || c == 'E') = true := by simpa using marker
        simp only [yes, ↓reduceIte, bind, Option.bind]
        rw [sign_run]
        dsimp only
        rw [nonempty_digits_run]
        simp [exponent, marker, exponentChars, Option.map_map]
        cases found : nonemptyDigits (sign rest).2 <;> simp
      · have no : (c == 'e' || c == 'E') = false := by simpa using marker
        simp [exponentTree, ParserIR.run, input, accepts, exponentPredicate, FirstOrder.eval,
          FirstOrder.lookup, no, exponent, marker]

theorem optional_fraction_run (state : State) :
    ParserIR.run (.optional fractionTree) state =
      some ((CssNumberSyntax.optional fraction state.input).1, { state with input := (CssNumberSyntax.optional fraction state.input).2 }) := by
  simp only [ParserIR.run, fraction_run]
  cases found : fraction state.input <;> simp [CssNumberSyntax.optional, found]

theorem optional_exponent_run (state : State) :
    ParserIR.run (.optional exponentTree) state =
      some ((CssNumberSyntax.optional exponent state.input).1.map exponentChars, { state with input := (CssNumberSyntax.optional exponent state.input).2 }) := by
  simp only [ParserIR.run, exponent_run]
  cases found : exponent state.input <;> simp [CssNumberSyntax.optional, found]

theorem pair_run (left : Parser a) (right : Parser b) (state : State) :
    ParserIR.run (.pair left right) state = (do
      let (x, next) ← ParserIR.run left state
      let (y, final) ← ParserIR.run right next
      pure ((x, y), final)) := rfl

theorem number_run (state : State) :
    ParserIR.run numberTree state = some (rawParts (consume state.input).decimal,
      { state with input := (consume state.input).rest }) := by
  simp [numberTree, pair_run, sign_run, digits_run, optional_fraction_run, optional_exponent_run,
    consume, rawParts]

def referenceExact (decimal : Decimal) : Exact :=
  ⟨(CssNumberValue.ofDecimal decimal).significand, (CssNumberValue.ofDecimal decimal).scale,
    decide (CssNumberValue.typeFlag decimal = .number), signChars decimal.sign⟩

theorem magnitude_meaning (digits : List Char) : magnitude digits = CssNumberValue.digitsValue digits := rfl

theorem signed_meaning (sign : Option Sign) (value : Nat) :
    signedMagnitude (signChars sign) value = CssNumberValue.signed sign value := by
  cases sign with
  | none => rfl
  | some s => cases s <;> rfl

theorem projection_meaning (decimal : Decimal) : project (rawParts decimal) = referenceExact decimal := by
  cases decimal with
  | mk sign integer fraction exponent =>
      cases fraction <;> cases exponent <;>
        simp [project, rawParts, referenceExact, magnitude_meaning, signed_meaning,
          exponentChars, CssNumberValue.ofDecimal, CssNumberValue.fractionDigits,
          CssNumberValue.exponentValue, CssNumberValue.typeFlag]

theorem execute_reference (state : State) : execute state =
    some (referenceExact (consume state.input).decimal, { state with input := (consume state.input).rest }) := by
  simp [execute, number_run, projection_meaning]

def NumericResult (source : List Char) (value : Exact) (rest : List Char) : Prop :=
  ∃ decimal, Consumed source ⟨decimal, rest⟩ ∧ value = referenceExact decimal

theorem execute_iff (source : List Char) (oldError : Bool) (value : Exact) (rest : List Char) :
    execute ⟨source, oldError⟩ = some (value, ⟨rest, oldError⟩) ↔ NumericResult source value rest := by
  rw [execute_reference]
  constructor
  · intro same
    have equal := Option.some.inj same
    have result := congrArg Prod.fst equal
    have remaining : (consume source).rest = rest := congrArg (fun x => x.2.input) equal
    exact ⟨(consume source).decimal, by rw [← remaining]; exact consume_sound source, result.symm⟩
  · rintro ⟨decimal, parsed, rfl⟩
    simp [parsed.result]

theorem ready_call (source : List Char) (ready : StartsNumber source) :
    Parsed source (consume source) := ⟨ready, consume_sound source⟩

theorem ready_result (source : List Char) (ready : StartsNumber source)
    (oldError : Bool) (value : Exact) (rest : List Char)
    (result : execute ⟨source, oldError⟩ = some (value, ⟨rest, oldError⟩)) :
    StartsNumber source ∧ NumericResult source value rest :=
  ⟨ready, (execute_iff source oldError value rest).mp result⟩

theorem projection_rational_meaning (decimal : Decimal) :
    (CssNumberValue.Value.mk (project (rawParts decimal)).significand
      (project (rawParts decimal)).scale).toRat = CssNumberValue.meaning decimal := by
  rw [projection_meaning]
  exact CssNumberValue.ofDecimal_meaning decimal

end CssDerivation.NumberTransfer
