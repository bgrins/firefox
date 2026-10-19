import ReloadState
namespace NativeAttributeReload

def visitLink (current next nextLowlink : Nat) (nextActive : Bool)
 (lowlink : Nat) (selfReference : Bool) : Nat × Bool :=
 if next > current then (min lowlink nextLowlink,selfReference)
 else if next = current then (lowlink,true)
 else if nextActive then (min lowlink next,selfReference)
 else (lowlink,selfReference)

theorem finished_larger_index_still_uses_lowlink (current next nextLowlink lowlink : Nat)
 (selfReference : Bool) (larger : next > current) :
 visitLink current next nextLowlink false lowlink selfReference =
 (min lowlink nextLowlink,selfReference) := by simp [visitLink,larger]

theorem repeated_finished_child_leaves_root_zero (next nextLowlink : Nat)
 (selfReference : Bool) (positive : next > 0) :
 visitLink 0 next nextLowlink false 0 selfReference = (0,selfReference) := by
 simp [visitLink,positive]

theorem earlier_finished_index_is_ignored (current next nextLowlink lowlink : Nat)
 (selfReference : Bool) (earlier : next < current) :
 visitLink current next nextLowlink false lowlink selfReference = (lowlink,selfReference) := by
 have notLarger : ¬next > current := by omega
 have notSame : next ≠ current := by omega
 simp [visitLink,notLarger,notSame]

theorem different_finished_index_does_not_mark_self_reference
 (current next nextLowlink lowlink : Nat) (selfReference : Bool) (different : next ≠ current) :
 (visitLink current next nextLowlink false lowlink selfReference).2 = selfReference := by
 unfold visitLink
 split <;> simp_all

theorem visit_link_lowlink_never_increases (current next nextLowlink lowlink : Nat)
 (active selfReference : Bool) :
 (visitLink current next nextLowlink active lowlink selfReference).1 ≤ lowlink := by
 unfold visitLink
 split
 · exact Nat.min_le_left _ _
 · split
   · exact Nat.le_refl _
   · split
     · exact Nat.min_le_left _ _
     · exact Nat.le_refl _

end NativeAttributeReload
