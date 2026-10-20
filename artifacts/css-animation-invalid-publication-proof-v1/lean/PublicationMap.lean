import Cow
import PublicationLaws
namespace InvalidPublication
variable {K P : Type} [DecidableEq K]

def removalCompare : Option P → Option P → Bool
  | none, none => true
  | _, _ => false

theorem removal_comparator_sound : LiveCount.CompareSound (removalCompare (P := P)) := by
  intro a b h
  cases a <;> cases b <;> simp_all [removalCompare]

theorem removal_lookup (s : LiveCount.Store K P) (unique : Bool) (k q : K) :
    LiveCount.lookup (LiveCount.doInsert unique removalCompare s k none).chain q =
      if q = k then none else LiveCount.lookup s.chain q :=
  LiveCount.cow_lookup s k q none unique removalCompare removal_comparator_sound

theorem removal_ready (s : LiveCount.Store K P) (unique : Bool) (ks : List K) (k : K)
    (keysUnique : ks.Nodup) (member : k ∈ ks) (ready : LiveCount.Ready ks s) :
    LiveCount.Ready ks (LiveCount.doInsert unique removalCompare s k none) :=
  LiveCount.cow_ready ks s k none unique removalCompare keysUnique member ready

def projectStores (stores : Bool → LiveCount.Store K P) (seen : K → Bool) (cycles : Bool) :
    State K P := ⟨fun r k => LiveCount.lookup (stores r).chain k, seen, cycles⟩

def removeRouted (stores : Bool → LiveCount.Store K P) (route : Bool) (k : K)
    (unique : Bool) : Bool → LiveCount.Store K P :=
  fun r => if r = route then LiveCount.doInsert unique removalCompare (stores r) k none else stores r

theorem routed_removal_projection (stores : Bool → LiveCount.Store K P) (route : Bool)
    (k : K) (unique : Bool) (seen : K → Bool) (cycles : Bool) :
    projectStores (removeRouted stores route k unique) seen cycles =
      put (projectStores stores seen cycles) route k none := by
  unfold projectStores put
  congr 1
  funext r q
  by_cases h : r = route
  · simp [projectStores, removeRouted, put, h, removal_lookup]
  · simp [projectStores, removeRouted, put, h]

theorem tombstone_masks_parent (parent : LiveCount.Chain K P) (k : K) :
    LiveCount.lookup ([(k, none)] :: parent) k = none := by
  simp [LiveCount.lookup, LiveCount.ownFind]

theorem removing_last_retains_ready (s : LiveCount.Store K P) (k : K) (unique : Bool)
    (ready : LiveCount.Ready [k] s) :
    (LiveCount.doInsert unique removalCompare s k none).stored = 0 := by
  have h := removal_ready s unique [k] k (by simp) (by simp) ready
  rw [h.1]
  simp [LiveCount.count, LiveCount.tally, removal_lookup]

end InvalidPublication
