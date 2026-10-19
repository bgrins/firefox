import NumericUnits
namespace NumericPayload
open NumericDigits

inductive Expr where
  | zero | one | negativeOne | ten | tenth | hundred
  | digit : Nat → Expr
  | add : Expr → Expr → Expr
  | mul : Expr → Expr → Expr
  | div : Expr → Expr → Expr
  | pow : Expr → Expr → Expr
  | f32 : Expr → Expr
  deriving DecidableEq,Repr

def accumulate (acc : Expr) (digits : List Byte) : Expr :=
  match digits with
  | [] => acc
  | d::ds => accumulate (.add (.mul acc .ten) (.digit (d.val-48))) ds

def fractions (value factor : Expr) (digits : List Byte) : Expr × Expr :=
  match digits with
  | [] => (value,factor)
  | d::ds => fractions (.add value (.mul (.digit (d.val-48)) factor)) (.mul factor .tenth) ds

def sign (negative : Bool) : Expr := if negative then .negativeOne else .one

def nativeValue (n : NumericLexical.Result) : Expr :=
  let base := Expr.mul (sign n.negative)
    (.add (accumulate .zero n.integralDigits) (fractions .zero .tenth n.fractionalDigits).1)
  if n.exponentDigits.isEmpty then base
  else .mul base (.pow .ten (.mul (sign n.exponentNegative) (accumulate .zero n.exponentDigits)))

def payload (r : NumericToken.Result) : Expr :=
  if r.kind = .percentage then .f32 (.div (nativeValue r.numeric) .hundred)
  else .f32 (nativeValue r.numeric)

inductive IntSelection where
  | max | min | cast
  deriving DecidableEq,Repr

def integerSelection (isInteger geMax leMin : Bool) : Option IntSelection :=
  if isInteger then some (if geMax then .max else if leMin then .min else .cast) else none

theorem accumulate_append (a : Expr) (xs ys : List Byte) :
    accumulate a (xs++ys) = accumulate (accumulate a xs) ys := by
  induction xs generalizing a with
  | nil => rfl
  | cons x xs ih => exact ih _

theorem fraction_append (a f : Expr) (xs ys : List Byte) :
    fractions a f (xs++ys) = fractions (fractions a f xs).1 (fractions a f xs).2 ys := by
  induction xs generalizing a f with
  | nil => rfl
  | cons x xs ih => exact ih _ _

theorem numeric_reference_trace (xs : List Byte) :
    nativeValue (NumericLexical.native xs) = nativeValue (NumericLexical.reference xs) := by
  rw [NumericLexical.native_reference]

theorem syntactic_integer_only (geMax leMin : Bool) :
    integerSelection false geMax leMin = none := rfl

theorem upper_saturation (leMin : Bool) : integerSelection true true leMin = some .max := rfl

theorem lower_saturation : integerSelection true false true = some .min := rfl

theorem cast_domain : integerSelection true false false = some .cast := rfl

theorem percentage_divide_before_cast (r : NumericToken.Result) (h : r.kind = .percentage) :
    payload r = .f32 (.div (nativeValue r.numeric) .hundred) := by simp [payload,h]

theorem other_cast (r : NumericToken.Result) (h : r.kind ≠ .percentage) :
    payload r = .f32 (nativeValue r.numeric) := by simp [payload,h]

#print axioms accumulate_append
#print axioms fraction_append
#print axioms numeric_reference_trace
#print axioms syntactic_integer_only
#print axioms upper_saturation
#print axioms lower_saturation
#print axioms cast_domain
#print axioms percentage_divide_before_cast
#print axioms other_cast
end NumericPayload
