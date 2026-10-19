import Histories
import Observation
namespace TaintHistory
open TaintShortcut
variable {K P U : Type} [DecidableEq K]

theorem compare_sound (cmp : P → P → Bool) (sound : PayloadSound cmp) :
    LiveCount.CompareSound (metadataSame cmp) := by
  intro a b h
  exact metadata_same_sound cmp sound a b h

theorem lookup_reference (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (ops : List (LiveCount.Op K (Value P))) (initial : LiveCount.Store K (Value P)) (key : K) :
    LiveCount.lookup (LiveCount.run (metadataSame cmp) initial ops).chain key =
      LiveCount.referenceRun (LiveCount.lookup initial.chain) ops key :=
  LiveCount.history_lookup ops initial (metadataSame cmp) (compare_sound cmp sound) key

theorem lookup_url (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (ops : List (LiveCount.Op K (Value P))) (initial : LiveCount.Store K (Value P))
    (key : K) (parse : P → Option U) :
    observeURL parse (LiveCount.lookup (LiveCount.run (metadataSame cmp) initial ops).chain key) =
      observeURL parse (LiveCount.referenceRun (LiveCount.lookup initial.chain) ops key) := by
  rw [lookup_reference cmp sound]

theorem indexed_reference (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (ops : List (LiveCount.Op K (Value P))) (index : Nat) (key : K) (value : Value P)
    (returned : let s := LiveCount.run (metadataSame cmp) LiveCount.initial ops
      MapIterator.getIndex s.chain s.stored index = some (key,some value)) :
    LiveCount.referenceRun (fun _ => none) ops key = some value :=
  MapComposition.history_value_reference ops (metadataSame cmp) (compare_sound cmp sound)
    index key value returned

theorem indexed_url (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (ops : List (LiveCount.Op K (Value P))) (index : Nat) (key : K) (value : Value P)
    (returned : let s := LiveCount.run (metadataSame cmp) LiveCount.initial ops
      MapIterator.getIndex s.chain s.stored index = some (key,some value))
    (parse : P → Option U) :
    observeURL parse (LiveCount.referenceRun (fun _ => none) ops key) =
      (if value.attr then none else parse value.payload) := by
  rw [indexed_reference cmp sound ops index key value returned]
  rfl

theorem prefix_indexed_taint (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (ops : List (LiveCount.Op K (Value P))) (n index : Nat) (key : K) (value : Value P)
    (returned : let s := LiveCount.run (metadataSame cmp) LiveCount.initial (ops.take n)
      MapIterator.getIndex s.chain s.stored index = some (key,some value)) :
    (LiveCount.referenceRun (fun _ => none) (ops.take n) key).map Value.attr = some value.attr := by
  rw [indexed_reference cmp sound (ops.take n) index key value returned]
  rfl

theorem exact_count (cmp : P → P → Bool) (ops : List (LiveCount.Op K (Value P))) :
    let s := LiveCount.run (metadataSame cmp) LiveCount.initial ops
    s.stored = (MapIterator.live (MapIterator.drain (MapIterator.start s.chain))).length :=
  MapComposition.history_live_count ops (metadataSame cmp)

def exampleOps : List (LiveCount.Op Nat (Value Nat)) :=
  [⟨1,some ⟨7,false⟩,false⟩,⟨1,some ⟨7,true⟩,false⟩]

theorem old_count_can_still_be_correct :
    let s := LiveCount.run (payloadSame (fun a b : Nat => a == b)) LiveCount.initial exampleOps
    s.stored = 1 ∧ MapIterator.getIndex s.chain s.stored 0 = some (1,some ⟨7,false⟩) ∧
      LiveCount.referenceRun (fun _ => none) exampleOps 1 = some ⟨7,true⟩ := by
  simp only [MapIterator.getIndex, MapIterator.initialized_enumeration]
  decide

theorem metadata_history_carries_taint :
    let s := LiveCount.run (metadataSame (fun a b : Nat => a == b)) LiveCount.initial exampleOps
    s.stored = 1 ∧ MapIterator.getIndex s.chain s.stored 0 = some (1,some ⟨7,true⟩) := by
  simp only [MapIterator.getIndex, MapIterator.initialized_enumeration]
  decide
end TaintHistory
