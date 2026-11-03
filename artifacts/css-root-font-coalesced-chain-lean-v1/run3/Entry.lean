import Route

namespace CancellationEntry
open CancellationRoute

structure Gate where
  hasStyles : Bool
  normalDirty : Bool
  localHint : Bool
  animationDirty : Bool
  deriving DecidableEq, Repr

def normalEligible (g : Gate) : Bool :=
  !g.hasStyles || g.normalDirty || g.localHint

def enter (g : Gate) (route : List Node) : State :=
  if normalEligible g then load route [] else ⟨none, route, []⟩

def animationVisit (g : Gate) : Gate := { g with animationDirty := true }

def reserveNormal (retained : Bool) (g : Gate) : Gate :=
  if retained then { g with normalDirty := true } else g

def SchedulingInvariant (retained : Bool) (g : Gate) : Prop :=
  retained = true → normalEligible g = true

theorem animation_visit_preserves_normal_gate (g : Gate) :
    normalEligible (animationVisit g) = normalEligible g := rfl

theorem denied_entry_visits_nothing (g : Gate) (route : List Node) (n : Nat)
    (denied : normalEligible g = false) :
    (run forwardAll n (enter g route)).visited = [] := by
  simp only [enter, denied, Bool.false_eq_true, ↓reduceIte]
  rw [no_scheduled_work_no_visitation]

theorem reserved_work_has_entry (retained : Bool) (g : Gate) :
    SchedulingInvariant retained (reserveNormal retained g) := by
  intro h
  simp [reserveNormal, h, normalEligible]

theorem no_work_does_not_add_dirtiness (g : Gate) :
    reserveNormal false g = g := rfl

theorem scheduled_entry_reaches_route (retained : Bool) (g : Gate)
    (route : List Node) (work : retained = true)
    (scheduled : SchedulingInvariant retained g) :
    run forwardAll route.length (enter g route) = load [] route := by
  have admitted := scheduled work
  simp only [enter, admitted, ↓reduceIte]
  simpa using scheduled_route_visits_in_order route []

def observed : Gate := ⟨true, false, false, true⟩

theorem retained_descendant_counterexample :
    observed.animationDirty = true ∧ normalEligible observed = false ∧
    (run forwardAll deepRoute.length (enter observed deepRoute)).visited = [] := by
  decide +kernel

theorem reserved_route_control :
    (run forwardAll deepRoute.length
      (enter (reserveNormal true observed) deepRoute)).visited = deepRoute := by
  decide +kernel

end CancellationEntry
