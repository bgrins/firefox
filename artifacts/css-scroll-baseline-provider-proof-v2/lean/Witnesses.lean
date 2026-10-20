import Dispatch
namespace ScrollBaselineWitnesses
open ScrollBaselineProvider ScrollBaselineDispatch

def input : Input := ⟨false,false,true,false,false,59,50,9,77,some 30⟩

theorem asymmetry : (native input).value = some 30 ∧ original 59 9 30 = 39 := by decide +kernel

theorem containment_legacy_order :
    (native { input with lineLayout := true, contain := true }).value = some 77 := by decide +kernel

theorem button_containment :
    (native { input with lineLayout := true, button := true, contain := true }).value = none := by decide +kernel

theorem absent_has_no_geometry_queries :
    native { input with child := none } = ⟨none,[.containment,.child]⟩ := by decide +kernel

theorem zero_not_absence :
    (native { input with child := some 0 }).value = some 0 := by decide +kernel

theorem arbitrary_size_requires_conversion :
    (native { input with outer := 60, inner := 200, child := some 10 }).value = some 0 ∧
    clamp 60 (1+10) = 11 := by decide +kernel

theorem child_before_start_clamped :
    (native { input with child := some 100 }).value = some 59 := by decide +kernel

theorem widened_before_clamp :
    (native { input with first := true, outer := 100, border := 2147483647, child := some 2147483647 }).value = some 100 := by decide +kernel

theorem original_int32_sum_not_safe :
    2147483647 + (2147483647 : Int) > 2147483647 := by decide +kernel

theorem first_queries_no_inner :
    (native { input with first := true }).calls = [.containment,.child,.border,.outer] := by decide +kernel

theorem last_queries_inner_before_border :
    (native input).calls = [.containment,.child,.inner,.border,.outer] := by decide +kernel

theorem mutant_0 : original 59 9 30 ≠ (30 : Int) := by decide +kernel

theorem mutant_1 : clamp 60 (1+10) ≠ (0 : Int) := by decide +kernel

theorem mutant_2 : (none : Option Int) ≠ (native { input with lineLayout := true, contain := true }).value := by decide +kernel

theorem mutant_3 : (some 0 : Option Int) ≠ (native { input with child := none }).value := by decide +kernel

theorem mutant_4 : (60-(9+200-10) : Int) ≠ (0 : Int) := by decide +kernel

theorem mutant_5 : (some (clamp 59 77) : Option Int) ≠ (native { input with lineLayout := true }).value := by decide +kernel

end ScrollBaselineWitnesses
