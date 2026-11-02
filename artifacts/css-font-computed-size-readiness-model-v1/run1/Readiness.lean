import Std

namespace ComputedSizeReadiness

structure Token where
  session : Nat
  index : Nat
  selection : Nat
  context : Nat
  deriving DecidableEq, Repr

inductive Phase where
  | semanticOpen | closed | computedSize | whole | cycle
  deriving DecidableEq, Repr

inductive Demand where
  | computedSize | metrics | orientedMetrics
  deriving DecidableEq, Repr

inductive Purpose where
  | unit (demand : Demand)
  | ordinary | reference
  deriving DecidableEq, Repr

structure Node where
  token : Token
  phase : Phase
  size : Option Nat
  applications : Nat
  deriving DecidableEq, Repr

inductive Reply where
  | pending
  | computedSize (token : Token) (value : Nat)
  | complete (token : Token)
  | cycle (token : Token)
  deriving DecidableEq, Repr

def read (expected : Token) (purpose : Purpose) (node : Node) : Reply :=
  if expected != node.token then .pending else
  match node.phase with
  | .whole => .complete node.token
  | .cycle => .cycle node.token
  | .computedSize =>
      match purpose, node.size with
      | .unit .computedSize, some value => .computedSize node.token value
      | _, _ => .pending
  | _ => .pending

inductive Action where
  | close
  | publishSize (value : Nat)
  | finishOrdinary
  | settleCycle
  deriving DecidableEq, Repr

def step (expected : Token) (action : Action) (node : Node) : Option Node :=
  if expected != node.token then none else
  match action, node.phase with
  | .close, .semanticOpen => some { node with phase := .closed }
  | .settleCycle, .semanticOpen => some { node with phase := .cycle }
  | .publishSize value, .closed =>
      if node.size.isNone && node.applications == 0 then
        some { node with phase := .computedSize, size := some value, applications := 1 }
      else none
  | .finishOrdinary, .computedSize => some { node with phase := .whole }
  | _, _ => none

def run (expected : Token) : List Action → Node → Option Node
  | [], node => some node
  | action :: rest, node => do
      let next ← step expected action node
      run expected rest next

def initial (token : Token) : Node := ⟨token, .semanticOpen, none, 0⟩
def closed (token : Token) : Node := ⟨token, .closed, none, 0⟩
def partial (token : Token) (value : Nat) : Node := ⟨token, .computedSize, some value, 1⟩
def complete (token : Token) (value : Nat) : Node := ⟨token, .whole, some value, 1⟩

theorem publish_requires_semantic_closure (token : Token) (value : Nat) :
    step token (.publishSize value) (initial token) = none := by
  simp [step, initial]

theorem closed_publishes_size (token : Token) (value : Nat) :
    step token (.publishSize value) (closed token) = some (partial token value) := by
  simp [step, closed, partial]

theorem facet_is_not_whole (token : Token) (value : Nat) :
    (partial token value).phase ≠ .whole := by
  simp [partial]

theorem exact_unit_can_read (token : Token) (value : Nat) :
    read token (.unit .computedSize) (partial token value) = .computedSize token value := by
  simp [read, partial]

theorem stronger_unit_waits (token : Token) (value : Nat) (demand : Demand)
    (stronger : demand ≠ .computedSize) :
    read token (.unit demand) (partial token value) = .pending := by
  cases demand <;> simp_all [read, partial]

theorem ordinary_waits (token : Token) (value : Nat) :
    read token .ordinary (partial token value) = .pending := by
  simp [read, partial]

theorem generic_reference_waits (token : Token) (value : Nat) :
    read token .reference (partial token value) = .pending := by
  simp [read, partial]

theorem stale_token_waits (expected : Token) (purpose : Purpose) (node : Node)
    (different : expected ≠ node.token) : read expected purpose node = .pending := by
  simp [read, different]

theorem stale_action_rejected (expected : Token) (action : Action) (node : Node)
    (different : expected ≠ node.token) : step expected action node = none := by
  simp [step, different]

theorem second_application_rejected (token : Token) (first second : Nat) :
    step token (.publishSize second) (partial token first) = none := by
  simp [step, partial]

theorem ordinary_completion_preserves_value_and_count (token : Token) (value : Nat) :
    step token .finishOrdinary (partial token value) = some (complete token value) := by
  simp [step, partial, complete]

theorem completed_property_rejects_reapplication (token : Token) (first second : Nat) :
    step token (.publishSize second) (complete token first) = none := by
  simp [step, complete]

theorem actual_three_stage_execution (token : Token) (value : Nat) :
    run token [.close, .publishSize value, .finishOrdinary] (initial token) =
      some (complete token value) := by
  simp [run, step, initial, complete]

structure Session where
  generation : Nat
  retained : List Node
  deriving DecidableEq, Repr

def terminal (node : Node) : Bool := node.phase == .whole || node.phase == .cycle

def reset (session : Session) : Option Session :=
  if session.retained.all terminal then some ⟨session.generation + 1, []⟩ else none

def query (session : Session) (expected : Token) (purpose : Purpose) : Reply :=
  if expected.session != session.generation then .pending else
  match session.retained.find? (fun node => node.token == expected) with
  | some node => read expected purpose node
  | none => .pending

theorem reset_rejects_retained_partial (generation : Nat) (token : Token) (value : Nat)
    (before after : List Node) :
    reset ⟨generation, before ++ partial token value :: after⟩ = none := by
  simp [reset, terminal, partial, List.all_append]

theorem reset_rejects_open_or_closed (generation : Nat) (token : Token) :
    reset ⟨generation, [initial token]⟩ = none ∧
    reset ⟨generation, [closed token]⟩ = none := by
  simp [reset, terminal, initial, closed]

theorem terminal_session_can_reset (generation : Nat) (token : Token) (value : Nat) :
    reset ⟨generation, [complete token value]⟩ = some ⟨generation + 1, []⟩ := by
  simp [reset, terminal, complete]

theorem session_mismatch_rejects_any_node (session : Session) (expected : Token)
    (purpose : Purpose) (different : expected.session ≠ session.generation) :
    query session expected purpose = .pending := by
  simp [query, different]

theorem same_index_new_session_cannot_accept_old_reply (generation index selection context value : Nat)
    (purpose : Purpose) :
    query ⟨generation + 1, [partial ⟨generation + 1, index, selection, context⟩ value]⟩
      ⟨generation, index, selection, context⟩ purpose = .pending := by
  simp [query]

theorem retained_facet_allows_only_typed_unit (token : Token) (value : Nat) :
    query ⟨token.session, [partial token value]⟩ token (.unit .computedSize) =
      .computedSize token value ∧
    query ⟨token.session, [partial token value]⟩ token .ordinary = .pending := by
  simp [query, read, partial]

def witnessToken : Token := ⟨0, 1, 2, 3⟩
def witnessPartial : Node := partial witnessToken 20

end ComputedSizeReadiness
