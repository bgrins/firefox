import Clamp

namespace ClampScaling
open ClampNaN

def mapNumber (f : Scalar → Scalar) : Number → Number
  | .nan => .nan
  | .value a => .value (f a)

theorem map_minimum (f : Scalar → Scalar) (mono : Monotone f) (a b : Number) :
    mapNumber f (strictMin a b) = strictMin (mapNumber f a) (mapNumber f b) := by
  cases a <;> cases b <;> simp [mapNumber, strictMin, minimum_map f mono]

theorem map_maximum (f : Scalar → Scalar) (mono : Monotone f) (a b : Number) :
    mapNumber f (strictMax a b) = strictMax (mapNumber f a) (mapNumber f b) := by
  cases a <;> cases b <;> simp [mapNumber, strictMax, maximum_map f mono]

theorem map_clamp (f : Scalar → Scalar) (mono : Monotone f) (a b c : Number) :
    mapNumber f (specClamp a b c) = specClamp (mapNumber f a) (mapNumber f b) (mapNumber f c) := by
  simp [specClamp, map_maximum f mono, map_minimum f mono]

theorem positive_resolution (basis : Rat) (positive : 0 < basis) (a : Number) :
    resolveScale basis a = mapNumber (scalePositive basis) a := by
  have nz : basis ≠ 0 := Rat.ne_of_gt positive
  cases a <;> simp [resolveScale, mapNumber, scaled, nz]

theorem positive_common_unit_clamp (basis : Rat) (positive : 0 < basis) (a b c : Number) :
    resolveScale basis (specClamp a b c) =
      specClamp (resolveScale basis a) (resolveScale basis b) (resolveScale basis c) := by
  simp only [positive_resolution basis positive]
  exact map_clamp _ (scale_positive_monotone basis positive) a b c

def finiteNumber : Number → Bool
  | .nan => false
  | .value value => finiteScalar value

def hasInfinity : Number → Bool
  | .value .negInf | .value .posInf => true
  | _ => false

def safeRelative (a b c : Number) : Bool :=
  !(hasInfinity a || hasInfinity b || hasInfinity c) || !finiteNumber (specClamp a b c)

theorem strict_nan_left (b c : Number) : specClamp .nan b c = .nan := by
  cases b <;> cases c <;> rfl

theorem strict_nan_center (a c : Number) : specClamp a .nan c = .nan := by cases a <;> rfl

theorem strict_nan_upper (a b : Number) : specClamp a b .nan = .nan := by
  cases a <;> cases b <;> rfl

theorem resolve_nan (basis : Rat) : resolveScale basis .nan = .nan := rfl

theorem scalar_has_infinity (a : Scalar) : hasInfinity (.value a) = !finiteScalar a := by cases a <;> rfl

theorem zero_nonfinite (a : Scalar) (h : finiteScalar a = false) : resolveScale 0 (.value a) = .nan := by
  simp [resolveScale, h]

theorem zero_common_unit_clamp (a b c : Number) (safe : safeRelative a b c = true) :
    resolveScale 0 (specClamp a b c) =
      specClamp (resolveScale 0 a) (resolveScale 0 b) (resolveScale 0 c) := by
  cases a with
  | nan => simp only [strict_nan_left, resolve_nan]
  | value x => cases b with
    | nan => simp only [strict_nan_center, resolve_nan]
    | value y => cases c with
      | nan => simp only [strict_nan_upper, resolve_nan]
      | value z =>
        by_cases fx : finiteScalar x = true
        · by_cases fy : finiteScalar y = true
          · by_cases fz : finiteScalar z = true
            · exact finite_common_unit_clamp 0 Rat.le_refl x y z fx fy fz
            · have iz : finiteScalar z = false := Bool.eq_false_iff.mpr fz
              simp only [safeRelative, scalar_has_infinity, fx, fy, iz, Bool.not_true,
                Bool.not_false, Bool.false_or, Bool.or_true, Bool.not_eq_true] at safe
              have nonfinite : finiteScalar (maximum x (minimum y z)) = false := by simpa [finiteNumber, specClamp, strictMin, strictMax] using safe
              rw [show specClamp (.value x) (.value y) (.value z) = .value (maximum x (minimum y z)) from rfl,
                zero_nonfinite _ nonfinite, zero_nonfinite z iz, strict_nan_upper]
          · have iy : finiteScalar y = false := Bool.eq_false_iff.mpr fy
            simp only [safeRelative, scalar_has_infinity, iy, Bool.not_false,
              Bool.or_true, Bool.true_or, Bool.not_true, Bool.false_or, Bool.not_eq_true] at safe
            have nonfinite : finiteScalar (maximum x (minimum y z)) = false := by simpa [finiteNumber, specClamp, strictMin, strictMax] using safe
            rw [show specClamp (.value x) (.value y) (.value z) = .value (maximum x (minimum y z)) from rfl,
              zero_nonfinite _ nonfinite, zero_nonfinite y iy, strict_nan_center]
        · have ix : finiteScalar x = false := Bool.eq_false_iff.mpr fx
          simp only [safeRelative, scalar_has_infinity, ix, Bool.not_false,
            Bool.true_or, Bool.not_true, Bool.false_or, Bool.not_eq_true] at safe
          have nonfinite : finiteScalar (maximum x (minimum y z)) = false := by simpa [finiteNumber, specClamp, strictMin, strictMax] using safe
          rw [show specClamp (.value x) (.value y) (.value z) = .value (maximum x (minimum y z)) from rfl,
            zero_nonfinite _ nonfinite, zero_nonfinite x ix, strict_nan_left]

theorem guarded_common_unit_clamp (basis : Rat) (nonnegative : 0 ≤ basis)
    (a b c : Number) (safe : safeRelative a b c = true) :
    resolveScale basis (specClamp a b c) =
      specClamp (resolveScale basis a) (resolveScale basis b) (resolveScale basis c) := by
  by_cases zero : basis = 0
  · subst basis
    exact zero_common_unit_clamp a b c safe
  · exact positive_common_unit_clamp basis (Rat.lt_of_le_of_ne nonnegative (Ne.symm zero)) a b c

theorem safe_nonfinite_controls :
    safeRelative (.value .posInf) (.value .posInf) (.value .posInf) = true ∧
    safeRelative (.value .posInf) .nan (.value (.finite 2)) = true ∧
    safeRelative (.value (.finite 1)) (.value (.finite 2)) (.value .posInf) = false := by decide +kernel

#print axioms positive_common_unit_clamp
#print axioms zero_common_unit_clamp
#print axioms guarded_common_unit_clamp
#print axioms safe_nonfinite_controls
end ClampScaling
