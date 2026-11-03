import Entry

namespace CancellationHandoff
open CancellationEntry CancellationRoute

structure Child where
  hasStyles : Bool
  ancestorFontHint : Bool
  deriving DecidableEq, Repr

structure Snapshot where
  gate : Gate
  selfHint : Bool
  descendantHint : Bool
  children : List Child
  deriving DecidableEq, Repr

def entryGate (s : Snapshot) : Gate :=
  { s.gate with localHint := s.gate.localHint || s.descendantHint }

def broad (signal : Bool) (s : Snapshot) : Snapshot :=
  if signal then { s with descendantHint := true } else s

def seed (child : Child) : Child :=
  if child.hasStyles then { child with ancestorFontHint := true } else child

def hasStyledChild (s : Snapshot) : Bool := s.children.any (·.hasStyles)

def selective (signal : Bool) (s : Snapshot) : Snapshot :=
  if signal && hasStyledChild s then
    { s with gate := { s.gate with normalDirty := true }, children := s.children.map seed }
  else s

theorem broad_supplies_entry (signal : Bool) (s : Snapshot) :
    SchedulingInvariant signal (entryGate (broad signal s)) := by
  intro work
  simp [broad, work, entryGate, normalEligible]

theorem selective_supplies_entry (signal : Bool) (s : Snapshot) :
    SchedulingInvariant (signal && hasStyledChild s) (entryGate (selective signal s)) := by
  intro work
  simp [selective, work, entryGate, normalEligible]

theorem broad_no_signal (s : Snapshot) : broad false s = s := rfl

theorem selective_no_signal (s : Snapshot) : selective false s = s := by
  simp [selective]

theorem selective_no_styled_child (signal : Bool) (s : Snapshot)
    (none : hasStyledChild s = false) : selective signal s = s := by
  simp [selective, none]

theorem styled_child_seeded (child : Child) (styled : child.hasStyles = true) :
    (seed child).ancestorFontHint = true := by
  simp [seed, styled]

theorem unstyled_child_unchanged (child : Child) (unstyled : child.hasStyles = false) :
    seed child = child := by
  simp [seed, unstyled]

theorem selective_children (signal : Bool) (s : Snapshot)
    (work : signal && hasStyledChild s = true) :
    (selective signal s).children = s.children.map seed := by
  simp [selective, work]

theorem broad_preserves_self_hint (signal : Bool) (s : Snapshot) :
    (broad signal s).selfHint = s.selfHint := by
  cases signal <;> rfl

theorem selective_preserves_self_hint (signal : Bool) (s : Snapshot) :
    (selective signal s).selfHint = s.selfHint := by
  simp [selective]
  split <;> rfl

theorem selective_preserves_root_hint (signal : Bool) (s : Snapshot) :
    (selective signal s).gate.localHint = s.gate.localHint ∧
    (selective signal s).descendantHint = s.descendantHint := by
  simp [selective]
  split <;> exact ⟨rfl, rfl⟩

theorem entry_is_not_visitation (g : Gate) (route : List Node) :
    (enter g route).visited = [] := by
  cases route <;> simp [enter, load]

theorem broad_with_forwarding_visits (s : Snapshot) (route : List Node) :
    run forwardAll route.length (enter (entryGate (broad true s)) route) = load [] route := by
  exact scheduled_entry_reaches_route true _ route rfl (broad_supplies_entry true s)

theorem selective_with_forwarding_visits (s : Snapshot) (route : List Node)
    (styled : hasStyledChild s = true) :
    run forwardAll route.length (enter (entryGate (selective true s)) route) = load [] route := by
  apply scheduled_entry_reaches_route (true && hasStyledChild s) _ route
  · simp [styled]
  · exact selective_supplies_entry true s

def observed : Snapshot := ⟨CancellationEntry.observed, false, false, [⟨true, false⟩]⟩
def noStyled : Snapshot := { observed with children := [⟨false, false⟩] }

end CancellationHandoff
