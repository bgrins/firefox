import RepresentedCutoffs
import RegionDeletion

namespace ShadowOrder.ConsumerBridge

def rustKeep (key : Priority → Int) (prior : Option Priority) (next : Priority) :=
  if (prior.map (fun old => decide (key next < key old))).getD true
  then some next else prior

theorem rust_keep_matches (key : Priority → Int) (prior : Option Priority) (next : Priority) :
    rustKeep key prior next = retainMinimum key prior next := by
  cases prior with
  | none => rfl
  | some old => simp [rustKeep, retainMinimum]

theorem rust_keep_tie_preserves (key : Priority → Int) (old next : Priority)
    (tie : key next = key old) : rustKeep key (some old) next = some old := by
  simp [rustKeep, tie]

def rustAdd (s : RevertRepresentatives) (cut : Priority × RevertKind) :=
  match cut.2 with
  | .rule => s
  | .origin => {s with origin := rustKeep coreKey s.origin cut.1}
  | .layer => if cut.1.important && cut.1.layer == 65535 then
      {s with special := rustKeep normalKey s.special cut.1}
    else {s with layer := rustKeep normalKey s.layer cut.1}

theorem rust_add_matches (s : RevertRepresentatives) (cut : Priority × RevertKind) :
    rustAdd s cut = representativeAdd s cut := by
  cases cut with
  | mk p kind => cases kind <;>
    simp only [rustAdd, representativeAdd, specialCut, rust_keep_matches] <;> rfl

def empty : RevertRepresentatives := ⟨none, none, none⟩

structure Packed where
  slot : Option RevertRepresentatives
  fast : Bool
  deriving DecidableEq, Repr

def project (s : Packed) := s.slot.getD empty

abbrev WellFormed (s : Packed) : Prop :=
  s.fast = s.slot.isSome ∧ representativeValid (project s)

def packedAdd (s : Packed) (cut : Priority × RevertKind) : Packed :=
  match cut.2 with
  | .rule => s
  | _ => ⟨some (rustAdd (project s) cut), true⟩

theorem rule_preserves_all_storage (s : Packed) (p : Priority) :
    packedAdd s (p, .rule) = s := rfl

theorem packed_add_projects (s : Packed) (cut : Priority × RevertKind) :
    project (packedAdd s cut) = representativeAdd (project s) cut := by
  cases cut with
  | mk p kind => cases kind <;>
    simp [packedAdd, project, rust_add_matches, representativeAdd]

theorem packed_add_well_formed (s : Packed) (cut : Priority × RevertKind)
    (wf : WellFormed s) : WellFormed (packedAdd s cut) := by
  constructor
  · cases cut with
    | mk p kind => cases kind <;> simp [packedAdd, wf.1]
  · rw [packed_add_projects]
    exact representative_add_valid (project s) cut wf.2

def longhandAllows (s : Packed) (p : Priority) : Bool :=
  !(s.fast && (s.slot.map (fun state => !representativeAllows state p)).getD false)

def customAllows (s : Packed) (p : Priority) : Bool :=
  (s.slot.map (fun state => representativeAllows state p)).getD true

theorem custom_allows_projects (s : Packed) (p : Priority) :
    customAllows s p = representativeAllows (project s) p := by
  cases s with
  | mk slot fast => cases slot <;> simp [customAllows, project, empty, representativeAllows]

theorem longhand_allows_projects (s : Packed) (p : Priority) (wf : WellFormed s) :
    longhandAllows s p = representativeAllows (project s) p := by
  rw [longhandAllows, wf.1]
  cases slot : s.slot <;>
    simp [slot, project, empty, representativeAllows]

inductive Consumer where
  | longhand
  | custom

def gate (consumer : Consumer) (s : Packed) (included : Bool) (p : Priority) :=
  match consumer with
  | .longhand => included && longhandAllows s p
  | .custom => customAllows s p && included

theorem gates_agree (consumer : Consumer) (s : Packed) (included : Bool)
    (p : Priority) (wf : WellFormed s) :
    gate consumer s included p = (included && representativeAllows (project s) p) := by
  cases consumer <;> simp [gate, longhand_allows_projects s p wf,
    custom_allows_projects, Bool.and_comm]

def nativeControl (consumer : Consumer) (action : ε → RegionAction (Priority × RevertKind) α)
    (priority : ε → Priority) (included : ε → Bool) : List ε → Packed → Option α
  | [], _ => none
  | event :: rest, state =>
    if gate consumer state (included event) (priority event) then
      match action event with
      | .rollback cut => nativeControl consumer action priority included rest (packedAdd state cut)
      | .terminal value => some value
      | .skip => nativeControl consumer action priority included rest state
    else nativeControl consumer action priority included rest state

theorem rejected_declaration_is_inert (consumer : Consumer)
    (action : ε → RegionAction (Priority × RevertKind) α)
    (priority : ε → Priority) (included : ε → Bool) (event : ε) (rest : List ε)
    (state : Packed) (rejected : gate consumer state (included event) (priority event) = false) :
    nativeControl consumer action priority included (event :: rest) state =
      nativeControl consumer action priority included rest state := by
  simp [nativeControl, rejected]

abbrev ValidRepresentatives := {s : RevertRepresentatives // representativeValid s}

def validAdd (state : ValidRepresentatives) (cut : Priority × RevertKind) : ValidRepresentatives :=
  ⟨representativeAdd state.val cut, representative_add_valid state.val cut state.property⟩

def validAllowed (priority : ε → Priority) (included : ε → Bool)
    (state : ValidRepresentatives) (event : ε) :=
  included event && representativeAllows state.val (priority event)

theorem native_control_bridge (consumer : Consumer)
    (action : ε → RegionAction (Priority × RevertKind) α)
    (priority : ε → Priority) (included : ε → Bool) (events : List ε)
    (state : Packed) (wf : WellFormed state) :
    nativeControl consumer action priority included events state =
      summarizedControl action (validAllowed priority included) validAdd events ⟨project state, wf.2⟩ := by
  induction events generalizing state with
  | nil => rfl
  | cons event rest ih =>
    simp only [nativeControl, summarizedControl, validAllowed, gates_agree _ _ _ _ wf]
    by_cases accepted : (included event && representativeAllows (project state) (priority event)) = true
    · simp only [accepted, ↓reduceIte]
      cases action event with
      | terminal value => rfl
      | skip => exact ih state wf
      | rollback cut =>
        change nativeControl consumer action priority included rest (packedAdd state cut) =
          summarizedControl action (validAllowed priority included) validAdd rest
            (validAdd ⟨project state, wf.2⟩ cut)
        rw [ih (packedAdd state cut) (packed_add_well_formed state cut wf)]
        congr 1
        apply Subtype.ext
        exact packed_add_projects state cut
    · simpa [accepted] using ih state wf

theorem guarded_consumer_region_deletion (consumer : Consumer)
    (action : ε → RegionAction (Priority × RevertKind) α)
    (priority : ε → Priority) (included : ε → Bool) (events : List ε)
    (state : Packed) (wf : WellFormed state) :
    nativeControl consumer action priority included events state =
      regionReference action (fun cut event => repairedAllows cut.1 (priority event) cut.2)
        (events.filter (fun event => included event && representativeAllows (project state) (priority event))) := by
  rw [native_control_bridge consumer action priority included events state wf]
  apply arbitrary_region_deletion
  intro s cut event
  simp only [validAllowed, validAdd, representative_step_intersection _ _ _ s.property,
    Bool.and_assoc]

theorem fresh_consumers_region_deletion (consumer : Consumer)
    (action : ε → RegionAction (Priority × RevertKind) α)
    (priority : ε → Priority) (included : ε → Bool) (events : List ε) :
    nativeControl consumer action priority included events ⟨none, false⟩ =
      regionReference action (fun cut event => repairedAllows cut.1 (priority event) cut.2)
        (events.filter included) := by
  have wf : WellFormed ⟨none, false⟩ :=
    ⟨rfl, empty_representatives_valid⟩
  simpa [project, empty, representativeAllows] using
    guarded_consumer_region_deletion consumer action priority included events ⟨none, false⟩ wf

theorem rule_is_not_identity_deletion (p : Priority) :
    regionReference (fun first => if first then .rollback (p, RevertKind.rule) else .terminal 7)
      (fun cut (_ : Bool) => repairedAllows cut.1 p cut.2) [true, false] = some 7 ∧
    regionReference (fun first => if first then .rollback () else .terminal 7)
      (fun (_ : Unit) (_ : Bool) => false) [true, false] = none := by
  simp [regionReference, repairedAllows, nativeAllows]

theorem stale_fast_bit_changes_admission :
    let p : Priority := ⟨3, false, 0, 0, 0⟩
    let s : Packed := ⟨some ⟨some p, none, none⟩, false⟩
    longhandAllows s p = true ∧ customAllows s p = false := by
  decide

#print axioms rust_keep_matches
#print axioms rust_keep_tie_preserves
#print axioms packed_add_projects
#print axioms packed_add_well_formed
#print axioms rule_preserves_all_storage
#print axioms longhand_allows_projects
#print axioms gates_agree
#print axioms rejected_declaration_is_inert
#print axioms native_control_bridge
#print axioms guarded_consumer_region_deletion
#print axioms fresh_consumers_region_deletion
#print axioms rule_is_not_identity_deletion
#print axioms stale_fast_bit_changes_admission

end ShadowOrder.ConsumerBridge
