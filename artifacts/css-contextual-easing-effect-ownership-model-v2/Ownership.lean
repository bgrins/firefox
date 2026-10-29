import Dependency

namespace EffectOwnershipV2
open ContextualEasing

structure Selection where
  ruleRoot : Nat
  ruleIdentity : Nat
  ruleVersion : Nat
  declaration : Nat
  parameters : List Expr

def computed (selection : Selection) (elementContext : Context) : List Nat :=
  evaluate selection.parameters elementContext

inductive Owner where
  | css | script
  deriving DecidableEq, Repr

structure Capture where
  association : Nat
  referenceRoot : Nat
  ruleRoot : Nat
  ruleIdentity : Nat
  ruleVersion : Nat
  declaration : Nat
  element : Nat
  values : List Nat
  deriving DecidableEq, Repr

structure State where
  association : Nat
  referenceRoot : Nat
  selection : Selection
  element : Nat
  elementContext : Context
  owner : Owner
  frames : List Nat
  transition : Option Capture

def capture (state : State) : Capture :=
  ⟨state.association, state.referenceRoot, state.selection.ruleRoot,
    state.selection.ruleIdentity, state.selection.ruleVersion,
    state.selection.declaration, state.element,
    computed state.selection state.elementContext⟩

inductive Event where
  | refresh (selection : Selection) (elementContext : Context)
  | setKeyframes (processed : Except Nat (List Nat))
  | startTransition

def step (state : State) : Event → State
  | .refresh selection elementContext =>
      { state with selection := selection, elementContext := elementContext, frames := if state.owner = .css then computed selection elementContext else state.frames }
  | .setKeyframes (.error _) => state
  | .setKeyframes (.ok frames) => { state with owner := .script, frames := frames }
  | .startTransition => { state with transition := some (capture state) }

def run (state : State) (events : List Event) : State := events.foldl step state

def NoSuccessfulOverride : Event → Prop
  | .setKeyframes (.ok _) => False
  | _ => True

theorem script_step_preserves (state : State) (event : Event)
    (owned : state.owner = .script) (allowed : NoSuccessfulOverride event) :
    (step state event).owner = .script ∧ (step state event).frames = state.frames := by
  cases event with
  | refresh selection elementContext => simp [step, owned]
  | startTransition => exact ⟨owned, rfl⟩
  | setKeyframes processed =>
      cases processed with
      | error error => exact ⟨owned, rfl⟩
      | ok frames => exact False.elim allowed

theorem script_trace_preserves (state : State) (events : List Event)
    (owned : state.owner = .script)
    (allowed : ∀ event ∈ events, NoSuccessfulOverride event) :
    (run state events).owner = .script ∧ (run state events).frames = state.frames := by
  induction events generalizing state with
  | nil => exact ⟨owned, rfl⟩
  | cons event rest ih =>
      have first := script_step_preserves state event owned (allowed event (by simp))
      have tail := ih (step state event) first.1 (fun e he => allowed e (by simp [he]))
      exact ⟨tail.1, tail.2.trans first.2⟩

theorem successful_override_shields (state : State) (frames : List Nat) (events : List Event)
    (allowed : ∀ event ∈ events, NoSuccessfulOverride event) :
    (run (step state (.setKeyframes (.ok frames))) events).owner = .script ∧
    (run (step state (.setKeyframes (.ok frames))) events).frames = frames := by
  exact script_trace_preserves _ events rfl allowed

theorem rejected_call_erases_from_trace (state : State) (front suffix : List Event)
    (error : Nat) :
    run state (front ++ .setKeyframes (.error error) :: suffix) =
      run state (front ++ suffix) := by
  simp [run, List.foldl_append, step]

theorem css_refresh_uses_element_context (state : State) (selection : Selection)
    (elementContext : Context) (owned : state.owner = .css) :
    (step state (.refresh selection elementContext)).frames =
      evaluate selection.parameters elementContext := by
  simp [step, owned, computed]

theorem new_transition_uses_css_selection (state : State) :
    (step state .startTransition).transition = some (capture state) := rfl

theorem selected_parameters_locality (left right : Selection) (before after : Context)
    (sameParameters : left.parameters = right.parameters)
    (agree : Agree (support left.parameters) before after) :
    computed left before = computed right after := by
  unfold computed
  rw [← sameParameters]
  exact parameters_locality left.parameters before after agree

def targetContext : Context
  | .ownFont => 16
  | .parentFont => 16
  | .siblingIndex => 2
  | .siblingCount => 4

def firstSelection : Selection :=
  ⟨7, 100, 1, 10, [.divConst (.read .ownFont) 8]⟩

def nextSelection : Selection :=
  ⟨7, 100, 2, 11, [.add (.literal 1) (.divConst (.read .ownFont) 8)]⟩

def initial : State := ⟨50, 7, firstSelection, 42, targetContext, .css, [2], none⟩

def outerSelection : Selection := { nextSelection with ruleRoot := 9, ruleIdentity := 101, ruleVersion := 1 }

def outerInitial : State := ⟨51, 9, outerSelection, 42, targetContext, .css, [3], none⟩

theorem independent_reference_root_witness :
    initial.element = outerInitial.element ∧
    initial.elementContext = outerInitial.elementContext ∧
    initial.referenceRoot ≠ outerInitial.referenceRoot ∧
    initial.association ≠ outerInitial.association ∧
    initial.owner = .css ∧ outerInitial.owner = .css ∧
    computed initial.selection initial.elementContext = [2] ∧
    computed outerInitial.selection outerInitial.elementContext = [3] := by
  constructor
  · rfl
  constructor
  · rfl
  decide

theorem rejected_then_refresh_remains_css :
    let result := run initial [.setKeyframes (.error 2), .refresh nextSelection targetContext]
    result.owner = .css ∧ result.frames = [3] := by decide

theorem independent_consumer_witness :
    let overridden := step initial (.setKeyframes (.ok [5]))
    let started := step overridden .startTransition
    let changed := step started (.refresh nextSelection targetContext)
    let restored := step changed (.refresh firstSelection targetContext)
    changed.frames = [5] ∧ changed.element = 42 ∧
    changed.association = initial.association ∧ changed.referenceRoot = initial.referenceRoot ∧
    computed changed.selection changed.elementContext = [3] ∧
    changed.transition = some ⟨50, 7, 7, 100, 1, 10, 42, [2]⟩ ∧
    (step changed .startTransition).transition = some ⟨50, 7, 7, 100, 2, 11, 42, [3]⟩ ∧
    computed restored.selection restored.elementContext = [2] := by decide

end EffectOwnershipV2
