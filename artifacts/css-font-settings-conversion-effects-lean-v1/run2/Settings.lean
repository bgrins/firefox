namespace FontSettingsEffects

inductive Demand where
  | parentSize | parentMetrics | viewport | selectedTree | randomSeed
  deriving DecidableEq, Repr

structure Expr where
  payload : Nat
  reads : List Demand
  deriving DecidableEq, Repr

structure Entry where
  tag : Nat
  scope : Nat
  expr : Expr
  deriving DecidableEq, Repr

structure Env where
  ready : Nat → Demand → Bool
  convert : Nat → Expr → Nat × List Nat

structure Receipt where
  entry : Entry
  value : Nat
  effects : List Nat
  deriving DecidableEq, Repr

structure State where
  done : List Receipt
  todo : List Entry
  deriving DecidableEq, Repr

def ready (env : Env) (entry : Entry) : Bool :=
  entry.expr.reads.all (env.ready entry.scope)

def convert (env : Env) (entry : Entry) : Receipt :=
  let output := env.convert entry.scope entry.expr
  ⟨entry, output.1, output.2⟩

def poll (env : Env) (state : State) : State :=
  match state.todo with
  | [] => state
  | entry :: rest =>
    if ready env entry then ⟨state.done ++ [convert env entry], rest⟩ else state

def run : List Env → State → State
  | [], state => state
  | env :: rest, state => run rest (poll env state)

def projection (state : State) : List Entry := state.done.map Receipt.entry ++ state.todo

def effects (receipts : List Receipt) : List Nat := receipts.flatMap Receipt.effects

def lookupLast (tag : Nat) : List Receipt → Option Nat
  | [] => none
  | receipt :: rest =>
    match lookupLast tag rest with
    | some value => some value
    | none => if receipt.entry.tag = tag then some receipt.value else none

structure Publication where
  receipts : List Receipt
  deriving DecidableEq, Repr

def publish (state : State) : Option Publication :=
  if state.todo.isEmpty then some ⟨state.done⟩ else none

theorem pending_preserves (env : Env) (done : List Receipt) (entry : Entry)
    (rest : List Entry) (h : ready env entry = false) :
    poll env ⟨done, entry :: rest⟩ = ⟨done, entry :: rest⟩ := by
  simp [poll, h]

theorem admitted_once (env : Env) (done : List Receipt) (entry : Entry)
    (rest : List Entry) (h : ready env entry = true) :
    poll env ⟨done, entry :: rest⟩ = ⟨done ++ [convert env entry], rest⟩ := by
  simp [poll, h]

theorem selected_scope (env : Env) (entry : Entry) :
    (convert env entry).value = (env.convert entry.scope entry.expr).1 ∧
    (convert env entry).effects = (env.convert entry.scope entry.expr).2 := by
  simp [convert]

theorem poll_projection (env : Env) (state : State) :
    projection (poll env state) = projection state := by
  rcases state with ⟨done, todo⟩
  cases todo with
  | nil => rfl
  | cons entry rest =>
    simp only [poll]
    split <;> simp [projection, convert, List.append_assoc]

theorem run_projection (schedule : List Env) (state : State) :
    projection (run schedule state) = projection state := by
  induction schedule generalizing state with
  | nil => rfl
  | cons env rest ih => rw [run, ih, poll_projection]

theorem poll_retains_prefix (env : Env) (state : State) :
    ∃ suffix, (poll env state).done = state.done ++ suffix := by
  rcases state with ⟨done, todo⟩
  cases todo with
  | nil => exact ⟨[], by simp [poll]⟩
  | cons entry rest =>
    simp only [poll]
    split
    · exact ⟨[convert env entry], rfl⟩
    · exact ⟨[], by simp⟩

theorem run_retains_prefix (schedule : List Env) (state : State) :
    ∃ suffix, (run schedule state).done = state.done ++ suffix := by
  induction schedule generalizing state with
  | nil => exact ⟨[], by simp [run]⟩
  | cons env rest ih =>
    obtain ⟨first, hf⟩ := poll_retains_prefix env state
    obtain ⟨later, hl⟩ := ih (poll env state)
    exact ⟨first ++ later, by simp [run, hl, hf, List.append_assoc]⟩

theorem run_count_conserved (schedule : List Env) (state : State) :
    (run schedule state).done.length + (run schedule state).todo.length =
      state.done.length + state.todo.length := by
  have h := congrArg List.length (run_projection schedule state)
  simpa [projection] using h

theorem complete_stays (env : Env) (done : List Receipt) :
    poll env ⟨done, []⟩ = ⟨done, []⟩ := rfl

theorem effect_prefix (schedule : List Env) (state : State) :
    ∃ suffix, effects (run schedule state).done = effects state.done ++ effects suffix := by
  obtain ⟨suffix, h⟩ := run_retains_prefix schedule state
  exact ⟨suffix, by simp [h, effects]⟩

theorem publication_requires_complete (state : State) (output : Publication)
    (h : publish state = some output) : state.todo = [] ∧ output.receipts = state.done := by
  rcases state with ⟨done, todo⟩
  cases todo with
  | nil =>
    have he : output = ⟨done⟩ := by simpa [publish] using h.symm
    simp [he]
  | cons entry rest => simp [publish] at h

theorem published_projection (schedule : List Env) (entries : List Entry)
    (output : Publication) (h : publish (run schedule ⟨[], entries⟩) = some output) :
    output.receipts.map Receipt.entry = entries := by
  obtain ⟨empty, receipts⟩ := publication_requires_complete _ _ h
  have hp := run_projection schedule ⟨[], entries⟩
  simpa [projection, empty, ← receipts] using hp

theorem last_duplicate_wins (tag : Nat) (a b : Receipt)
    (hb : b.entry.tag = tag) : lookupLast tag [a, b] = some b.value := by
  simp [lookupLast, hb]

theorem discarded_duplicate_effects (a b : Receipt) :
    effects [a, b] = a.effects ++ b.effects := by
  simp [effects]

def drain (env : Env) (fuel : Nat) (state : State) : State :=
  run (List.replicate fuel env) state

theorem ready_list_finishes (env : Env) (entries : List Entry) (done : List Receipt)
    (h : ∀ entry ∈ entries, ready env entry = true) :
    drain env entries.length ⟨done, entries⟩ = ⟨done ++ entries.map (convert env), []⟩ := by
  induction entries generalizing done with
  | nil => simp [drain, run]
  | cons entry rest ih =>
    have head := h entry (by simp)
    have tail : ∀ item ∈ rest, ready env item = true := by
      intro item hm
      exact h item (by simp [hm])
    simpa [drain, run, List.replicate_succ, poll, head, List.append_assoc] using
      ih (done ++ [convert env entry]) tail

def a : Entry := ⟨1, 7, ⟨20, [.parentSize]⟩⟩
def b : Entry := ⟨1, 9, ⟨30, [.selectedTree]⟩⟩
def complete : Env := ⟨fun _ _ => true, fun scope expr => (scope + expr.payload, [scope])⟩
def waiting : Env := ⟨fun _ _ => false, complete.convert⟩
def secondPending : Env := ⟨fun _ demand => demand == .parentSize, complete.convert⟩
def exampleDone : State := drain complete 2 ⟨[], [a, b]⟩

theorem duplicate_example : lookupLast 1 exampleDone.done = some 39 ∧
    effects exampleDone.done = [7, 9] := by decide

theorem pause_resume_example :
    run [secondPending, waiting, complete] ⟨[], [a, b]⟩ = exampleDone := by decide

end FontSettingsEffects
