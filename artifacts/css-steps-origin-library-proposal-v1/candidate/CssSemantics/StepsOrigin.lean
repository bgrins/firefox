import CssSemantics.CssNumericFinalization

namespace CssSemantics.StepsOrigin

open CssSemantics

inductive Position where
  | ordinary
  | jumpNone
  deriving DecidableEq, Repr

def minimum : Position → Int
  | .ordinary => 1
  | .jumpNone => 2

inductive Specified where
  | literal (value : Int)
  | calculation (resolved : Option Int)
  deriving DecidableEq, Repr

def integerNormalize (upper : Int) (value : CssExtendedScalar.Value) : Int :=
  CssIntegerRounding.round (CssNumericCensorship.complete ⟨1, upper⟩ value)

def calculation (upper : Int) (value : CssExtendedScalar.Value) : Specified :=
  .calculation (some (integerNormalize upper value))

def old (position : Position) : Specified → Option Int
  | .literal n | .calculation (some n) =>
      if minimum position ≤ n then some n else none
  | .calculation none => none

def repaired (position : Position) : Specified → Option Int
  | .literal n => if minimum position ≤ n then some n else none
  | .calculation (some n) => some (max (minimum position) n)
  | .calculation none => none

theorem literal_unchanged (position n) :
    repaired position (.literal n) = old position (.literal n) := rfl

theorem unresolved_unchanged (position) :
    repaired position (.calculation none) = old position (.calculation none) := rfl

theorem retained_success {position source result}
    (success : old position source = some result) :
    repaired position source = some result := by
  cases source with
  | literal n => exact success
  | calculation resolved =>
    cases resolved with
    | none => contradiction
    | some n =>
      simp only [old] at success
      split at success
      · simp only [Option.some.injEq] at success
        subst result
        simp only [repaired, Option.some.injEq]
        omega
      · contradiction

theorem resolved_result_bounded {position : Position} {n upper : Int}
    (minimumFits : minimum position ≤ upper) (normalizationBound : n ≤ upper) :
    minimum position ≤ max (minimum position) n ∧
      max (minimum position) n ≤ upper := by
  omega

theorem normalized_bounded {upper : Int} (valid : 1 ≤ upper) (value) :
    1 ≤ integerNormalize upper value ∧ integerNormalize upper value ≤ upper := by
  have bounds := CssNumericFinalization.finish_bounded
    (context := .integer 1 upper)
    (show CssNumericFinalization.Context.Valid (.integer 1 upper) from
      Rat.intCast_le_intCast.mpr valid) value
  exact ⟨Rat.intCast_le_intCast.mp bounds.1, Rat.intCast_le_intCast.mp bounds.2⟩

theorem calculation_nan_equals_zero (upper) :
    calculation upper .nan = calculation upper (.finite ⟨0, false⟩) := rfl

theorem exact_old_loss {n : Int} (normalizedPositive : 1 ≤ n) :
    old .jumpNone (.calculation (some n)) = none ↔ n = 1 := by
  by_cases enough : 2 ≤ n
  · simp [old, minimum, enough]
    omega
  · simp [old, minimum, enough]
    omega

theorem ordinary_calculation_unchanged {n : Int} (normalizedPositive : 1 ≤ n) :
    repaired .ordinary (.calculation (some n)) = old .ordinary (.calculation (some n)) := by
  simp only [repaired, old, minimum, normalizedPositive, ite_true, Option.some.injEq]
  omega

theorem repaired_jump_none_at_one :
    old .jumpNone (.calculation (some 1)) = none ∧
    repaired .jumpNone (.calculation (some 1)) = some 2 ∧
    repaired .jumpNone (.literal 1) = none := by decide +kernel

theorem repaired_nan : repaired .jumpNone (calculation 4 .nan) = some 2 := by
  decide +kernel

end CssSemantics.StepsOrigin
