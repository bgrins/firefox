import Deletion

namespace Destruction

def detached (h : Heap) (frame content : Address) (bit : Bool) : Heap :=
  write h frame (some (.frame content bit emptyTable))

theorem detach_primary (h : Heap) (frame content : Address) (bit : Bool)
    (props : PropertyTable) (present : h frame = some (.frame content bit props)) :
    primary (detached h frame content bit) = primary h := by
  funext x
  by_cases same : x = frame
  · subst x; simp [primary, detached, write, present]
  · simp [primary, detached, write, same]

theorem detach_coherent (h : Heap) (frame content : Address) (bit : Bool)
    (props : PropertyTable) (present : h frame = some (.frame content bit props))
    (coherent : Coherent h) : Coherent (detached h frame content bit) := by
  intro f c b ps atF
  rw [detach_primary h frame content bit props present]
  by_cases same : f = frame
  · subst f
    simp [detached, write] at atF
    rw [← atF.1, ← atF.2.1]
    exact coherent frame content bit props present
  · apply coherent f c b ps
    simpa [detached, write, same] using atF

def removeAll (h : Heap) (frame : Address) : Option Heap :=
  match h frame with
  | some (.frame content bit props) =>
      let cleared := detached h frame content bit
      (tablePlan props).bind (fun addresses => freeMany cleared addresses)
  | _ => none

theorem phase_execution (h next : Heap) (frame content : Address) (bit : Bool)
    (props : PropertyTable) (present : h frame = some (.frame content bit props))
    (success : removeAll h frame = some next) :
    ∃ addresses, tablePlan props = some addresses ∧
      freeMany (detached h frame content bit) addresses = some next := by
  cases planned : tablePlan props with
  | none => simp [removeAll, present, planned] at success
  | some addresses =>
      exact ⟨addresses, rfl, by simpa [removeAll, present, planned] using success⟩

theorem content_cell_survives (h next : Heap) (frame content : Address) (bit : Bool)
    (props : PropertyTable) (pointer : Option Address)
    (present : h frame = some (.frame content bit props))
    (ownerLive : h content = some (.content pointer))
    (success : removeAll h frame = some next) :
    next content = some (.content pointer) := by
  obtain ⟨addresses, _, execution⟩ := phase_execution h next frame content bit props present success
  have different : content ≠ frame := by
    intro same
    subst content
    rw [present] at ownerLive
    cases ownerLive
  exact protected_cell _ next addresses content (.content pointer)
    (by simpa [detached, write, different] using ownerLive) rfl execution

theorem allocation_survives_detach (h : Heap) (frame content : Address) (bit : Bool)
    (props : PropertyTable) (present : h frame = some (.frame content bit props))
    (a : Release) (allocated : Allocation h a) :
    Allocation (detached h frame content bit) a := by
  have different : a.address ≠ frame := by
    intro same
    have atA := allocated
    unfold Allocation at atA
    rw [same, present] at atA
    cases atA
  simpa [Allocation, detached, write, different] using allocated

theorem phase_complete (h : Heap) (frame content : Address) (bit : Bool)
    (props : PropertyTable) (addresses : List Release)
    (present : h frame = some (.frame content bit props))
    (planned : tablePlan props = some addresses)
    (unique : (addresses.map Release.address).Nodup) (ready : Allocated h addresses) :
    removeAll h frame = some (referenceErase (detached h frame content bit) addresses) := by
  have after : Allocated (detached h frame content bit) addresses := by
    intro a member
    exact allocation_survives_detach h frame content bit props present a (ready a member)
  simpa [removeAll, present, planned] using
    freeMany_complete (detached h frame content bit) addresses unique after

theorem phase_contract (h next : Heap) (frame : Address)
    (coherent : Coherent h) (success : removeAll h frame = some next) :
    Coherent next ∧ ∃ content bit props addresses,
      h frame = some (.frame content bit props) ∧
      tablePlan props = some addresses ∧
      next frame = some (.frame content bit emptyTable) ∧
      primary next = primary h ∧
      (∀ a ∈ addresses, next a.address = none) := by
  cases atFrame : h frame with
  | none => simp [removeAll, atFrame] at success
  | some cell =>
      cases cell with
      | allocation kind => simp [removeAll, atFrame] at success
      | content pointer => simp [removeAll, atFrame] at success
      | frame content bit props =>
          cases planned : tablePlan props with
          | none => simp [removeAll, atFrame, planned] at success
          | some addresses =>
              have execution : freeMany (detached h frame content bit) addresses = some next := by
                simpa [removeAll, atFrame, planned] using success
              have live : next frame = some (.frame content bit emptyTable) :=
                protected_cell (detached h frame content bit) next addresses frame
                  (.frame content bit emptyTable) (by simp [detached, write]) rfl execution
              exact ⟨coherent_after_free _ _ _
                (detach_coherent h frame content bit props atFrame coherent) execution,
                content, bit, props, addresses, rfl, planned, live,
                (primary_preserved _ _ _ execution).trans
                  (detach_primary h frame content bit props atFrame),
                fun a member => freed_allocation _ _ _ a member execution⟩

def bitRead (h : Heap) (frame : Address) : Option Bool :=
  match h frame with
  | some (.frame _ bit _) => some bit
  | _ => none

def pointerRead (h : Heap) (frame : Address) : Option Bool :=
  match h frame with
  | some (.frame content _ _) => some (decide (primary h content = some frame))
  | _ => none

theorem read_agrees (h : Heap) (coherent : Coherent h) (frame : Address) :
    bitRead h frame = pointerRead h frame := by
  cases atFrame : h frame with
  | none => simp [bitRead, pointerRead, atFrame]
  | some cell =>
      cases cell with
      | allocation kind => simp [bitRead, pointerRead, atFrame]
      | content pointer => simp [bitRead, pointerRead, atFrame]
      | frame content bit props =>
          simp [bitRead, pointerRead, atFrame, coherent frame content bit props atFrame]

theorem projected_read_after_phase_agrees (h next : Heap) (frame : Address)
    (coherent : Coherent h) (success : removeAll h frame = some next) :
    bitRead next frame = pointerRead next frame :=
  read_agrees next (phase_contract h next frame coherent success).1 frame

theorem immediate_repeat_empty (h next : Heap) (frame : Address)
    (coherent : Coherent h) (success : removeAll h frame = some next) :
    removeAll next frame = some next := by
  obtain ⟨_, content, bit, props, addresses, _, _, live, _, _⟩ :=
    phase_contract h next frame coherent success
  have unchanged : detached next frame content bit = next := by
    funext x
    by_cases same : x = frame
    · subst x; simp [detached, write, live]
    · simp [detached, write, same]
  simp [removeAll, live, tablePlan, emptyTable, plan, optional, freeMany, unchanged]

theorem shared_raw_pointer_irrelevant (root : Address) (buffer : Option Address)
    (lines : List LinePayload) (replace : List Address → List Address) :
    footprint (.shared root buffer (lines.map (fun line => { line with frames := replace line.frames }))) =
      footprint (.shared root buffer lines) := by
  simp [footprint, List.flatMap_map]

theorem shared_root_in_footprint (root : Address) (buffer : Option Address)
    (lines : List LinePayload) :
    ∃ addresses, footprint (.shared root buffer lines) = some addresses ∧ ⟨root, .shared⟩ ∈ addresses := by
  exact ⟨_, rfl, by simp⟩

theorem no_foreign_admission (root : Address) (tail : List Property) :
    plan (.foreign root :: tail) = none := rfl

end Destruction
