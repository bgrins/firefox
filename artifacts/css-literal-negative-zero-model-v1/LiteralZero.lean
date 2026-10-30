import SpecialValueObserver

namespace LiteralZero

inductive Policy where
  | mathematicalLiteral | preserveLiteralSign
  deriving DecidableEq, Repr

inductive Spelling where
  | unsigned | positive | negative
  deriving DecidableEq, Repr

inductive Quantity where
  | number | pixelLength
  deriving DecidableEq, Repr

inductive Value where
  | nan | negInf | negOne | negZero | posZero | posOne | posInf
  deriving DecidableEq, Repr

open Value

def sign : Value → Value
  | nan => nan
  | negInf | negOne => negOne
  | posInf | posOne => posOne
  | negZero => negZero
  | posZero => posZero

def reciprocal : Value → Value
  | nan => nan
  | negInf => negZero
  | posInf => posZero
  | negZero => negInf
  | posZero => posInf
  | negOne => negOne
  | posOne => posOne

def negativeOneTimes : Value → Value
  | nan => nan
  | negInf => posInf
  | posInf => negInf
  | negOne => posOne
  | posOne => negOne
  | negZero => posZero
  | posZero => negZero

def literal (p : Policy) (s : Spelling) : Value :=
  match p, s with
  | .preserveLiteralSign, .negative => negZero
  | _, _ => posZero

def biasedQuarters : Value → Nat
  | nan => 0
  | negOne => 1
  | posOne => 3
  | negZero | posZero => 2
  | negInf => 0
  | posInf => 4

def observe (v : Value) : Nat := biasedQuarters (sign (reciprocal (sign v)))

inductive Expression where
  | zeroLiteral (spelling : Spelling)
  | generatedNegativeZero
  deriving DecidableEq, Repr

def evaluate (p : Policy) (_q : Quantity) : Expression → Value
  | .zeroLiteral s => literal p s
  | .generatedNegativeZero => negativeOneTimes (literal p .unsigned)

def normalizeAllZeros : Value → Value
  | negZero => posZero
  | v => v

def sixCases : List (Quantity × Expression) :=
  [(.number, .zeroLiteral .unsigned), (.number, .zeroLiteral .negative),
   (.number, .generatedNegativeZero), (.pixelLength, .zeroLiteral .unsigned),
   (.pixelLength, .zeroLiteral .negative), (.pixelLength, .generatedNegativeZero)]

def results (p : Policy) : List Nat :=
  sixCases.map fun (q, e) => observe (evaluate p q e)

theorem mathematical_literals_positive (s : Spelling) :
    literal .mathematicalLiteral s = posZero := by cases s <;> rfl

theorem preserving_negative_literal : literal .preserveLiteralSign .negative = negZero := rfl

theorem policies_agree_except_negative (s : Spelling) :
    literal .mathematicalLiteral s = literal .preserveLiteralSign s ↔ s ≠ .negative := by
  cases s <;> decide

theorem generated_negative_stays_negative (p : Policy) (q : Quantity) :
    evaluate p q .generatedNegativeZero = negZero := by cases p <;> rfl

theorem quantity_erasure_explicit (p : Policy) (e : Expression) :
    evaluate p .number e = evaluate p .pixelLength e := rfl

theorem sign_preserves_zeros : sign negZero = negZero ∧ sign posZero = posZero := by decide

theorem positive_zero_observer : observe posZero = 3 := rfl

theorem negative_zero_observer : observe negZero = 1 := rfl

theorem nan_observer : observe nan = 0 := rfl

theorem generated_observer (p : Policy) (q : Quantity) :
    observe (evaluate p q .generatedNegativeZero) = 1 := by cases p <;> rfl

theorem mathematical_six_cases : results .mathematicalLiteral = [3, 3, 1, 3, 3, 1] := rfl

theorem preserving_six_cases : results .preserveLiteralSign = [3, 1, 1, 3, 1, 1] := rfl

theorem policy_disagreement_is_literal_only (q : Quantity) (e : Expression) :
    observe (evaluate .mathematicalLiteral q e) ≠
      observe (evaluate .preserveLiteralSign q e) ↔ e = .zeroLiteral .negative := by
  cases e with
  | zeroLiteral s => cases q <;> cases s <;> decide
  | generatedNegativeZero => cases q <;> decide

theorem global_normalization_changes_generated (p : Policy) (q : Quantity) :
    observe (normalizeAllZeros (evaluate p q .generatedNegativeZero)) ≠
      observe (evaluate p q .generatedNegativeZero) := by cases p <;> cases q <;> decide

theorem zero_and_nan_outputs_distinct :
    observe posZero ≠ observe negZero ∧ observe posZero ≠ observe nan ∧
      observe negZero ≠ observe nan := by decide

def embed : SpecialValueObserver.Value → Value
  | .nan => nan
  | .negInf => negInf
  | .negZero => negZero
  | .posZero => posZero
  | .posInf => posInf

theorem existing_reciprocal_agrees (v : SpecialValueObserver.Value) :
    reciprocal (embed v) = embed (SpecialValueObserver.reciprocal v) := by
  cases v <;> rfl

end LiteralZero
