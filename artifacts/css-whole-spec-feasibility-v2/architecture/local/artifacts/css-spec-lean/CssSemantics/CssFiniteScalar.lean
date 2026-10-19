import CssSemantics.CssNumberValue

namespace CssSemantics.CssFiniteScalar

structure Scalar where
  value : Rat
  negativeZero : Bool
  deriving DecidableEq, Repr

def Scalar.Valid (scalar : Scalar) : Prop := scalar.negativeZero = true → scalar.value = 0

def make (value : Rat) (negativeZero : Bool) : Scalar :=
  ⟨value, decide (value = 0) && negativeZero⟩

def source (value : Rat) : Scalar := ⟨value, false⟩

def ofNumber (value : CssNumberValue.Value) : Scalar := source value.toRat

def Scalar.isNegativeZero (scalar : Scalar) : Bool := decide (scalar.value = 0) && scalar.negativeZero

def Scalar.isNegative (scalar : Scalar) : Bool := decide (scalar.value < 0) || scalar.isNegativeZero

-- Sign-bit reversal is separate from CSS Negate-node evaluation.
def reverseSign (scalar : Scalar) : Scalar := make (-scalar.value) (!scalar.negativeZero)

def add (left right : Scalar) : Scalar :=
  make (left.value + right.value) (left.isNegativeZero && right.isNegativeZero)

def Scalar.isPositiveZero (scalar : Scalar) : Bool := decide (scalar.value = 0) && !scalar.negativeZero

def subtract (left right : Scalar) : Scalar :=
  make (left.value - right.value) (left.isNegativeZero && right.isPositiveZero)

def multiply (left right : Scalar) : Scalar :=
  make (left.value * right.value) (left.isNegative != right.isNegative)

def divide (left right : Scalar) : Option Scalar :=
  if right.value = 0 then none
  else some (make (left.value / right.value) (left.isNegative != right.isNegative))

inductive SignReversed (input : Scalar) : Scalar → Prop where
  | nonzero : input.value ≠ 0 → SignReversed input ⟨-input.value, false⟩
  | zero : input.value = 0 → SignReversed input ⟨0, !input.negativeZero⟩

inductive Sum (left right : Scalar) : Scalar → Prop where
  | nonzero : left.value + right.value ≠ 0 → Sum left right ⟨left.value + right.value, false⟩
  | negative : left.isNegativeZero = true → right.isNegativeZero = true → Sum left right ⟨0, true⟩
  | positive : left.value + right.value = 0 → ¬ (left.isNegativeZero = true ∧ right.isNegativeZero = true) →
      Sum left right ⟨0, false⟩

inductive Difference (left right : Scalar) : Scalar → Prop where
  | nonzero : left.value - right.value ≠ 0 → Difference left right ⟨left.value - right.value, false⟩
  | negative : left.isNegativeZero = true → right.isPositiveZero = true → Difference left right ⟨0, true⟩
  | positive : left.value - right.value = 0 → ¬ (left.isNegativeZero = true ∧ right.isPositiveZero = true) →
      Difference left right ⟨0, false⟩

inductive Product (left right : Scalar) : Scalar → Prop where
  | nonzero : left.value * right.value ≠ 0 → Product left right ⟨left.value * right.value, false⟩
  | zero : left.value * right.value = 0 →
      Product left right ⟨0, left.isNegative != right.isNegative⟩

inductive Quotient (left right : Scalar) : Scalar → Prop where
  | nonzero : right.value ≠ 0 → left.value / right.value ≠ 0 →
      Quotient left right ⟨left.value / right.value, false⟩
  | zero : right.value ≠ 0 → left.value / right.value = 0 →
      Quotient left right ⟨0, left.isNegative != right.isNegative⟩

theorem make_valid (value negativeZero) : (make value negativeZero).Valid := by
  simp only [Scalar.Valid, make, Bool.and_eq_true, decide_eq_true_eq]
  exact fun proof => proof.1

theorem source_valid (value) : (source value).Valid := by simp [source, Scalar.Valid]

theorem source_zero_positive : source 0 = ⟨0, false⟩ := rfl

theorem ofNumber_value (value) : (ofNumber value).value = value.toRat := rfl

theorem negativeZero_iff (scalar : Scalar) : scalar.isNegativeZero = true ↔ scalar.value = 0 ∧ scalar.negativeZero = true := by
  simp [Scalar.isNegativeZero]

theorem SignReversed.result {input result} (parsed : SignReversed input result) : reverseSign input = result := by
  cases parsed with
  | nonzero nonzero =>
    have negativeNonzero : -input.value ≠ 0 := by
      intro equal
      have reversed := congrArg (fun value : Rat => -value) equal
      exact nonzero (by simpa [Rat.neg_neg, Rat.neg_zero] using reversed)
    simp [reverseSign, make, negativeNonzero]
  | zero zero => simp [reverseSign, make, zero]

theorem reverseSign_sound (input : Scalar) : SignReversed input (reverseSign input) := by
  by_cases zero : input.value = 0
  · simpa [reverseSign, make, zero] using SignReversed.zero (input := input) zero
  · have negativeNonzero : -input.value ≠ 0 := by
      intro equal
      have reversed := congrArg (fun value : Rat => -value) equal
      exact zero (by simpa [Rat.neg_neg, Rat.neg_zero] using reversed)
    simpa [reverseSign, make, negativeNonzero] using SignReversed.nonzero (input := input) zero

theorem reverseSign_iff (input result) : reverseSign input = result ↔ SignReversed input result :=
  ⟨fun equal => equal ▸ reverseSign_sound input, SignReversed.result⟩

theorem Sum.result {left right result} (parsed : Sum left right result) : add left right = result := by
  cases parsed with
  | nonzero nonzero => simp [add, make, nonzero]
  | negative leftZero rightZero =>
    have leftValue := ((negativeZero_iff left).mp leftZero).1
    have rightValue := ((negativeZero_iff right).mp rightZero).1
    simp [add, make, leftValue, rightValue, leftZero, rightZero, Rat.zero_add]
  | positive zero notBoth =>
    have no : (left.isNegativeZero && right.isNegativeZero) = false := by
      cases first : left.isNegativeZero <;> cases second : right.isNegativeZero <;> simp_all
    simp [add, make, zero, no]

theorem add_sound (left right : Scalar) : Sum left right (add left right) := by
  by_cases zero : left.value + right.value = 0
  · by_cases both : left.isNegativeZero = true ∧ right.isNegativeZero = true
    · simpa [add, make, zero, both.1, both.2] using Sum.negative both.1 both.2
    · have no : (left.isNegativeZero && right.isNegativeZero) = false := by
        cases first : left.isNegativeZero <;> cases second : right.isNegativeZero <;> simp_all
      simpa [add, make, zero, no] using Sum.positive (left := left) (right := right) zero both
  · simpa [add, make, zero] using Sum.nonzero (left := left) (right := right) zero

theorem add_iff (left right result) : add left right = result ↔ Sum left right result :=
  ⟨fun equal => equal ▸ add_sound left right, Sum.result⟩

theorem positiveZero_iff (scalar : Scalar) : scalar.isPositiveZero = true ↔ scalar.value = 0 ∧ scalar.negativeZero = false := by
  simp [Scalar.isPositiveZero]

theorem Difference.result {left right result} (parsed : Difference left right result) : subtract left right = result := by
  cases parsed with
  | nonzero nonzero => simp [subtract, make, nonzero]
  | negative leftZero rightZero =>
    have leftValue := ((negativeZero_iff left).mp leftZero).1
    have rightValue := ((positiveZero_iff right).mp rightZero).1
    simp [subtract, make, leftValue, rightValue, leftZero, rightZero, Rat.sub_self]
  | positive zero notBoth =>
    have no : (left.isNegativeZero && right.isPositiveZero) = false := by
      cases first : left.isNegativeZero <;> cases second : right.isPositiveZero <;> simp_all
    simp [subtract, make, zero, no]

theorem subtract_sound (left right : Scalar) : Difference left right (subtract left right) := by
  by_cases zero : left.value - right.value = 0
  · by_cases both : left.isNegativeZero = true ∧ right.isPositiveZero = true
    · simpa [subtract, make, zero, both.1, both.2] using Difference.negative both.1 both.2
    · have no : (left.isNegativeZero && right.isPositiveZero) = false := by
        cases first : left.isNegativeZero <;> cases second : right.isPositiveZero <;> simp_all
      simpa [subtract, make, zero, no] using Difference.positive (left := left) (right := right) zero both
  · simpa [subtract, make, zero] using Difference.nonzero (left := left) (right := right) zero

theorem subtract_iff (left right result) : subtract left right = result ↔ Difference left right result :=
  ⟨fun equal => equal ▸ subtract_sound left right, Difference.result⟩

theorem Product.result {left right result} (parsed : Product left right result) : multiply left right = result := by
  cases parsed with
  | nonzero nonzero => simp [multiply, make, nonzero]
  | zero zero => simp [multiply, make, zero]

theorem multiply_sound (left right : Scalar) : Product left right (multiply left right) := by
  by_cases zero : left.value * right.value = 0
  · simpa [multiply, make, zero] using Product.zero (left := left) (right := right) zero
  · simpa [multiply, make, zero] using Product.nonzero (left := left) (right := right) zero

theorem multiply_iff (left right result) : multiply left right = result ↔ Product left right result :=
  ⟨fun equal => equal ▸ multiply_sound left right, Product.result⟩

theorem Quotient.result {left right result} (parsed : Quotient left right result) : divide left right = some result := by
  cases parsed with
  | nonzero divisor nonzero => simp [divide, make, divisor, nonzero]
  | zero divisor zero => simp [divide, make, divisor, zero]

theorem divide_iff (left right result) : divide left right = some result ↔ Quotient left right result := by
  constructor
  · intro equal
    unfold divide at equal
    split at equal
    · contradiction
    · have divisor : right.value ≠ 0 := by assumption
      cases equal
      by_cases zero : left.value / right.value = 0
      · simpa [make, zero] using Quotient.zero (left := left) (right := right) divisor zero
      · simpa [make, zero] using Quotient.nonzero (left := left) (right := right) divisor zero
  · exact Quotient.result

theorem divide_none_iff (left right) : divide left right = none ↔ right.value = 0 := by
  simp [divide]

theorem reverseSign_valid (input) : (reverseSign input).Valid := make_valid _ _
theorem add_valid (left right) : (add left right).Valid := make_valid _ _
theorem subtract_valid (left right) : (subtract left right).Valid := make_valid _ _
theorem multiply_valid (left right) : (multiply left right).Valid := make_valid _ _

theorem quotient_valid {left right result} (parsed : Quotient left right result) : result.Valid := by
  have equal := parsed.result
  unfold divide at equal
  split at equal
  · contradiction
  · cases equal; exact make_valid _ _

theorem reverseSign_value (input) : (reverseSign input).value = -input.value := rfl
theorem add_value (left right) : (add left right).value = left.value + right.value := rfl
theorem subtract_value (left right) : (subtract left right).value = left.value - right.value := rfl
theorem multiply_value (left right) : (multiply left right).value = left.value * right.value := rfl

theorem quotient_value {left right result} (parsed : Quotient left right result) : result.value = left.value / right.value := by
  cases parsed with
  | nonzero => rfl
  | zero _ zero => exact zero.symm

theorem source_number_zero (scale : Int) : ofNumber ⟨0, scale⟩ = source 0 := by
  simp [ofNumber, CssNumberValue.Value.toRat, Rat.zero_mul]

theorem reverseSign_involutive (input : Scalar) (valid : input.Valid) : reverseSign (reverseSign input) = input := by
  cases input with
  | mk value negativeZero =>
    by_cases zero : value = 0
    · simp [reverseSign, make, zero, Rat.neg_zero]
    · have flag : negativeZero = false := by
        cases negativeZero with
        | false => rfl
        | true => exact False.elim (zero (valid rfl))
      have negativeNonzero : -value ≠ 0 := by
        intro equal
        have reversed := congrArg (fun value : Rat => -value) equal
        exact zero (by simpa [Rat.neg_neg, Rat.neg_zero] using reversed)
      simp [reverseSign, make, flag, zero, negativeNonzero, Rat.neg_neg]

theorem source_zero_reversal_differs : reverseSign (source 0) ≠ subtract (source 0) (source 0) := by
  decide +kernel

end CssSemantics.CssFiniteScalar
