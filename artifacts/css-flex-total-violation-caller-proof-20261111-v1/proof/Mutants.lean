import Universal
import Witness

namespace FlexViolationCaller

def droppedCount : Pass :=
  { firstPass with after := { firstPass.after with frozenCount := 0 } }

def prematureFinal : Pass :=
  (runPass 1 (start twoSeeds true false).line [-1,5]).getD emptyPass

def reversedAfter : Pass :=
  { secondPass with after := { secondPass.after with items := secondPass.after.items.reverse } }

theorem dropped_count_wrong : droppedCount.after.frozenCount = 0 ∧
    countedFrozen droppedCount.after.items = 1 := by decide

theorem dropped_count_refutes : ¬CountAgrees droppedCount.after := by
  unfold CountAgrees
  decide

theorem premature_final_wrong : prematureFinal.helper.fallback = true ∧
    prematureFinal.after.frozenCount = 2 ∧
    (FlexViolation.frozen ((active prematureFinal.prepared.items).map asItem)).length = 1 := by decide

theorem premature_final_refutes :
    newlySelected prematureFinal.prepared.items prematureFinal.after.items ≠
      FlexViolation.frozen ((active prematureFinal.prepared.items).map asItem) := by decide

theorem reversed_after_wrong :
    reversedAfter.after.items.map (fun item => (item.fields.identity, item.current)) = [(9,5),(9,0)] := by decide

theorem reversed_after_refutes : reversedAfter.after.items ≠ secondPass.after.items := by decide

theorem corrupt_count_actual_walk :
    let bad := { (start twoSeeds true false).line with frozenCount := 2 }
    ∃ pass, runPass 0 bad [-1,5] = some pass ∧
      remaining pass.after = 2 ∧ pass.clamped.violation = 0 ∧ pass.helper.newlyFrozen = 0 := by
  refine ⟨(runPass 0 { (start twoSeeds true false).line with frozenCount := 2 }
    [-1,5]).getD emptyPass, ?_⟩
  decide

end FlexViolationCaller
