import Lean
namespace ObserverBoundaries
def temporary (content consumed border available : Int) :=
  min (content-consumed+border) available
def clampLower (x : Int) := max 0 x
theorem first_fragment_unchanged (c b a : Int)
    (hc : 0 ≤ c) (hb : 0 ≤ b) (ha : 0 ≤ a) :
    clampLower (temporary c 0 b a) = temporary c 0 b a := by
  unfold clampLower temporary; omega
theorem nonnegative_content_is_not_enough :
    temporary 80 0 0 (-1) = -1 ∧
    clampLower (temporary 80 0 0 (-1)) = 0 := by decide
def minmax (x : Int) (lower upper : Option Int) : Int :=
  let x := match upper with | none => x | some u => min x u
  match lower with | none => x | some l => max x l
theorem minmax_lower_nonnegative (x u l : Int) (hl : 0 ≤ l) :
    0 ≤ minmax x (some l) (some u) := by
  simp only [minmax]; omega
theorem minmax_unconstrained_min_requires_upper (x u : Int)
    (hx : 0 ≤ x) (hu : 0 ≤ u) : 0 ≤ minmax x none (some u) := by
  simp only [minmax]; omega
def alignedPhysical (computed temporary origin alignment final size : Int) :=
  final - ((computed - (temporary-origin) + alignment) + size)
theorem alignment_add_preserves_dependency (c t p a f s d : Int) :
    alignedPhysical c (t+d) p a f s = alignedPhysical c t p a f s + d := by
  unfold alignedPhysical; omega
theorem definite_consistent_origin (t p a s : Int) :
    alignedPhysical t t p a t s = t-p-a-s := by
  unfold alignedPhysical; omega
def machineMax : Int := 2147483647
theorem cumulative_third_fragment_overflow :
    0 ≤ (1920000000 : Int) ∧ 1920000000 ≤ machineMax ∧
    0 ≤ (960000000 : Int) ∧ 960000000 ≤ machineMax ∧
    machineMax < 1920000000 + 960000000 := by decide
theorem small_original_sum_does_not_bound_fragment_prefix :
    (12*80*60 : Int) < 4*16000000*60 := by decide
end ObserverBoundaries
#print axioms ObserverBoundaries.first_fragment_unchanged
#print axioms ObserverBoundaries.nonnegative_content_is_not_enough
#print axioms ObserverBoundaries.minmax_lower_nonnegative
#print axioms ObserverBoundaries.minmax_unconstrained_min_requires_upper
#print axioms ObserverBoundaries.alignment_add_preserves_dependency
#print axioms ObserverBoundaries.definite_consistent_origin
#print axioms ObserverBoundaries.cumulative_third_fragment_overflow
#print axioms ObserverBoundaries.small_original_sum_does_not_bound_fragment_prefix
