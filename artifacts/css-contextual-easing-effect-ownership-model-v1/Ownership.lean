import Dependency

namespace EffectOwnership
open ContextualEasing

structure Selection where
  declaration : Nat
  root : Nat
  parameters : List Expr

abbrev Environment := Nat → Context

def computed (selection : Selection) (environment : Environment) : List Nat :=
  evaluate selection.parameters (environment selection.root)

inductive Owner where
  | css | script
  deriving DecidableEq, Repr

structure Capture where
  declaration : Nat
  root : Nat
  values : List Nat
  deriving DecidableEq, Repr

structure State where
  selection : Selection
  environment : Environment
  owner : Owner
  frames : List Nat
  transition : Option Capture

inductive Event where
  | refresh (selection : Selection) (environment : Environment)
  | setKeyframes (processed : Except Nat (List Nat))
  | startTransition

def step (state : State) : Event → State
  | .refresh selection environment =>
      { state with selection := selection, environment := environment, frames := if state.owner = .css then computed selection environment else state.frames }
  | .setKeyframes (.error _) => state
  | .setKeyframes (.ok frames) => { state with owner := .script, frames := frames }
  | .startTransition =>
      { state with transition := some ⟨state.selection.declaration, state.selection.root,
          computed state.selection state.environment⟩ }

def run (state : State) (events : List Event) : State := events.foldl step state

def NoSuccessfulOverride : Event → Prop
  | .setKeyframes (.ok _) => False
  | _ => True

theorem script_step_preserves (state : State) (event : Event)
    (owned : state.owner = .script) (allowed : NoSuccessfulOverride event) :
    (step state event).owner = .script ∧ (step state event).frames = state.frames := by
  cases event with
  | refresh selection environment => simp [step, owned]
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

theorem css_refresh_uses_selection (state : State) (selection : Selection)
    (environment : Environment) (owned : state.owner = .css) :
    (step state (.refresh selection environment)).frames =
      evaluate selection.parameters (environment selection.root) := by
  simp [step, owned, computed]

theorem new_transition_uses_css_selection (state : State) :
    (step state .startTransition).transition =
      some ⟨state.selection.declaration, state.selection.root,
        computed state.selection state.environment⟩ := rfl

def env : Environment := fun root field =>
  match field with
  | .siblingIndex => if root = 7 then 2 else 3
  | .ownFont => 16
  | .parentFont => 16
  | .siblingCount => 4

def firstSelection : Selection := ⟨10, 7, [.read .siblingIndex]⟩
def nextSelection : Selection := ⟨11, 9, [.add (.literal 1) (.read .siblingIndex)]⟩
def initial : State := ⟨firstSelection, env, .css, [2], none⟩

theorem rejected_then_refresh_remains_css :
    let result := run initial [.setKeyframes (.error 2), .refresh nextSelection env]
    result.owner = .css ∧ result.frames = [4] := by decide

theorem independent_consumer_witness :
    let overridden := step initial (.setKeyframes (.ok [5]))
    let started := step overridden .startTransition
    let changed := step started (.refresh nextSelection env)
    changed.frames = [5] ∧ computed changed.selection changed.environment = [4] ∧
    changed.transition = some ⟨10, 7, [2]⟩ ∧
    (step changed .startTransition).transition = some ⟨11, 9, [4]⟩ := by decide

end EffectOwnership
