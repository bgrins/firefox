import Std
namespace FlexCrossSize

def limit : Int := 1073741823

def groupMaximum (firstStart firstEnd lastStart lastEnd ordinary : Int) : Int :=
  max (max (firstStart + firstEnd) (lastStart + lastEnd)) ordinary

def repaired (firstStart firstEnd lastStart lastEnd ordinary : Int) : Int :=
  min limit (groupMaximum firstStart firstEnd lastStart lastEnd ordinary)

theorem widened_addition_is_int64 (a b : Int)
    (ha : -2147483648 ≤ a ∧ a ≤ 2147483647)
    (hb : -2147483648 ≤ b ∧ b ≤ 2147483647) :
    -9223372036854775808 ≤ a + b ∧ a + b ≤ 9223372036854775807 := by omega

theorem repaired_result_is_coord (a b c d ordinary : Int) (ho : 0 ≤ ordinary) :
    0 ≤ repaired a b c d ordinary ∧ repaired a b c d ordinary ≤ limit := by
  have hm : ordinary ≤ groupMaximum a b c d ordinary := Int.le_max_right _ _
  have hl : 0 ≤ limit := by decide
  unfold repaired
  omega

theorem finite_maximum_observer_preserved (a b c d ordinary cap : Int)
    (hc : cap ≤ limit) :
    min cap (repaired a b c d ordinary) =
      min cap (groupMaximum a b c d ordinary) := by
  unfold repaired
  omega

theorem already_representable_unchanged (a b c d ordinary : Int)
    (bound : groupMaximum a b c d ordinary ≤ limit) :
    repaired a b c d ordinary = groupMaximum a b c d ordinary := by
  unfold repaired
  exact Int.min_eq_right bound

theorem absent_groups_still_zero : repaired (-limit) (-limit) (-limit) (-limit) 0 = 0 := by
  decide +kernel

theorem browser_witness_clamps_to_100px :
    min 6000 (repaired 720000000 1440000000 (-limit) (-limit) 0) = 6000 := by
  decide +kernel

#print axioms widened_addition_is_int64
#print axioms repaired_result_is_coord
#print axioms finite_maximum_observer_preserved
#print axioms already_representable_unchanged
#print axioms absent_groups_still_zero
#print axioms browser_witness_clamps_to_100px
end FlexCrossSize
