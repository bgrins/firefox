namespace SubstitutedInherit

structure State (Value Flags : Type) where
  value : Option Value
  resetDependency : Bool
  otherFlags : Flags

def resolve (fixed root inherits : Bool) (initial parent : Option V)
    (s : State V F) : State V F :=
  if root then { s with value := initial }
  else { s with value := parent,
                resetDependency := s.resetDependency || (fixed && !inherits) }

structure Observations where
  ordinaryChanged : Bool
  ordinaryInheritedEqual : Bool
  inheritedCustomEqual : Bool
  resetCustomEqual : Bool

structure Difference where
  changed : Bool
  resetOnly : Bool
  deriving DecidableEq, Repr

def difference (o : Observations) : Difference :=
  let changed := o.ordinaryChanged
  let resetOnly := o.ordinaryInheritedEqual
  if !o.inheritedCustomEqual then ⟨true, false⟩
  else if !o.resetCustomEqual then ⟨true, resetOnly⟩
  else ⟨changed, resetOnly⟩

structure Hint where
  unconditional : Bool
  conditionalReset : Bool
  deriving DecidableEq, Repr

def childrenHint (d : Difference) (otherForce resetForce : Bool) : Hint :=
  if !d.changed then ⟨otherForce, false⟩
  else if d.resetOnly then
    if resetForce then ⟨true, false⟩ else ⟨otherForce, true⟩
  else ⟨true, false⟩

def recascade (h : Hint) (s : State V F) : Bool :=
  h.unconditional || (h.conditionalReset && s.resetDependency)

def resetEventHint (changed : Bool) : Hint :=
  childrenHint (difference ⟨false, true, true, !changed⟩) false false

structure Event (Value : Type) where
  parent : Option Value
  changed : Bool

def refresh (fixed : Bool) (e : Event V) (s : State V F) : State V F :=
  if recascade (resetEventHint e.changed) s then
    resolve fixed false false none e.parent s
  else s

def EventReady (parent : Option V) (e : Event V) : Prop :=
  e.changed = false → e.parent = parent

def HistoryReady : Option V → List (Event V) → Prop
  | _, [] => True
  | parent, e :: es => EventReady parent e ∧ HistoryReady e.parent es

def run (fixed : Bool) : List (Event V) → State V F → State V F
  | [], s => s
  | e :: es, s => run fixed es (refresh fixed e s)

def expected : Option V → List (Event V) → Option V
  | parent, [] => parent
  | _, e :: es => expected e.parent es

def witness : State Nat Nat := ⟨some 10, false, 73⟩
def absent : State Nat Nat := ⟨none, false, 73⟩
def events : List (Event Nat) := [⟨some 20, true⟩, ⟨none, true⟩]

theorem selected_value (fixed root inherits : Bool) (initial parent : Option V)
    (s : State V F) :
    (resolve fixed root inherits initial parent s).value = if root then initial else parent := by
  cases root <;> rfl

theorem exact_dependency (fixed root inherits : Bool) (initial parent : Option V)
    (s : State V F) :
    (resolve fixed root inherits initial parent s).resetDependency =
      (s.resetDependency || (fixed && !root && !inherits)) := by
  cases root <;> cases fixed <;> cases inherits <;> simp [resolve]

theorem other_flags (fixed root inherits : Bool) (initial parent : Option V)
    (s : State V F) : (resolve fixed root inherits initial parent s).otherFlags = s.otherFlags := by
  cases root <;> rfl

theorem reset_only_provider (changed : Bool) :
    difference ⟨false, true, true, !changed⟩ = ⟨changed, true⟩ := by
  cases changed <;> rfl

theorem inherited_change_forces (o : Observations) (h : o.inheritedCustomEqual = false)
    (otherForce resetForce : Bool) :
    (childrenHint (difference o) otherForce resetForce).unconditional = true := by
  simp [difference, h, childrenHint]

theorem exact_conditional_consumption (changed : Bool) (s : State V F) :
    recascade (resetEventHint changed) s = (changed && s.resetDependency) := by
  cases changed <;> simp [resetEventHint, difference, childrenHint, recascade]

theorem corrected_publication (initial parent : Option V) (s : State V F) :
    (resolve true false false initial parent s).value = parent ∧
    (resolve true false false initial parent s).resetDependency = true ∧
    (resolve true false false initial parent s).otherFlags = s.otherFlags := by
  simp [resolve]

theorem refresh_correct (e : Event V) (s : State V F)
    (marked : s.resetDependency = true) (ready : EventReady s.value e) :
    (refresh true e s).value = e.parent ∧
    (refresh true e s).resetDependency = true ∧
    (refresh true e s).otherFlags = s.otherFlags := by
  cases changed : e.changed
  · have same := ready changed
    simp [refresh, exact_conditional_consumption, changed, marked, same]
  · simp [refresh, exact_conditional_consumption, changed, marked, resolve]

theorem history_correct (es : List (Event V)) (s : State V F)
    (marked : s.resetDependency = true) (ready : HistoryReady s.value es) :
    (run true es s).value = expected s.value es ∧
    (run true es s).resetDependency = true ∧
    (run true es s).otherFlags = s.otherFlags := by
  induction es generalizing s with
  | nil => simp [run, expected, marked]
  | cons e es ih =>
    rcases ready with ⟨now, later⟩
    rcases refresh_correct e s marked now with ⟨value, marker, flags⟩
    have remaining : HistoryReady (refresh true e s).value es := by simpa [value] using later
    rcases ih (refresh true e s) marker remaining with ⟨v, m, f⟩
    exact ⟨by simpa [run, expected, value] using v, m, f.trans flags⟩

theorem publication_history (initial parent : Option V) (s : State V F)
    (es : List (Event V)) (ready : HistoryReady parent es) :
    (run true es (resolve true false false initial parent s)).value = expected parent es ∧
    (run true es (resolve true false false initial parent s)).resetDependency = true ∧
    (run true es (resolve true false false initial parent s)).otherFlags = s.otherFlags := by
  rcases corrected_publication initial parent s with ⟨value, marker, flags⟩
  have ready' : HistoryReady (resolve true false false initial parent s).value es := by
    simpa [value] using ready
  rcases history_correct es (resolve true false false initial parent s) marker ready' with ⟨v, m, f⟩
  exact ⟨by simpa [value] using v, m, f.trans flags⟩

theorem original_missing_flag :
    let s := resolve false false false (some 1) (some 10) witness
    (refresh false ⟨some 20, true⟩ s).value = some 10 ∧
    (refresh true ⟨some 20, true⟩ (resolve true false false (some 1) (some 10) witness)).value = some 20 := by
  decide

theorem absent_parent_history :
    let s := resolve true false false (some 1) none absent
    s.resetDependency = true ∧ HistoryReady none events ∧
    (refresh true ⟨some 20, true⟩ s).value = some 20 ∧
    (run true events s).value = none := by
  simp [resolve, absent, events, HistoryReady, EventReady, refresh,
    exact_conditional_consumption, run]

theorem unchanged_event_requires_soundness :
    (refresh true ⟨some 20, false⟩ (resolve true false false (some 1) (some 10) witness)).value = some 10 := by
  decide

theorem root_and_inherited_no_extra_marker :
    (resolve true true false (some 1) (some 10) witness).value = some 1 ∧
    (resolve true true false (some 1) (some 10) witness).resetDependency = false ∧
    (resolve true false true (some 1) (some 10) witness).value = some 10 ∧
    (resolve true false true (some 1) (some 10) witness).resetDependency = false := by
  decide

end SubstitutedInherit
