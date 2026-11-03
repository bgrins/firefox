import Handoff

namespace SelectiveRouteAdmission

open CancellationRoute CancellationEntry CancellationHandoff

theorem eligible_route_visits (forward : Node → Bool) (route prior : List Node)
    (eligible : ∀ node ∈ route, forward node = true) :
    run forward route.length (load route prior) = load [] (prior ++ route) := by
  induction route generalizing prior with
  | nil => simp [run, load]
  | cons node rest ih =>
    have remaining : ∀ next ∈ rest, forward next = true := by
      intro next member
      exact eligible next (List.mem_cons_of_mem node member)
    have handoff : step forward (load (node :: rest) prior) = load rest (prior ++ [node]) := by
      cases rest with
      | nil => rfl
      | cons next tail =>
        have enabled := remaining next (by simp)
        simp [step, load, enabled]
    simp only [List.length_cons, run, handoff]
    rw [ih _ remaining]
    simp [List.append_assoc]

def normalForward (styled hidden : Nat → Bool) (node : Node) : Bool :=
  styled node.id && !hidden node.id

theorem stable_route_eligible (styled hidden : Nat → Bool) (route : List Node)
    (stable : ∀ node ∈ route, styled node.id = true ∧ hidden node.id = false) :
    ∀ node ∈ route, normalForward styled hidden node = true := by
  intro node member
  obtain ⟨styles, visible⟩ := stable node member
  simp [normalForward, styles, visible]

theorem selective_route_and_consumer (snapshot : Snapshot) (route : List Node)
    (styled hidden : Nat → Bool) (hasChild : hasStyledChild snapshot = true)
    (stable : ∀ node ∈ route, styled node.id = true ∧ hidden node.id = false)
    (ownerOf : Nat → Nat) (events : List FontUnitAdmission.Event)
    (id : Nat) (entry : AttributeWatches.Entry) (retainedFlag : Bool)
    (target : Node) (inRoute : target ∈ route) (sameTarget : target.id = entry.target)
    (member : (id, entry) ∈ (FontUnitAdmission.run ownerOf events).registry.active) :
    target ∈ (run (normalForward styled hidden) route.length
      (enter (entryGate (selective true snapshot)) route)).visited ∧
    FontUnitAdmission.admits ownerOf true true retainedFlag
      (FontUnitAdmission.run ownerOf events) target.id = true := by
  have admitted : normalEligible (entryGate (selective true snapshot)) = true := by
    apply selective_supplies_entry true snapshot
    simp [hasChild]
  constructor
  · simp only [enter, admitted, ↓reduceIte]
    rw [eligible_route_visits _ _ [] (stable_route_eligible styled hidden route stable)]
    simpa [load] using inRoute
  · rw [sameTarget]
    exact FontUnitAdmission.registered_normal_hint_admitted ownerOf events id entry retainedFlag member

end SelectiveRouteAdmission
