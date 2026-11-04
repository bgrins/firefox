import RepresentedCutoffs
import RegionDeletion
namespace ShadowOrder

inductive StoredConstraint (κ : Type) where
 | rule (identity : κ)
 | priority (cut : Priority) (kind : RevertKind)

structure StoredControl (κ : Type) where
 priorities : RevertRepresentatives
 valid : representativeValid priorities
 excluded : List κ

def storedRegion [DecidableEq κ] (identity : ε → κ) (priority : ε → Priority)
 (constraint : StoredConstraint κ) (event : ε) : Bool :=
 match constraint with
 | .rule key => decide (identity event ≠ key)
 | .priority cut kind => repairedAllows cut (priority event) kind

def storedAllowed [DecidableEq κ] (identity : ε → κ) (priority : ε → Priority)
 (included : ε → Bool) (state : StoredControl κ) (event : ε) : Bool :=
 included event && representativeAllows state.priorities (priority event) &&
 decide (identity event ∉ state.excluded)

def storedAdd (state : StoredControl κ) (constraint : StoredConstraint κ) : StoredControl κ :=
 match constraint with
 | .rule key => {state with excluded := key::state.excluded}
 | .priority cut kind =>
   ⟨representativeAdd state.priorities (cut,kind),
     representative_add_valid state.priorities (cut,kind) state.valid,state.excluded⟩

theorem stored_control_intersection [DecidableEq κ] (identity : ε → κ)
 (priority : ε → Priority) (included : ε → Bool)
 (state : StoredControl κ) (constraint : StoredConstraint κ) (event : ε) :
 storedAllowed identity priority included (storedAdd state constraint) event =
 (storedAllowed identity priority included state event && storedRegion identity priority constraint event) := by
 cases constraint with
 | rule key =>
   simp [storedAllowed,storedAdd,storedRegion,List.mem_cons,
     Bool.and_assoc,Bool.and_left_comm,Bool.and_comm]
 | priority cut kind =>
   simp only [storedAllowed,storedAdd,storedRegion]
   rw [representative_step_intersection _ _ _ state.valid]
   by_cases member : identity event ∈ state.excluded <;>
     simp [member,Bool.and_left_comm,Bool.and_comm]

theorem stored_control_deletion [DecidableEq κ] (identity : ε → κ)
 (priority : ε → Priority) (included : ε → Bool)
 (action : ε → RegionAction (StoredConstraint κ) α)
 (events : List ε) (state : StoredControl κ) :
 summarizedControl action (storedAllowed identity priority included) storedAdd events state =
 regionReference action (storedRegion identity priority)
   (events.filter (storedAllowed identity priority included state)) :=
 arbitrary_region_deletion action _ _ _
   (stored_control_intersection identity priority included) events state

def emptyStoredControl : StoredControl κ :=
 ⟨⟨none,none,none⟩,empty_representatives_valid,[]⟩

theorem fresh_stored_control_deletion [DecidableEq κ] (identity : ε → κ)
 (priority : ε → Priority) (included : ε → Bool)
 (action : ε → RegionAction (StoredConstraint κ) α) (events : List ε) :
 summarizedControl action (storedAllowed identity priority included) storedAdd events emptyStoredControl =
 regionReference action (storedRegion identity priority) (events.filter included) := by
 have result := stored_control_deletion identity priority included action events emptyStoredControl
 have initial : storedAllowed identity priority included emptyStoredControl = included := by
   funext event
   simp [storedAllowed,emptyStoredControl,representativeAllows]
 rw [initial] at result
 exact result

#print axioms fresh_stored_control_deletion
end ShadowOrder
