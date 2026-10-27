import Std

namespace CentralSynthesis

def halfAway (total : Int) : Int := total.tdiv 2 + total.tmod 2

def oriented (inverted : Bool) (extent startMargin endMargin : Int) : Int :=
  halfAway (extent + startMargin + endMargin) -
    if inverted then endMargin else startMargin

def physicalStart (inverted : Bool) (extent startMargin endMargin : Int) : Int :=
  if inverted then extent - oriented inverted extent startMargin endMargin
  else oriented inverted extent startMargin endMargin

def offset (first : Bool) (extent start : Int) : Int :=
  if first then start else extent - start

def decode (first : Bool) (extent value : Int) : Int :=
  if first then value else extent - value

def originAware (inverted first : Bool) (extent startMargin endMargin : Int) : Int :=
  let raw := oriented inverted extent startMargin endMargin
  if first != inverted then raw else extent - raw

def adjustedGroup (inverted first : Bool) : Bool :=
  if inverted then !first else first

def sourceExpression (inverted first : Bool) (extent startMargin endMargin : Int) : Int :=
  let raw := oriented inverted extent startMargin endMargin
  if adjustedGroup inverted first then raw else extent - raw

theorem sourceExpression_eq (inverted first : Bool) (extent startMargin endMargin : Int) :
    sourceExpression inverted first extent startMargin endMargin =
      originAware inverted first extent startMargin endMargin := by
  cases inverted <;> cases first <;> rfl

theorem half_error (total : Int) :
    2 * halfAway total - total = total.tmod 2 := by
  have := Int.tmod_add_mul_tdiv total 2
  unfold halfAway
  omega

theorem remainder_bounds (total : Int) :
    -1 ≤ total.tmod 2 ∧ total.tmod 2 ≤ 1 := by
  have upper := Int.tmod_lt_of_pos total (b := 2) (by decide)
  have lower := Int.tmod_lt_of_pos (-total) (b := 2) (by decide)
  rw [Int.neg_tmod] at lower
  omega

theorem half_even (k : Int) : halfAway (2 * k) = k := by
  have := half_error (2 * k)
  have := remainder_bounds (2 * k)
  omega

theorem half_positive_odd (k : Int) (nonnegative : 0 ≤ k) :
    halfAway (2 * k + 1) = k + 1 := by
  have := half_error (2 * k + 1)
  have := remainder_bounds (2 * k + 1)
  have := Int.tmod_nonneg 2 (a := 2 * k + 1) (by omega)
  omega

theorem half_negative_odd (k : Int) (nonnegative : 0 ≤ k) :
    halfAway (-(2 * k + 1)) = -(k + 1) := by
  have := half_error (-(2 * k + 1))
  have := remainder_bounds (-(2 * k + 1))
  have sign := Int.tmod_nonneg 2 (a := 2 * k + 1) (by omega)
  have negative := Int.neg_tmod (2 * k + 1) 2
  omega

theorem decode_offset (first : Bool) (extent start : Int) :
    decode first extent (offset first extent start) = start := by
  cases first <;> simp [decode, offset] <;> omega

theorem originAware_origin (inverted first : Bool) (extent startMargin endMargin : Int) :
    originAware inverted first extent startMargin endMargin =
      offset first extent (physicalStart inverted extent startMargin endMargin) := by
  cases inverted <;> cases first <;>
    simp [originAware, offset, physicalStart] <;> omega

theorem same_physical_point (inverted first : Bool) (extent startMargin endMargin : Int) :
    decode first extent (originAware inverted first extent startMargin endMargin) =
      physicalStart inverted extent startMargin endMargin := by
  rw [originAware_origin, decode_offset]

theorem midpoint_error (inverted : Bool) (extent startMargin endMargin : Int) :
    2 * physicalStart inverted extent startMargin endMargin -
        (extent - startMargin + endMargin) =
      if inverted then -(extent + startMargin + endMargin).tmod 2
      else (extent + startMargin + endMargin).tmod 2 := by
  have := half_error (extent + startMargin + endMargin)
  cases inverted <;> simp only [physicalStart, oriented, Bool.false_eq_true,
    ite_false, ite_true] <;> omega

theorem midpoint_half_unit_bound (inverted : Bool) (extent startMargin endMargin : Int) :
    -1 ≤ 2 * physicalStart inverted extent startMargin endMargin -
        (extent - startMargin + endMargin) ∧
      2 * physicalStart inverted extent startMargin endMargin -
        (extent - startMargin + endMargin) ≤ 1 := by
  rw [midpoint_error]
  have := remainder_bounds (extent + startMargin + endMargin)
  cases inverted <;> simp only [Bool.false_eq_true, ite_false, ite_true] <;> omega

theorem legacy_consistency_iff (inverted : Bool) (extent startMargin endMargin : Int) :
    decode true extent (oriented inverted extent startMargin endMargin) =
      decode false extent (oriented inverted extent startMargin endMargin) ↔
      2 * oriented inverted extent startMargin endMargin = extent := by
  simp only [decode, ite_true, Bool.false_eq_true, ite_false]
  omega

def firstAnchored (inverted first : Bool) (extent startMargin endMargin : Int) : Int :=
  offset first extent (oriented inverted extent startMargin endMargin)

theorem firstAnchored_consistent (inverted first : Bool) (extent startMargin endMargin : Int) :
    decode first extent (firstAnchored inverted first extent startMargin endMargin) =
      oriented inverted extent startMargin endMargin := by
  exact decode_offset first extent _

theorem independent_rounding_error (extent startMargin endMargin : Int) :
    (halfAway (extent + startMargin + endMargin) - startMargin) +
      (halfAway (extent + startMargin + endMargin) - endMargin) - extent =
      (extent + startMargin + endMargin).tmod 2 := by
  have := half_error (extent + startMargin + endMargin)
  omega

theorem inverted_policy_difference :
    firstAnchored true true 100 10 30 = 40 ∧
    firstAnchored true false 100 10 30 = 60 ∧
    physicalStart true 100 10 30 = 60 := by
  decide +kernel

theorem asymmetric_witness :
    oriented false 100 10 30 = 60 ∧ oriented true 100 10 30 = 40 ∧
    originAware false true 100 10 30 = 60 ∧ originAware false false 100 10 30 = 40 ∧
    originAware true true 100 10 30 = 60 ∧ originAware true false 100 10 30 = 40 := by
  decide +kernel

theorem odd_signed_witnesses :
    halfAway 141 = 71 ∧ halfAway (-141) = -71 ∧
    physicalStart false 101 10 30 = 61 ∧ physicalStart true 101 10 30 = 60 ∧
    physicalStart false 1 (-4) 0 = 2 ∧ physicalStart true 1 (-4) 0 = 3 := by
  decide +kernel

end CentralSynthesis

#print axioms CentralSynthesis.half_error
#print axioms CentralSynthesis.remainder_bounds
#print axioms CentralSynthesis.half_even
#print axioms CentralSynthesis.half_positive_odd
#print axioms CentralSynthesis.half_negative_odd
#print axioms CentralSynthesis.decode_offset
#print axioms CentralSynthesis.originAware_origin
#print axioms CentralSynthesis.same_physical_point
#print axioms CentralSynthesis.midpoint_error
#print axioms CentralSynthesis.midpoint_half_unit_bound
#print axioms CentralSynthesis.legacy_consistency_iff
#print axioms CentralSynthesis.asymmetric_witness
#print axioms CentralSynthesis.odd_signed_witnesses

#print axioms CentralSynthesis.firstAnchored_consistent
#print axioms CentralSynthesis.independent_rounding_error
#print axioms CentralSynthesis.inverted_policy_difference

#print axioms CentralSynthesis.sourceExpression_eq
