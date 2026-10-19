import Std
set_option autoImplicit false

namespace AbsposMargins

inductive Axis where
  | inline | block
  deriving DecidableEq

inductive Margin where
  | auto
  | fixed (value : Int)
  deriving DecidableEq

def Margin.isAuto : Margin → Bool
  | .auto => true
  | .fixed _ => false

def Margin.initial : Margin → Int
  | .auto => 0
  | .fixed value => value

structure Pair where
  start : Int
  finish : Int
  deriving DecidableEq

structure Inset where
  autoProvenance : Bool
  unresolvedSentinel : Bool
  numeric : Int
  deriving DecidableEq

def Inset.needsZero (a b : Inset) : Bool :=
  a.autoProvenance || b.autoProvenance || a.unresolvedSentinel || b.unresolvedSentinel

def half (r : Int) : Int := if 0 ≤ r then r / 2 else -((-r) / 2)

def split (axis : Axis) (residual : Int) (start finish : Margin) : Pair :=
  match start, finish with
  | .fixed a, .fixed b => ⟨a, b⟩
  | .auto, .fixed b => ⟨residual, b⟩
  | .fixed a, .auto => ⟨a, residual⟩
  | .auto, .auto =>
    if axis = .inline ∧ residual < 0 then ⟨0, residual⟩
    else ⟨half residual, residual - half residual⟩

def signedResidual (cb startInset endInset fixedSum kid : Int) : Int :=
  max 0 (cb - (startInset + endInset)) - fixedSum - kid

structure Step where
  values : Pair
  geometryEvaluated : Bool
  deriving DecidableEq

def resolve (axis : Axis) (cb kid : Int) (startInset endInset : Inset)
    (start finish : Margin) : Step :=
  if start.isAuto || finish.isAuto then
    if startInset.needsZero endInset then
      ⟨split axis 0 start finish, false⟩
    else
      ⟨split axis (signedResidual cb startInset.numeric endInset.numeric
          (start.initial + finish.initial) kid) start finish, true⟩
  else ⟨⟨start.initial, finish.initial⟩, false⟩

theorem no_auto_no_arithmetic (axis : Axis) (cb kid a b : Int) (si ei : Inset) :
    resolve axis cb kid si ei (.fixed a) (.fixed b) = ⟨⟨a,b⟩, false⟩ := rfl

theorem zero_split (axis : Axis) (start finish : Margin) :
    split axis 0 start finish = ⟨start.initial, finish.initial⟩ := by
  cases start <;> cases finish <;> simp [split, half, Margin.initial]

theorem auto_inset_zero (axis : Axis) (cb kid numeric : Int) (endInset : Inset)
    (start finish : Margin) (sentinel : Bool) :
    resolve axis cb kid ⟨true,sentinel,numeric⟩ endInset start finish =
      ⟨⟨start.initial,finish.initial⟩,false⟩ := by
  simp only [resolve, Inset.needsZero, Bool.true_or]
  split <;> simp_all [zero_split]

theorem end_auto_inset_zero (axis : Axis) (cb kid numeric : Int) (startInset : Inset)
    (start finish : Margin) (sentinel : Bool) :
    resolve axis cb kid startInset ⟨true,sentinel,numeric⟩ start finish =
      ⟨⟨start.initial,finish.initial⟩,false⟩ := by
  simp only [resolve, Inset.needsZero, Bool.or_true, Bool.true_or]
  split <;> simp_all [zero_split]

theorem sentinel_zero (axis : Axis) (cb kid numeric : Int) (endInset : Inset)
    (start finish : Margin) (provenance : Bool) :
    resolve axis cb kid ⟨provenance,true,numeric⟩ endInset start finish =
      ⟨⟨start.initial,finish.initial⟩,false⟩ := by
  simp only [resolve, Inset.needsZero, Bool.or_true, Bool.true_or]
  split <;> simp_all [zero_split]

theorem one_auto_start (axis : Axis) (r fixed : Int) :
    split axis r .auto (.fixed fixed) = ⟨r,fixed⟩ := rfl

theorem one_auto_end (axis : Axis) (r fixed : Int) :
    split axis r (.fixed fixed) .auto = ⟨fixed,r⟩ := rfl

theorem both_auto_conserve (axis : Axis) (r : Int) :
    (split axis r .auto .auto).start + (split axis r .auto .auto).finish = r := by
  simp only [split]
  split <;> dsimp <;> omega

theorem fixed_margins_preserved (axis : Axis) (r fixed : Int) (other : Margin) :
    (split axis r (.fixed fixed) other).start = fixed ∧
    (split axis r other (.fixed fixed)).finish = fixed := by
  cases other <;> simp [split]

theorem inline_negative_safe (r : Int) (negative : r < 0) :
    split .inline r .auto .auto = ⟨0,r⟩ := by simp [split, negative]

theorem block_split (r : Int) :
    split .block r .auto .auto = ⟨half r,r-half r⟩ := by simp [split]

theorem half_remainder (r : Int) :
    -1 ≤ (r - half r) - half r ∧ (r - half r) - half r ≤ 1 := by
  unfold half
  split <;> omega

def Fits32 (n : Int) : Prop := -2147483648 ≤ n ∧ n ≤ 2147483647

theorem split_representable (r : Int) (bounded : Fits32 r) :
    Fits32 (half r) ∧ Fits32 (r - half r) := by
  unfold half Fits32 at *
  split <;> omega

theorem fixed_residual_conservation (cb si ei fixed kid : Int) :
    signedResidual cb si ei fixed kid + fixed + kid = max 0 (cb - (si + ei)) := by
  unfold signedResidual
  omega

theorem automatic_total (axis : Axis) (r : Int) (start finish : Margin)
    (active : (start.isAuto || finish.isAuto) = true) :
    (split axis r start finish).start + (split axis r start finish).finish =
      r + start.initial + finish.initial := by
  cases start with
  | auto =>
    cases finish with
    | auto => simpa [Margin.initial] using both_auto_conserve axis r
    | fixed n => simp [split, Margin.initial]
  | fixed n =>
    cases finish with
    | auto => simp [split, Margin.initial]; omega
    | fixed m => simp [Margin.isAuto] at active

theorem definite_distribution_conservation (axis : Axis) (cb kid si ei : Int)
    (start finish : Margin) (active : (start.isAuto || finish.isAuto) = true) :
    let result := resolve axis cb kid ⟨false,false,si⟩ ⟨false,false,ei⟩ start finish
    result.values.start + result.values.finish + kid = max 0 (cb - (si + ei)) := by
  simp only [resolve, active, Bool.false_or, Inset.needsZero, ite_true, Bool.false_eq_true, ite_false]
  rw [automatic_total axis _ start finish active]
  unfold signedResidual
  omega

theorem both_auto_floor_preserved (cb si ei kid : Int) :
    signedResidual cb si ei 0 kid = max 0 (cb - (si + ei) - 0) - kid := by
  simp [signedResidual]

theorem positive_imcb_excess_fixed :
    signedResidual 100 0 0 150 20 = -70 ∧
    max 0 ((100 : Int) - 0 - 150) - 20 = -20 := by decide

theorem negative_imcb_fixed_sign :
    signedResidual 100 60 60 150 20 = -170 ∧
    signedResidual 100 60 60 (-50) 20 = 30 := by decide

theorem negative_odd_truncation :
    half (-21) = -10 ∧ split .block (-21) .auto .auto = ⟨-10,-11⟩ := by decide

theorem numeric_auto_provenance_matters :
    resolve .inline 100 20 ⟨true,false,130⟩ ⟨false,false,0⟩ .auto (.fixed (-50)) =
      ⟨⟨0,-50⟩,false⟩ ∧
    resolve .inline 100 20 ⟨false,false,130⟩ ⟨false,false,0⟩ .auto (.fixed (-50)) =
      ⟨⟨30,-50⟩,true⟩ := by decide

#print axioms no_auto_no_arithmetic
#print axioms zero_split
#print axioms auto_inset_zero
#print axioms end_auto_inset_zero
#print axioms sentinel_zero
#print axioms one_auto_start
#print axioms one_auto_end
#print axioms both_auto_conserve
#print axioms fixed_margins_preserved
#print axioms inline_negative_safe
#print axioms block_split
#print axioms half_remainder
#print axioms split_representable
#print axioms fixed_residual_conservation
#print axioms automatic_total
#print axioms definite_distribution_conservation
#print axioms both_auto_floor_preserved
#print axioms positive_imcb_excess_fixed
#print axioms negative_imcb_fixed_sign
#print axioms negative_odd_truncation
#print axioms numeric_auto_provenance_matters
end AbsposMargins
