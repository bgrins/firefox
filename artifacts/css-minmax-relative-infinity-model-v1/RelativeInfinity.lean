import Std

namespace RelativeInfinity

inductive Value where
  | nan
  | negInf
  | finite (value : Int)
  | posInf
  deriving DecidableEq, Repr

inductive Basis where
  | zero
  | positive (predecessor : Nat)
  deriving DecidableEq, Repr

inductive Op where
  | min
  | max
  deriving DecidableEq, Repr

def scale (basis : Basis) : Value → Value
  | .nan => .nan
  | .negInf => match basis with | .zero => .nan | .positive _ => .negInf
  | .posInf => match basis with | .zero => .nan | .positive _ => .posInf
  | .finite n => match basis with
    | .zero => .finite 0
    | .positive k => .finite (n * (Int.ofNat k + 1))

def minimum : Value → Value → Value
  | .nan, _ => .nan
  | _, .nan => .nan
  | .negInf, _ => .negInf
  | _, .negInf => .negInf
  | .posInf, b => b
  | a, .posInf => a
  | .finite a, .finite b => .finite (min a b)

def maximum : Value → Value → Value
  | .nan, _ => .nan
  | _, .nan => .nan
  | .posInf, _ => .posInf
  | _, .posInf => .posInf
  | .negInf, b => b
  | a, .negInf => a
  | .finite a, .finite b => .finite (max a b)

def semantic (op : Op) (a b : Value) : Value :=
  match op with | .min => minimum a b | .max => maximum a b

def isNaNCoefficient : Value → Bool
  | .nan => true
  | _ => false

def isInfinite : Value → Bool
  | .negInf | .posInf => true
  | _ => false

inductive Plan where
  | defer
  | constant
  | relative
  deriving DecidableEq, Repr

def coefficientPlan (op : Op) : Value → Plan
  | .nan => .relative
  | .finite _ => .defer
  | .negInf => match op with | .min => .relative | .max => .constant
  | .posInf => match op with | .min => .constant | .max => .relative

def execute (plan : Plan) (op : Op) (constant : Int)
    (coefficient : Value) (basis : Basis) : Value :=
  match plan with
  | .defer => semantic op (.finite constant) (scale basis coefficient)
  | .constant => .finite constant
  | .relative => scale basis coefficient

def guardedPlan (op : Op) (coefficient : Value) (knownPositive : Bool) : Plan :=
  if isInfinite coefficient && !knownPositive then .defer
  else coefficientPlan op coefficient

def knowledgeSound (knownPositive : Bool) (basis : Basis) : Prop :=
  knownPositive = true → ∃ k, basis = .positive k

theorem infinity_not_coefficient_nan (negative : Bool) :
    isNaNCoefficient (if negative then .negInf else .posInf) = false := by
  cases negative <;> rfl

theorem infinity_zero_becomes_nan (negative : Bool) :
    scale .zero (if negative then .negInf else .posInf) = .nan := by
  cases negative <;> rfl

theorem min_positive_infinity_counterexample (constant : Int) :
    execute (coefficientPlan .min .posInf) .min constant .posInf .zero ≠
      semantic .min (.finite constant) (scale .zero .posInf) := by
  simp [execute, coefficientPlan, semantic, scale, minimum]

theorem max_negative_infinity_counterexample (constant : Int) :
    execute (coefficientPlan .max .negInf) .max constant .negInf .zero ≠
      semantic .max (.finite constant) (scale .zero .negInf) := by
  simp [execute, coefficientPlan, semantic, scale, maximum]

theorem positive_basis_shortcut_sound (op : Op) (constant : Int)
    (coefficient : Value) (k : Nat) :
    execute (coefficientPlan op coefficient) op constant coefficient (.positive k) =
      semantic op (.finite constant) (scale (.positive k) coefficient) := by
  cases op <;> cases coefficient <;>
    simp [execute, coefficientPlan, semantic, scale, minimum, maximum]

theorem unknown_infinite_basis_defers (op : Op) (negative : Bool) :
    guardedPlan op (if negative then .negInf else .posInf) false = .defer := by
  cases negative <;> rfl

theorem guarded_plan_sound (op : Op) (constant : Int) (coefficient : Value)
    (basis : Basis) (knownPositive : Bool)
    (sound : knowledgeSound knownPositive basis) :
    execute (guardedPlan op coefficient knownPositive) op constant coefficient basis =
      semantic op (.finite constant) (scale basis coefficient) := by
  cases knownPositive with
  | false =>
    cases op <;> cases coefficient <;> cases basis <;>
      simp [guardedPlan, isInfinite, coefficientPlan, execute, semantic, scale,
        minimum, maximum]
  | true =>
    obtain ⟨k, rfl⟩ := sound rfl
    simpa [guardedPlan] using positive_basis_shortcut_sound op constant coefficient k

theorem unknown_basis_preserves_mutation (op : Op) (constant : Int)
    (coefficient : Value) (before after : Basis) :
    (execute (guardedPlan op coefficient false) op constant coefficient before,
     execute (guardedPlan op coefficient false) op constant coefficient after) =
    (semantic op (.finite constant) (scale before coefficient),
     semantic op (.finite constant) (scale after coefficient)) := by
  have sound : ∀ b, knowledgeSound false b := by
    intro b impossible
    cases impossible
  rw [guarded_plan_sound op constant coefficient before false (sound before),
      guarded_plan_sound op constant coefficient after false (sound after)]

theorem selected_infinity_keeps_nan (constant : Int) :
    execute (coefficientPlan .min .negInf) .min constant .negInf .zero = .nan ∧
    execute (coefficientPlan .max .posInf) .max constant .posInf .zero = .nan := by
  constructor <;> rfl

theorem unknown_finite_pair_stays_deferred (op : Op) (coefficient : Int) :
    guardedPlan op (.finite coefficient) false = .defer := by
  rfl

def clamp (lower center upper : Value) : Value :=
  maximum lower (minimum center upper)

theorem clamp_zero_basis_is_nan :
    clamp (.finite (-1)) (scale .zero .posInf) (.finite 10) = .nan := by
  rfl

theorem clamp_positive_basis_is_upper (k : Nat) :
    clamp (.finite (-1)) (scale (.positive k) .posInf) (.finite 10) = .finite 10 := by
  rfl

end RelativeInfinity
