import Invalidation
namespace TypeInvalidation

def fixture : Environment :=
  { owner := some 7, rootPresent := true, composedDocument := true, presContext := true
    subjects := [.root, .descendant 0, .pseudo 0]
    base := fun s => match s with | .root => 10 | .descendant _ => 17 | .pseudo _ => 23
    rules := [⟨.root, .activeType 0, 100⟩,
      ⟨.descendant 0, .activeType 0, 43⟩, ⟨.pseudo 0, .activeType 0, 71⟩] }

def freshState (e : Environment) (types : Nat → List Nat) : State :=
  let raw : State := ⟨types, fun _ => 0, false, 0, 0⟩
  { raw with cache := expected e raw }

theorem fresh_coherent (e : Environment) (types : Nat → List Nat) :
    Coherent e (freshState e types) := by
  intro _ subject _
  exact Or.inl rfl

def emptyState : State := freshState fixture (fun _ => [])
def alphaState : State := freshState fixture (fun _ => [0])
def addAlpha : State := mutate fixture emptyState 7 (.add 0) true
def deleteAlpha : State := mutate fixture alphaState 7 (.delete 0) true

def lostNotification (e : Environment) (s : State) (actor : Nat) (op : Edit) : State :=
  { mutate e s actor op true with pending := s.pending, requests := s.requests }

def missingAdd : State := lostNotification fixture emptyState 7 (.add 0)

theorem missing_notification_three_subjects :
    expected fixture missingAdd .root = 100 ∧ missingAdd.cache .root = 10 ∧
    expected fixture missingAdd (.descendant 0) = 43 ∧ missingAdd.cache (.descendant 0) = 17 ∧
    expected fixture missingAdd (.pseudo 0) = 71 ∧ missingAdd.cache (.pseudo 0) = 23 ∧
    missingAdd.pending = false := by decide +kernel

theorem missing_notification_incoherent : ¬Coherent fixture missingAdd := by
  intro h
  have bad := h (by decide) .root (by simp [fixture])
  have h1 : missingAdd.cache .root = 10 := by decide +kernel
  have h2 : expected fixture missingAdd .root = 100 := by decide +kernel
  have h3 : missingAdd.pending = false := by decide +kernel
  simp only [h1, h2, h3] at bad
  cases bad <;> contradiction

theorem direct_matching_changes_before_cache :
    evaluate true (activeTypes fixture addAlpha) (.activeType 0) = true ∧
    addAlpha.cache .root = 10 ∧ addAlpha.pending = true := by decide +kernel

theorem successful_subtree_delivery :
    (flush fixture addAlpha fixture.subjects).cache .root = 100 ∧
    (flush fixture addAlpha fixture.subjects).cache (.descendant 0) = 43 ∧
    (flush fixture addAlpha fixture.subjects).cache (.pseudo 0) = 71 ∧
    (flush fixture addAlpha fixture.subjects).pending = false := by decide +kernel

theorem root_only_delivery_retains_debt :
    (flush fixture addAlpha [.root]).cache .root = 100 ∧
    (flush fixture addAlpha [.root]).cache (.descendant 0) = 17 ∧
    (flush fixture addAlpha [.root]).cache (.pseudo 0) = 23 ∧
    (flush fixture addAlpha [.root]).pending = true := by decide +kernel

def dropPartial : State := { flush fixture addAlpha [.root] with pending := false }

theorem prematurely_cleared_partial_incoherent : ¬Coherent fixture dropPartial := by
  intro h
  have bad := h (by decide) (.descendant 0) (by simp [fixture])
  have h1 : dropPartial.cache (.descendant 0) = 17 := by decide +kernel
  have h2 : expected fixture dropPartial (.descendant 0) = 43 := by decide +kernel
  have h3 : dropPartial.pending = false := by decide +kernel
  simp only [h1, h2, h3] at bad
  cases bad <;> contradiction

def stateMatch (active : Bool) (types : List Nat) : Bool := active && types.contains 0

theorem fabricated_previous_state_loses_types :
    stateMatch true [0] = true ∧
    stateMatch (Bool.xor true true) [] = false ∧ stateMatch true [] = false := by decide +kernel

theorem deletion_needs_type_history_or_subtree_work :
    deleteAlpha.cache .root = 100 ∧ expected fixture deleteAlpha .root = 10 ∧
    stateMatch (Bool.xor true true) (activeTypes fixture deleteAlpha) =
      stateMatch true (activeTypes fixture deleteAlpha) ∧ deleteAlpha.pending = true := by decide +kernel

def addThenDelete : State := mutate fixture addAlpha 7 (.delete 0) true

def staleSnapshotFlush : State :=
  { addThenDelete with cache := expected fixture addAlpha, pending := false }

theorem stale_snapshot_flush_wrong :
    staleSnapshotFlush.cache .root = 100 ∧ expected fixture staleSnapshotFlush .root = 10 ∧
    staleSnapshotFlush.pending = false ∧
    (flush fixture addThenDelete fixture.subjects).cache .root = 10 := by decide +kernel

theorem requests_coalesce_pending_without_losing_latest :
    addThenDelete.requests = 2 ∧ addThenDelete.pending = true ∧
    (flush fixture addThenDelete fixture.subjects).pending = false ∧
    (flush fixture addThenDelete fixture.subjects).cache (.pseudo 0) = 23 := by decide +kernel

theorem noop_add_no_helper :
    (mutate fixture alphaState 7 (.add 0) true).helperCalls = 0 ∧
    (mutate fixture alphaState 7 (.add 0) true).requests = 0 := by decide +kernel

theorem noop_delete_no_helper :
    (mutate fixture emptyState 7 (.delete 0) true).helperCalls = 0 ∧
    (mutate fixture emptyState 7 (.delete 0) true).requests = 0 := by decide +kernel

theorem noop_clear_no_helper :
    (mutate fixture emptyState 7 .clear true).helperCalls = 0 ∧
    (mutate fixture emptyState 7 .clear true).requests = 0 := by decide +kernel

theorem errors_preserve_native (e : Environment) (s : State) (actor : Nat) (op : Edit) :
    (mutate e s actor op false).types = s.types ∧
    (mutate e s actor op false).pending = s.pending ∧
    (mutate e s actor op false).helperCalls = s.helperCalls ∧
    (mutate e s actor op false).requests = s.requests := by
  simp only [mutate, notified, helperCalled, failure_unchanged]
  simp
  funext id
  split <;> simp_all

theorem old_owner_changes_own_types_only :
    (mutate fixture emptyState 8 (.add 0) true).types 8 = [0] ∧
    (mutate fixture emptyState 8 (.add 0) true).types 7 = [] ∧
    (mutate fixture emptyState 8 (.add 0) true).helperCalls = 1 ∧
    (mutate fixture emptyState 8 (.add 0) true).requests = 0 ∧
    expected fixture (mutate fixture emptyState 8 (.add 0) true) .root = 10 := by decide +kernel

theorem root_absent_blocks_post :
    notified { fixture with rootPresent := false } emptyState 7 (.add 0) true = false := by decide +kernel

theorem composed_document_absent_blocks_post :
    notified { fixture with composedDocument := false } emptyState 7 (.add 0) true = false := by decide +kernel

theorem prescontext_absent_blocks_post :
    notified { fixture with presContext := false } emptyState 7 (.add 0) true = false := by decide +kernel

theorem boolean_rules_and_order :
    resolve true [0] .root 10
      [⟨.root, .both (.activeType 0) (.negated (.activeType 1)), 20⟩,
       ⟨.root, .either (.activeType 1) (.activeType 0), 30⟩] = 30 := by decide +kernel

end TypeInvalidation
