import Histories
namespace MapComposition

private def never : Option Nat → Option Nat → Bool := fun _ _ => false

def seed : List (LiveCount.Op Nat Nat) :=
  (List.range 9).map (fun k => ⟨k, some (k + 10), true⟩)

def removed : LiveCount.Store Nat Nat :=
  LiveCount.run never LiveCount.initial (seed ++ [⟨0, none, false⟩])

def restored : LiveCount.Store Nat Nat :=
  LiveCount.run never LiveCount.initial (seed ++ [⟨0, none, false⟩, ⟨0, some 99, false⟩])

theorem reachable_removal : removed.stored = 8 ∧ removed.chain.length = 2 ∧
    LiveCount.owner removed.chain 0 = some none := by decide

theorem reachable_resurrection : restored.stored = 9 ∧ restored.chain.length = 2 ∧
    LiveCount.owner restored.chain 0 = some (some 99) := by decide

theorem reachable_removed_index_complete :
    ∀ i < removed.stored, ∃ e, MapIterator.getIndex removed.chain removed.stored i = some e := by
  intro i hi
  exact history_index_in_bounds _ never i hi

theorem reachable_restored_index_complete :
    ∀ i < restored.stored, ∃ e, MapIterator.getIndex restored.chain restored.stored i = some e := by
  intro i hi
  exact history_index_in_bounds _ never i hi

def originalInsert (s : LiveCount.Store Nat Nat) (k : Nat) (v : Option Nat) : LiveCount.Store Nat Nat :=
  let fresh := (LiveCount.ownFind (s.chain.headD []) k).isNone
  let absentParent := (LiveCount.lookup s.chain.tail k).isNone
  ⟨LiveCount.insert s.chain k v, if fresh && absentParent then s.stored + 1 else s.stored⟩

def originalCow (unique : Bool) (s : LiveCount.Store Nat Nat) (k : Nat) (v : Option Nat) : LiveCount.Store Nat Nat :=
  if unique then originalInsert s k v
  else if LiveCount.lookup s.chain k == v then s
  else if LiveCount.shouldExpand s.chain then originalInsert ⟨[] :: s.chain, s.stored⟩ k v
  else originalInsert s k v

def originalRun (s : LiveCount.Store Nat Nat) : List (LiveCount.Op Nat Nat) → LiveCount.Store Nat Nat
  | [] => s
  | op :: rest => originalRun (originalCow op.unique s op.key op.value) rest

def oldRemoved : LiveCount.Store Nat Nat := originalRun LiveCount.initial
  (seed ++ [⟨0, none, true⟩])

def oldRestored : LiveCount.Store Nat Nat := originalRun LiveCount.initial
  (seed ++ [⟨0, none, true⟩, ⟨0, some 99, false⟩])

theorem original_removal_history : oldRemoved.stored = 9 ∧
    LiveCount.count (List.range 9) oldRemoved.chain = 8 ∧
    LiveCount.owner oldRemoved.chain 0 = some none := by decide

theorem original_resurrection_history : oldRestored.stored = 10 ∧
    LiveCount.count (List.range 9) oldRestored.chain = 9 ∧
    oldRestored.chain.length = 2 ∧ LiveCount.owner oldRestored.chain 0 = some (some 99) := by decide

theorem unsound_comparison_boundary :
    let ops : List (LiveCount.Op Nat Nat) := [⟨0,some 99,false⟩]
    let s := LiveCount.run (fun _ _ => true) LiveCount.initial ops
    s.stored = 0 ∧ LiveCount.lookup s.chain 0 = none ∧
      LiveCount.referenceRun (fun _ => none) ops 0 = some 99 := by decide

end MapComposition
