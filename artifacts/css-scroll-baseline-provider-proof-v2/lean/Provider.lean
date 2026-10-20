import Std
namespace ScrollBaselineProvider

def clamp (size value : Int) : Int := max 0 (min size value)
def fromStart (first : Bool) (size distance : Int) : Int :=
  if first then distance else size - distance
def repaired (first : Bool) (outer inner border distance : Int) : Int :=
  fromStart first outer (clamp outer (border + fromStart first inner distance))
def original (outer border distance : Int) : Int := clamp outer (border + distance)

theorem orientation_is_involutive (first : Bool) (size distance : Int) :
    fromStart first size (fromStart first size distance) = distance := by
  cases first <;> simp [fromStart] <;> omega

theorem output_preserves_clamped_physical_baseline
    (first : Bool) (outer inner border distance : Int) :
    fromStart first outer (repaired first outer inner border distance) =
      clamp outer (border + fromStart first inner distance) := by
  exact orientation_is_involutive first outer _

theorem clamp_bounds (outer value : Int) (valid : 0 ≤ outer) :
    0 ≤ clamp outer value ∧ clamp outer value ≤ outer := by
  unfold clamp
  omega

theorem result_is_within_border_box (first : Bool) (outer inner border distance : Int)
    (valid : 0 ≤ outer) :
    0 ≤ repaired first outer inner border distance ∧
      repaired first outer inner border distance ≤ outer := by
  have h := clamp_bounds outer (border + fromStart first inner distance) valid
  cases first <;> simp only [repaired,fromStart,ite_true,Bool.false_eq_true,ite_false] at * <;> omega

theorem first_group_is_preserved (outer inner border distance : Int) :
    repaired true outer inner border distance = original outer border distance := by
  rfl

theorem last_group_interior_conversion (outer inner border distance : Int)
    (lower : 0 ≤ border + inner - distance)
    (upper : border + inner - distance ≤ outer) :
    repaired false outer inner border distance = outer - border - inner + distance := by
  unfold repaired fromStart clamp
  simp only [Bool.false_eq_true,ite_false]
  omega

theorem asymmetric_border_error (outer inner start finish distance : Int)
    (sizes : outer = start + inner + finish)
    (oldLower : 0 ≤ start + distance) (oldUpper : start + distance ≤ outer)
    (newLower : 0 ≤ start + inner - distance)
    (newUpper : start + inner - distance ≤ outer) :
    original outer start distance - repaired false outer inner start distance = start - finish := by
  have h := last_group_interior_conversion outer inner start distance newLower newUpper
  unfold original clamp
  omega

theorem symmetric_borders_are_an_interior_control (outer inner border distance : Int)
    (sizes : outer = border + inner + border)
    (oldLower : 0 ≤ border + distance) (oldUpper : border + distance ≤ outer)
    (newLower : 0 ≤ border + inner - distance)
    (newUpper : border + inner - distance ≤ outer) :
    original outer border distance = repaired false outer inner border distance := by
  have h := asymmetric_border_error outer inner border border distance sizes
    oldLower oldUpper newLower newUpper
  omega

theorem last_baseline_after_border_clamps_to_end (outer inner border distance : Int)
    (valid : 0 ≤ outer) (outside : outer ≤ border + inner - distance) :
    repaired false outer inner border distance = 0 := by
  unfold repaired fromStart clamp
  simp only [Bool.false_eq_true,ite_false]
  omega

theorem last_baseline_before_border_clamps_to_start (outer inner border distance : Int)
    (outside : border + inner - distance ≤ 0) :
    repaired false outer inner border distance = outer := by
  unfold repaired fromStart clamp
  simp only [Bool.false_eq_true,ite_false]
  omega

theorem replacing_start_border_with_end_is_insufficient :
    repaired false 60 200 9 10 = 0 ∧ clamp 60 (1 + 10) = 11 := by decide +kernel

theorem literal_asymmetric_counterexample :
    original 59 9 30 = 39 ∧ repaired false 59 50 9 30 = 30 ∧
    original 59 0 30 = 30 ∧ repaired false 59 50 0 30 = 39 := by decide +kernel

theorem widened_native_intermediates_fit (inner border distance : Int)
    (hi : 0 ≤ inner ∧ inner ≤ 2147483647)
    (hb : 0 ≤ border ∧ border ≤ 2147483647)
    (hd : -2147483648 ≤ distance ∧ distance ≤ 2147483647) :
    -9223372036854775808 ≤ inner - distance ∧
    inner - distance ≤ 9223372036854775807 ∧
    -9223372036854775808 ≤ border + inner - distance ∧
    border + inner - distance ≤ 9223372036854775807 ∧
    -9223372036854775808 ≤ border + distance ∧
    border + distance ≤ 9223372036854775807 := by omega

theorem narrowing_and_final_subtraction_fit (first : Bool) (outer inner border distance : Int)
    (valid : 0 ≤ outer ∧ outer ≤ 2147483647) :
    0 ≤ clamp outer (border + fromStart first inner distance) ∧
    clamp outer (border + fromStart first inner distance) ≤ 2147483647 ∧
    0 ≤ repaired first outer inner border distance ∧
    repaired first outer inner border distance ≤ 2147483647 := by
  have h := clamp_bounds outer (border + fromStart first inner distance) valid.1
  have h' := result_is_within_border_box first outer inner border distance valid.1
  omega

end ScrollBaselineProvider
