import IndexAllocation
namespace NativeAttributeReload
open QualifiedAttributes NativeAttributeIndices

inductive Value where
 | pending (payload : Nat)
 | resolved (payload : Nat)
 deriving DecidableEq

abbrev Slot := Option (Option Value)

def getAttr (slot : Slot) : Option Value := slot.join

def lazyOriginal (slot : Slot) (provider : Option Value) : Slot :=
 if (getAttr slot).isNone then
   match provider with | none => slot | some value => some (some value)
 else slot

def lazyAbsentOnly (slot : Slot) (provider : Option Value) : Slot :=
 if slot.isNone then
   match provider with | none => slot | some value => some (some value)
 else slot

theorem getter_conflates_absence_and_invalidity :
 getAttr none = getAttr (some none) := rfl

theorem corrected_loader_preserves_any_present_entry (value : Option Value) (provider : Option Value) :
 lazyAbsentOnly (some value) provider = some value := rfl

theorem corrected_loader_retries_absence (value : Value) :
 lazyAbsentOnly none (some value) = some (some value) := rfl

theorem failed_provider_does_not_create_tombstone : lazyAbsentOnly none none = none := rfl

theorem original_loader_resurrects_tombstone (payload : Nat) :
 lazyOriginal (some none) (some (.pending payload)) = some (some (.pending payload)) := rfl

structure StableState where
 slot : Slot
 finished : Bool

def terminal (slot : Slot) : Prop :=
 slot = some none ∨ ∃ payload, slot = some (some (.resolved payload))

def stable (state : StableState) : Prop := state.finished = true → terminal state.slot

def discover (state : StableState) (provider : Option Value) : StableState :=
 ⟨lazyAbsentOnly state.slot provider,state.finished⟩

def finish (result : Option Nat) : StableState :=
 ⟨some (result.map Value.resolved),true⟩

theorem corrected_loader_preserves_stable_finished_state (state : StableState)
 (valid : stable state) (provider : Option Value) : stable (discover state provider) := by
 intro finished
 have old := valid finished
 rcases old with invalid | ⟨payload,resolved⟩
 · exact Or.inl (by simp [discover,invalid,lazyAbsentOnly])
 · exact Or.inr ⟨payload,by simp [discover,resolved,lazyAbsentOnly]⟩

theorem completion_establishes_stability (result : Option Nat) : stable (finish result) := by
 intro _
 cases result with
 | none => exact Or.inl rfl
 | some payload => exact Or.inr ⟨payload,rfl⟩

inductive Operation where
 | discover (provider : Option Value)
 | complete (result : Option Nat)
 | reset

def step (state : StableState) : Operation → StableState
 | .discover provider => discover state provider
 | .complete result => finish result
 | .reset => ⟨state.slot,false⟩

def execute (operations : List Operation) (state : StableState) := operations.foldl step state

theorem arbitrary_completed_visit_history_stable (operations : List Operation)
 (state : StableState) (valid : stable state) : stable (execute operations state) := by
 induction operations generalizing state with
 | nil => exact valid
 | cons operation rest ih =>
   apply ih
   cases operation with
   | discover provider => exact corrected_loader_preserves_stable_finished_state state valid provider
   | complete result => exact completion_establishes_stability result
   | reset => intro impossible; contradiction

theorem original_loader_violates_stability (payload : Nat) :
 stable ⟨some none,true⟩ ∧
 ¬ stable ⟨lazyOriginal (some none) (some (.pending payload)),true⟩ := by
 constructor
 · intro _; exact Or.inl rfl
 · intro valid
   have outcome := valid rfl
   rcases outcome with invalid | ⟨value,resolved⟩
   · simp [lazyOriginal,getAttr] at invalid
   · simp [lazyOriginal,getAttr] at resolved

def traversePrelude (state : NativeAttributeIndices.State) (slot : Slot) (node : Node) :
 NativeAttributeIndices.State × Option Nat :=
 match getAttr slot with
 | none => (state,none)
 | some (.resolved _) => (state,none)
 | some (.pending _) => let next := enter state node; (next.1,some next.2)

theorem resurrected_pending_value_reuses_finished_index
 (state : NativeAttributeIndices.State) (node : Node) (index payload : Nat)
 (occupied : lookup state.maps node = some index) :
 traversePrelude state (lazyOriginal (some none) (some (.pending payload))) node = (state,some index) := by
 simp [traversePrelude,lazyOriginal,getAttr,enter,occupied]

theorem retained_tombstone_bypasses_old_index
 (state : NativeAttributeIndices.State) (node : Node) (provider : Option Value) :
 traversePrelude state (lazyAbsentOnly (some none) provider) node = (state,none) := rfl

theorem entered_then_popped_index_remains_occupied (node : Node) :
 let after := finishTop (enter initial node).1
 lookup after.maps node = some 0 ∧ after.infos = [none] ∧ coherent after := by
 dsimp only
 have noEntry : lookup emptyMaps node = none := by cases node <;> rfl
 constructor
 · simp [finishTop,enter,noEntry,initial,index_bucket_insert_is_tagged_write]
 constructor
 · simp [finishTop,enter,noEntry,initial]
 · exact finish_preserves_coherence _ (enter_preserves_coherence initial initial_coherent node)

end NativeAttributeReload
