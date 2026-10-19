import Std
set_option autoImplicit false

namespace PolygonInterpolation

abbrev fits32 (v : Int) : Prop := -2147483648 ≤ v ∧ v ≤ 2147483647

abbrev fits64 (v : Int) : Prop := -9223372036854775808 ≤ v ∧ v ≤ 9223372036854775807

def delta (n dx d : Int) : Int := (n * dx).tdiv d

def interpolate (x1 y1 x2 y2 y : Int) : Int :=
  x1 + delta (y - y1) (x2 - x1) (y2 - y1)

def domain (x1 y1 x2 y2 y : Int) : Prop :=
  fits32 x1 ∧ fits32 y1 ∧ fits32 x2 ∧ fits32 y2 ∧ fits32 y ∧
  y1 < y2 ∧ y1 ≤ y ∧ y ≤ y2 ∧ y2 - y1 ≤ 2147483646 ∧
  -2147483646 ≤ x2 - x1 ∧ x2 - x1 ≤ 2147483646

theorem positive_slope_bounds (n dx d : Int)
    (hn : 0 ≤ n) (hnd : n ≤ d) (hd : 0 < d) (hx : 0 ≤ dx) :
    0 ≤ delta n dx d ∧ delta n dx d ≤ dx := by
  have hmul := Int.mul_nonneg hn hx
  have hupper := Int.mul_le_mul_of_nonneg_right hnd hx
  have hlo := Int.tdiv_nonneg hmul (Int.le_of_lt hd)
  have hhi := Int.tdiv_le_tdiv hd hupper
  have hnz : d ≠ 0 := by omega
  simpa [delta, Int.mul_tdiv_cancel_left dx hnz] using And.intro hlo hhi

theorem negative_slope_bounds (n dx d : Int)
    (hn : 0 ≤ n) (hnd : n ≤ d) (hd : 0 < d) (hx : dx ≤ 0) :
    dx ≤ delta n dx d ∧ delta n dx d ≤ 0 := by
  have hmul := Int.mul_nonpos_of_nonneg_of_nonpos hn hx
  have hlower := Int.mul_le_mul_of_nonpos_right hnd hx
  have hlo := Int.tdiv_le_tdiv hd hlower
  have hhi := Int.tdiv_le_tdiv hd hmul
  have hnz : d ≠ 0 := by omega
  simpa [delta, Int.mul_tdiv_cancel_left dx hnz] using And.intro hlo hhi

theorem endpoint_containment (x1 y1 x2 y2 y : Int)
    (hy : y1 < y2) (hlo : y1 ≤ y) (hhi : y ≤ y2) :
    min x1 x2 ≤ interpolate x1 y1 x2 y2 y ∧
    interpolate x1 y1 x2 y2 y ≤ max x1 x2 := by
  have hn : 0 ≤ y - y1 := by omega
  have hnd : y - y1 ≤ y2 - y1 := by omega
  have hd : 0 < y2 - y1 := by omega
  by_cases hx : 0 ≤ x2 - x1
  · have h := positive_slope_bounds (y-y1) (x2-x1) (y2-y1) hn hnd hd hx
    simp only [interpolate]
    omega
  · have h := negative_slope_bounds (y-y1) (x2-x1) (y2-y1) hn hnd hd (by omega)
    simp only [interpolate]
    omega

theorem first_endpoint (x1 y1 x2 y2 : Int) :
    interpolate x1 y1 x2 y2 y1 = x1 := by simp [interpolate, delta]

theorem second_endpoint (x1 y1 x2 y2 : Int) (hy : y1 < y2) :
    interpolate x1 y1 x2 y2 y2 = x2 := by
  have hnz : y2 - y1 ≠ 0 := by omega
  simp only [interpolate, delta, Int.mul_tdiv_cancel_left (x2-x1) hnz]
  omega

theorem product_bound (n dx : Int)
    (hn : 0 ≤ n) (hnmax : n ≤ 2147483646)
    (hxlo : -2147483646 ≤ dx) (hxhi : dx ≤ 2147483646) :
    -4611686009837453316 ≤ n * dx ∧ n * dx ≤ 4611686009837453316 := by
  have hlo := Int.mul_le_mul_of_nonneg_left hxlo hn
  have hhi := Int.mul_le_mul_of_nonneg_left hxhi hn
  omega

theorem subtraction_ranges (x1 y1 x2 y2 y : Int)
    (h : domain x1 y1 x2 y2 y) :
    fits32 (y-y1) ∧ fits32 (x2-x1) ∧ fits32 (y2-y1) ∧
    0 ≤ y-y1 ∧ y-y1 ≤ y2-y1 ∧ 0 < y2-y1 := by
  simp only [domain, fits32] at *
  omega

theorem all_intermediates_representable (x1 y1 x2 y2 y : Int)
    (h : domain x1 y1 x2 y2 y) :
    fits64 ((y-y1)*(x2-x1)) ∧
    fits32 (delta (y-y1) (x2-x1) (y2-y1)) ∧
    fits32 (interpolate x1 y1 x2 y2 y) := by
  have hs := subtraction_ranges x1 y1 x2 y2 y h
  have hp := product_bound (y-y1) (x2-x1) hs.2.2.2.1 (by simp [domain] at h; omega)
    (by simp [domain] at h; omega) (by simp [domain] at h; omega)
  have hc := endpoint_containment x1 y1 x2 y2 y
    (by simp [domain] at h; omega) (by simp [domain] at h; omega) (by simp [domain] at h; omega)
  have hq : -2147483646 ≤ delta (y-y1) (x2-x1) (y2-y1) ∧
      delta (y-y1) (x2-x1) (y2-y1) ≤ 2147483646 := by
    by_cases hx : 0 ≤ x2-x1
    · have hb := positive_slope_bounds (y-y1) (x2-x1) (y2-y1)
        hs.2.2.2.1 hs.2.2.2.2.1 hs.2.2.2.2.2 hx
      simp only [domain] at h
      omega
    · have hb := negative_slope_bounds (y-y1) (x2-x1) (y2-y1)
        hs.2.2.2.1 hs.2.2.2.2.1 hs.2.2.2.2.2 (by omega)
      simp only [domain] at h
      omega
  simp only [domain, fits32, fits64] at *
  omega

def wideEvaluation (x1 y1 x2 y2 y : Int) : Option Int :=
  let product := (y-y1)*(x2-x1)
  let step := product.tdiv (y2-y1)
  if fits64 product ∧ fits32 step ∧ fits32 (x1+step) then some (x1+step) else none

def oldEvaluation (x1 y1 x2 y2 y : Int) : Option Int :=
  let product := (y-y1)*(x2-x1)
  let step := product.tdiv (y2-y1)
  if fits32 product ∧ fits32 step ∧ fits32 (x1+step) then some (x1+step) else none

theorem wide_evaluation_exact (x1 y1 x2 y2 y : Int)
    (h : domain x1 y1 x2 y2 y) :
    wideEvaluation x1 y1 x2 y2 y = some (interpolate x1 y1 x2 y2 y) := by
  have hb := all_intermediates_representable x1 y1 x2 y2 y h
  exact ite_eq_left hb

theorem old_defined_compatibility (x1 y1 x2 y2 y : Int)
    (h : domain x1 y1 x2 y2 y) (hp : fits32 ((y-y1)*(x2-x1))) :
    oldEvaluation x1 y1 x2 y2 y = wideEvaluation x1 y1 x2 y2 y := by
  rw [wide_evaluation_exact x1 y1 x2 y2 y h]
  have hb := all_intermediates_representable x1 y1 x2 y2 y h
  exact ite_eq_left ⟨hp, hb.2⟩

theorem translation_invariance (x1 y1 x2 y2 y tx ty : Int) :
    interpolate (x1+tx) (y1+ty) (x2+tx) (y2+ty) (y+ty) =
      interpolate x1 y1 x2 y2 y + tx := by
  have hx : x2+tx-(x1+tx) = x2-x1 := by omega
  have hy : y2+ty-(y1+ty) = y2-y1 := by omega
  have hn : y+ty-(y1+ty) = y-y1 := by omega
  simp only [interpolate, hx, hy, hn]
  omega

theorem common_offset_difference_bound (a b t : Int)
    (ha : -1073741823 ≤ a ∧ a ≤ 1073741823)
    (hb : -1073741823 ≤ b ∧ b ≤ 1073741823) :
    -2147483646 ≤ (b+t)-(a+t) ∧ (b+t)-(a+t) ≤ 2147483646 := by omega

theorem common_reflection_difference_bound (a b t : Int)
    (ha : -1073741823 ≤ a ∧ a ≤ 1073741823)
    (hb : -1073741823 ≤ b ∧ b ≤ 1073741823) :
    -2147483646 ≤ (t-b)-(t-a) ∧ (t-b)-(t-a) ≤ 2147483646 := by omega

theorem rounding_anchor_counterexample :
    interpolate 5 0 4 2 1 = 5 ∧ (5*2+(1-0)*(4-5) : Int).tdiv 2 = 4 := by decide

theorem old_product_counterexample :
    ¬ fits32 ((12000 : Int) * 600000) ∧
    interpolate 0 0 600000 600000 12000 = 12000 := by decide

#print axioms positive_slope_bounds
#print axioms negative_slope_bounds
#print axioms endpoint_containment
#print axioms first_endpoint
#print axioms second_endpoint
#print axioms product_bound
#print axioms subtraction_ranges
#print axioms all_intermediates_representable
#print axioms wide_evaluation_exact
#print axioms old_defined_compatibility
#print axioms translation_invariance
#print axioms common_offset_difference_bound
#print axioms common_reflection_difference_bound
#print axioms rounding_anchor_counterexample
#print axioms old_product_counterexample
end PolygonInterpolation
