import Subtree
namespace Independent
open Subtree

def clean : Tree := .node 2 false false false []
def tableRoot : Tree := .node 1 false false true [clean]
def eligibleBarrier : Tree := .node 1 true false false [.node 2 false true false []]
def world : World := ⟨true, [tableRoot], [clean], [clean], [clean]⟩

theorem root_vs_descendant_table :
    eligibleAt [0] (markRoot tableRoot) = true ∧
    eligibleAt [0] (markDesc tableRoot) = false := by simp [eligibleAt, locate, markRoot, markDesc, tableRoot, clean, eligibleBarrier, rootClosure, allDirty, allDirtyList, eligible, clearRootPath, markPrincipal, world, forceAll, Hidden.geometryQuery, Hidden.measure, Hidden.canReuse, Hidden.fixedBlock, Hidden.key, Hidden.warm, dirty]

theorem closure_stronger_than_query_eligibility :
    rootClosure eligibleBarrier = false ∧
    eligibleAt [] (markRoot eligibleBarrier) = true ∧
    eligibleAt [0] (markRoot eligibleBarrier) = true := by simp [eligibleAt, locate, markRoot, markDesc, tableRoot, clean, eligibleBarrier, rootClosure, allDirty, allDirtyList, eligible, clearRootPath, markPrincipal, world, forceAll, Hidden.geometryQuery, Hidden.measure, Hidden.canReuse, Hidden.fixedBlock, Hidden.key, Hidden.warm, dirty]

theorem clear_path_not_necessary :
    clearRootPath [0] eligibleBarrier = false ∧
    eligibleAt [0] (markRoot eligibleBarrier) = true := by simp [eligibleAt, locate, markRoot, markDesc, tableRoot, clean, eligibleBarrier, rootClosure, allDirty, allDirtyList, eligible, clearRootPath, markPrincipal, world, forceAll, Hidden.geometryQuery, Hidden.measure, Hidden.canReuse, Hidden.fixedBlock, Hidden.key, Hidden.warm, dirty]

theorem container_dirty_does_not_prune_principal :
    ((markPrincipal world).principal[0]?).any (eligibleAt [0]) = true ∧
    (markPrincipal world).ownDirty = true := by simp [eligibleAt, locate, markRoot, markDesc, tableRoot, clean, eligibleBarrier, rootClosure, allDirty, allDirtyList, eligible, clearRootPath, markPrincipal, world, forceAll, Hidden.geometryQuery, Hidden.measure, Hidden.canReuse, Hidden.fixedBlock, Hidden.key, Hidden.warm, dirty]

theorem other_targets_not_followed :
    ((markPrincipal world).externalOutOfFlow[0]?).any eligible = false ∧
    ((markPrincipal world).nextContinuation[0]?).any eligible = false ∧
    ((markPrincipal world).otherLists[0]?).any eligible = false := by simp [eligibleAt, locate, markRoot, markDesc, tableRoot, clean, eligibleBarrier, rootClosure, allDirty, allDirtyList, eligible, clearRootPath, markPrincipal, world, forceAll, Hidden.geometryQuery, Hidden.measure, Hidden.canReuse, Hidden.fixedBlock, Hidden.key, Hidden.warm, dirty]

theorem producer_crosses_both_barriers :
    allDirty (forceAll (.node 0 true false false [tableRoot])) = true ∧
    allDirty (markRoot (.node 0 true false false [tableRoot])) = false := by simp [eligibleAt, locate, markRoot, markDesc, tableRoot, clean, eligibleBarrier, rootClosure, allDirty, allDirtyList, eligible, clearRootPath, markPrincipal, world, forceAll, Hidden.geometryQuery, Hidden.measure, Hidden.canReuse, Hidden.fixedBlock, Hidden.key, Hidden.warm, dirty]

theorem h_flag_does_not_prune :
    eligibleAt [0] (markRoot (.node 0 false true false [clean])) = true := by simp [eligibleAt, locate, markRoot, markDesc, tableRoot, clean, eligibleBarrier, rootClosure, allDirty, allDirtyList, eligible, clearRootPath, markPrincipal, world, forceAll, Hidden.geometryQuery, Hidden.measure, Hidden.canReuse, Hidden.fixedBlock, Hidden.key, Hidden.warm, dirty]

theorem recovery_does_not_certify_provider (f : Hidden.Frame) :
    (Hidden.geometryQuery true (fun _ => Hidden.zero) (Hidden.key 0)
      {f with dirty := eligible (markRoot clean)}).geometry = Hidden.zero := by
  apply Hidden.dirty_query_uses_actual_provider
  exact root_is_eligible clean

theorem query_does_not_update_tree :
    let tree := markRoot clean
    let frame := Hidden.geometryQuery true Hidden.fixedBlock (Hidden.key 0)
      {Hidden.warm with dirty := eligible tree}
    frame.dirty = false ∧ dirty tree = true := by simp [eligibleAt, locate, markRoot, markDesc, tableRoot, clean, eligibleBarrier, rootClosure, allDirty, allDirtyList, eligible, clearRootPath, markPrincipal, world, forceAll, Hidden.geometryQuery, Hidden.measure, Hidden.canReuse, Hidden.fixedBlock, Hidden.key, Hidden.warm, dirty]

#print axioms root_vs_descendant_table
#print axioms closure_stronger_than_query_eligibility
#print axioms clear_path_not_necessary
#print axioms container_dirty_does_not_prune_principal
#print axioms other_targets_not_followed
#print axioms producer_crosses_both_barriers
#print axioms h_flag_does_not_prune
#print axioms recovery_does_not_certify_provider
#print axioms query_does_not_update_tree
end Independent
