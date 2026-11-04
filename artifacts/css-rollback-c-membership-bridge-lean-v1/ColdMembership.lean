import ConsumerBridge
import RepresentedControl

namespace ShadowOrder.ColdMembership
open ConsumerBridge

abbrev Key (β : Type) := Priority × β

structure State (β : Type) where
  storage : Packed
  excluded : List (Key β)

abbrev WellFormed (s : State β) : Prop :=
  s.storage.fast = (s.storage.slot.isSome || !s.excluded.isEmpty) ∧
  representativeValid (project s.storage)

def initial : State β := ⟨⟨none, false⟩, []⟩

theorem initial_well_formed : WellFormed (initial : State β) :=
  ⟨rfl, empty_representatives_valid⟩

def add (s : State β) (constraint : StoredConstraint (Key β)) : State β :=
  match constraint with
  | .rule key => ⟨{s.storage with fast := true}, key :: s.excluded⟩
  | .priority _ .rule => s
  | .priority p kind =>
      ⟨⟨some (rustAdd (project s.storage) (p, kind)), true⟩, s.excluded⟩

theorem add_well_formed (s : State β) (constraint : StoredConstraint (Key β))
    (wf : WellFormed s) : WellFormed (add s constraint) := by
  cases constraint with
  | rule key => exact ⟨by simp [add], wf.2⟩
  | priority p kind =>
    cases kind with
    | rule => exact wf
    | origin =>
      constructor
      · simp [add]
      · simpa [add, project, rust_add_matches] using
          representative_add_valid (project s.storage) (p, .origin) wf.2
    | layer =>
      constructor
      · simp [add]
      · simpa [add, project, rust_add_matches] using
          representative_add_valid (project s.storage) (p, .layer) wf.2

theorem guarded_fold_well_formed (events : List ε)
    (admitted : State β → ε → Bool) (constraint : ε → StoredConstraint (Key β))
    (s : State β) (wf : WellFormed s) :
    WellFormed (events.foldl (fun state event =>
      if admitted state event then add state (constraint event) else state) s) := by
  induction events generalizing s with
  | nil => exact wf
  | cons event rest ih =>
    simp only [List.foldl_cons]
    split
    · exact ih _ (add_well_formed s (constraint event) wf)
    · exact ih _ wf

def toStored (s : State β) (wf : WellFormed s) : StoredControl (Key β) :=
  ⟨project s.storage, wf.2, s.excluded⟩

theorem add_matches_stored (s : State β) (constraint : StoredConstraint (Key β))
    (wf : WellFormed s) :
    toStored (add s constraint) (add_well_formed s constraint wf) =
      storedAdd (toStored s wf) constraint := by
  cases constraint with
  | rule key => rfl
  | priority p kind => cases kind <;>
      simp [toStored, add, storedAdd, project, rust_add_matches, representativeAdd]

def coldMatch [DecidableEq β] (contains : β → δ → Bool)
    (excluded : List (Key β)) (p : Priority) (declaration : δ) : Bool :=
  excluded.any (fun key => decide (key.1 = unimportantPriority p) && contains key.2 declaration)

def identity (owner : δ → β) (p : Priority) (declaration : δ) : Key β :=
  (unimportantPriority p, owner declaration)

theorem cold_match_exact [DecidableEq β] (contains : β → δ → Bool) (owner : δ → β)
    (membership : ∀ block declaration, contains block declaration = decide (owner declaration = block))
    (excluded : List (Key β)) (p : Priority) (declaration : δ) :
    coldMatch contains excluded p declaration = decide (identity owner p declaration ∈ excluded) := by
  induction excluded with
  | nil => rfl
  | cons key rest ih =>
    simp only [coldMatch, List.any_cons] at ih ⊢
    rw [ih]
    simp [membership, identity, Prod.ext_iff, eq_comm, Bool.and_comm]
    rfl

def coldAllows [DecidableEq β] (contains : β → δ → Bool)
    (s : State β) (p : Priority) (declaration : δ) : Bool :=
  !(s.storage.fast &&
    (!customAllows s.storage p || coldMatch contains s.excluded p declaration))

theorem fast_gate_projects [DecidableEq β] (contains : β → δ → Bool)
    (s : State β) (p : Priority) (declaration : δ) (wf : WellFormed s) :
    coldAllows contains s p declaration =
      (representativeAllows (project s.storage) p && !coldMatch contains s.excluded p declaration) := by
  rw [coldAllows, wf.1, custom_allows_projects]
  cases slot : s.storage.slot <;> cases s.excluded <;>
    simp [slot, project, empty, representativeAllows, coldMatch]

def allowed [DecidableEq β] (contains : β → δ → Bool)
    (priority : ε → Priority) (declaration : ε → δ) (included : ε → Bool)
    (s : State β) (event : ε) :=
  included event && coldAllows contains s (priority event) (declaration event)

theorem longhand_gate_matches_stored [DecidableEq β]
    (contains : β → δ → Bool) (owner : δ → β)
    (membership : ∀ block declaration, contains block declaration = decide (owner declaration = block))
    (priority : ε → Priority) (declaration : ε → δ) (included : ε → Bool)
    (s : State β) (event : ε) (wf : WellFormed s) :
    allowed contains priority declaration included s event =
      storedAllowed (fun e => identity owner (priority e) (declaration e)) priority included
        (toStored s wf) event := by
  simp only [allowed, fast_gate_projects _ _ _ _ wf,
    cold_match_exact contains owner membership, storedAllowed, toStored]
  by_cases member : identity owner (priority event) (declaration event) ∈ s.excluded <;>
    simp [member]

theorem first_rule_without_cutoff (key : Key β) :
    (add initial (.rule key)).storage.fast = true ∧
    (add initial (.rule key)).storage.slot = none ∧
    (add initial (.rule key)).excluded = [key] ∧
    WellFormed (add initial (.rule key)) :=
  ⟨rfl, rfl, rfl, add_well_formed initial (.rule key) initial_well_formed⟩

theorem later_priority_preserves_rule (key : Key β) (p : Priority) (kind : RevertKind) :
    (add (add initial (.rule key)) (.priority p kind)).excluded = [key] ∧
    WellFormed (add (add initial (.rule key)) (.priority p kind)) := by
  constructor
  · cases kind <;> rfl
  · exact add_well_formed _ _ (add_well_formed initial (.rule key) initial_well_formed)

theorem full_priority_equality_retains_flags (p : Priority) (flags : Nat)
    (different : flags ≠ p.flags) :
    unimportantPriority {p with flags := flags} ≠ unimportantPriority p := by
  intro equal
  exact different (congrArg Priority.flags equal)

theorem rule_layer_origin_sequence (key : Key β) (layer origin : Priority) :
    let s := add (add (add initial (.rule key)) (.priority layer .layer)) (.priority origin .origin)
    s.storage.fast = true ∧ s.storage.slot.isSome = true ∧ s.excluded = [key] ∧ WellFormed s := by
  refine ⟨rfl, rfl, rfl, ?_⟩
  apply add_well_formed
  apply add_well_formed
  exact add_well_formed initial (.rule key) initial_well_formed

theorem identity_only_gate [DecidableEq β]
    (contains : β → δ → Bool) (owner : δ → β)
    (membership : ∀ block declaration, contains block declaration = decide (owner declaration = block))
    (key : Key β) (p : Priority) (declaration : δ) :
    coldAllows contains (add initial (.rule key)) p declaration =
      decide (identity owner p declaration ≠ key) := by
  rw [fast_gate_projects _ _ _ _ (add_well_formed initial (.rule key) initial_well_formed),
    cold_match_exact contains owner membership]
  simp [add, initial, project, empty, representativeAllows]

#print axioms initial_well_formed
#print axioms add_well_formed
#print axioms guarded_fold_well_formed
#print axioms add_matches_stored
#print axioms cold_match_exact
#print axioms fast_gate_projects
#print axioms longhand_gate_matches_stored
#print axioms first_rule_without_cutoff
#print axioms later_priority_preserves_rule
#print axioms full_priority_equality_retains_flags
#print axioms rule_layer_origin_sequence
#print axioms identity_only_gate

end ShadowOrder.ColdMembership
