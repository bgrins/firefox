import Std

namespace MaskedBaseInput

structure Composed where
  font : Nat
  durations : List Nat
  deriving DecidableEq, Repr

inductive Owner | css | script
  deriving DecidableEq, Repr

structure State (Input View : Type) where
  input : Input
  composed : View
  applied : Nat
  owner : Owner
  deriving DecidableEq, Repr

def maskedView (_ : Nat) : Composed := ⟨32, [2000, 2000]⟩
def duration (font : Nat) : Nat := font * 1000 / 16

def before : State Nat Composed := ⟨16, maskedView 16, 1000, .css⟩

def composedStep {I V : Type} [DecidableEq V]
    (view : I → V) (timing : I → Nat) (s : State I V) (next : I) : State I V :=
  { s with
    input := next
    composed := view next
    applied := if s.owner = .css ∧ s.composed ≠ view next then timing next else s.applied }

def inputStep {I V : Type} [DecidableEq I] [DecidableEq V]
    (view : I → V) (timing : I → Nat) (s : State I V) (next : I) : State I V :=
  { s with
    input := next
    composed := view next
    applied := if s.owner = .css ∧ (s.composed ≠ view next ∨ s.input ≠ next)
               then timing next else s.applied }

def runInputs {I V : Type} [DecidableEq I] [DecidableEq V]
    (view : I → V) (timing : I → Nat) : State I V → List I → State I V
  | s, [] => s
  | s, next :: rest => runInputs view timing (inputStep view timing s next) rest

theorem composed_equality_is_insufficient :
    maskedView 16 = maskedView 32 ∧
    before.input ≠ 32 ∧ duration before.input = 1000 ∧ duration 32 = 2000 ∧
    (composedStep maskedView duration before 32).applied = 1000 ∧
    (composedStep maskedView duration before 32).input = 32 := by decide

theorem input_step_synchronizes {I V : Type} [DecidableEq I] [DecidableEq V]
    (view : I → V) (timing : I → Nat) (s : State I V) (next : I)
    (css : s.owner = .css) (synced : s.applied = timing s.input) :
    (inputStep view timing s next).applied = timing next ∧
    (inputStep view timing s next).owner = .css := by
  by_cases changed : s.input = next
  · simp [inputStep, css, synced, changed]
  · simp [inputStep, css, changed]

theorem arbitrary_finite_input_history {I V : Type} [DecidableEq I] [DecidableEq V]
    (view : I → V) (timing : I → Nat) (events : List I) (s : State I V)
    (css : s.owner = .css) (synced : s.applied = timing s.input) :
    (runInputs view timing s events).applied = timing (runInputs view timing s events).input ∧
    (runInputs view timing s events).owner = .css := by
  induction events generalizing s with
  | nil => exact ⟨synced, css⟩
  | cons next rest ih =>
    have step := input_step_synchronizes view timing s next css synced
    exact ih (inputStep view timing s next) step.2 step.1

theorem script_ownership_survives_history {I V : Type} [DecidableEq I] [DecidableEq V]
    (view : I → V) (timing : I → Nat) (events : List I) (s : State I V)
    (script : s.owner = .script) :
    (runInputs view timing s events).applied = s.applied ∧
    (runInputs view timing s events).owner = .script := by
  induction events generalizing s with
  | nil => exact ⟨rfl, script⟩
  | cons next rest ih =>
    have stepOwner : (inputStep view timing s next).owner = .script := script
    have restResult := ih (inputStep view timing s next) stepOwner
    simpa [runInputs, inputStep, script] using restResult

theorem complete_generation_detects_timing_change {I G : Type}
    (timing : I → Nat) (generation : I → G)
    (complete : ∀ a b, generation a = generation b → timing a = timing b)
    (old next : I) (changed : timing old ≠ timing next) :
    generation old ≠ generation next := by
  intro equal
  exact changed (complete old next equal)

theorem recorded_input_change_is_admitted :
    (inputStep maskedView duration before 32).applied = 2000 ∧
    (inputStep maskedView duration before 32).composed = before.composed ∧
    750 * 4 = duration 16 * 3 ∧ 750 * 8 = duration 32 * 3 := by decide

end MaskedBaseInput
