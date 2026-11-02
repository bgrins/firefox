import Stability

namespace SelectedResumption
open SelectedDeclaration PreparationStability

inductive Task (E : Type) where
  | read (edge : E) (value : Nat)
  | combine (left right : Task E)
  deriving DecidableEq, Repr

inductive Instruction (E : Type) where
  | read (edge : E) (value : Nat)
  | combine
  | unsupported (edge : E)
  deriving DecidableEq, Repr

def Task.value (combine : Nat → Nat → Nat) : Task E → Nat
  | .read _ value => value
  | .combine left right => combine (left.value combine) (right.value combine)

def Task.reads : Task E → List E
  | .read edge _ => [edge]
  | .combine left right => left.reads ++ right.reads

def Task.code : Task E → List (Instruction E)
  | .read edge value => [.read edge value]
  | .combine left right => left.code ++ right.code ++ [.combine]

structure Cursor (E : Type) where
  todo : List (Instruction E)
  values : List Nat
  reads : List E
  actions : Nat
  deriving DecidableEq, Repr

def tick (combine : Nat → Nat → Nat) (cursor : Cursor E) : Option (Cursor E) :=
  match cursor.todo with
  | [] => none
  | .unsupported _ :: _ => none
  | .read edge value :: rest =>
      some ⟨rest, value :: cursor.values, cursor.reads ++ [edge], cursor.actions + 1⟩
  | .combine :: rest =>
      match cursor.values with
      | right :: left :: values =>
          some ⟨rest, combine left right :: values, cursor.reads, cursor.actions + 1⟩
      | _ => none

def execute (combine : Nat → Nat → Nat) :
    List (Instruction E) → List Nat → List E → Nat → Option (Cursor E)
  | [], values, reads, actions => some ⟨[], values, reads, actions⟩
  | .unsupported _ :: _, _, _, _ => none
  | .read edge value :: rest, values, reads, actions =>
      execute combine rest (value :: values) (reads ++ [edge]) (actions + 1)
  | .combine :: rest, right :: left :: values, reads, actions =>
      execute combine rest (combine left right :: values) reads (actions + 1)
  | .combine :: _, _, _, _ => none

def completion (combine : Nat → Nat → Nat) (cursor : Cursor E) :=
  execute combine cursor.todo cursor.values cursor.reads cursor.actions

theorem compiled_task_executes (combine : Nat → Nat → Nat) (task : Task E)
    (tail : List (Instruction E)) (values : List Nat) (reads : List E) (actions : Nat) :
    execute combine (task.code ++ tail) values reads actions =
      execute combine tail (task.value combine :: values) (reads ++ task.reads)
        (actions + task.code.length) := by
  induction task generalizing tail values reads actions with
  | read edge value => simp [Task.code, Task.value, Task.reads, execute]
  | combine left right ihl ihr =>
      simp only [Task.code, List.append_assoc]
      rw [ihl, ihr]
      simp [execute, Task.value, Task.reads, List.append_assoc, Nat.add_assoc]

theorem tick_preserves_completion (combine : Nat → Nat → Nat) (before after : Cursor E)
    (step : tick combine before = some after) :
    completion combine before = completion combine after := by
  cases before with
  | mk todo values reads actions =>
      cases todo with
      | nil => simp [tick] at step
      | cons instruction rest =>
          cases instruction with
          | unsupported edge => simp [tick] at step
          | read edge value =>
              simp only [tick, Option.some.injEq] at step
              subst after
              rfl
          | combine =>
              cases values with
              | nil => simp [tick] at step
              | cons right restValues =>
                  cases restValues with
                  | nil => simp [tick] at step
                  | cons left values =>
                      simp only [tick, Option.some.injEq] at step
                      subst after
                      rfl

theorem tick_decreases_remaining_actions (combine : Nat → Nat → Nat)
    (before after : Cursor E) (step : tick combine before = some after) :
    after.todo.length + 1 = before.todo.length ∧ after.actions = before.actions + 1 := by
  cases before with
  | mk todo values reads actions =>
      cases todo with
      | nil => simp [tick] at step
      | cons instruction rest =>
          cases instruction with
          | unsupported edge => simp [tick] at step
          | read edge value => simp_all [tick]
          | combine =>
              cases values with
              | nil => simp [tick] at step
              | cons right restValues =>
                  cases restValues with
                  | nil => simp [tick] at step
                  | cons left values => simp_all [tick]

inductive Advances (combine : Nat → Nat → Nat) : Cursor E → Cursor E → Prop where
  | refl (cursor) : Advances combine cursor cursor
  | next {before middle after} : tick combine before = some middle →
      Advances combine middle after → Advances combine before after

theorem finite_pauses_preserve_completion (combine : Nat → Nat → Nat)
    (before after : Cursor E) (steps : Advances combine before after) :
    completion combine before = completion combine after := by
  induction steps with
  | refl => rfl
  | next step _ ih => exact (tick_preserves_completion _ _ _ step).trans ih

def takeValue (cursor : Cursor E) : Option Nat :=
  match cursor.todo, cursor.values with
  | [], [value] => some value
  | _, _ => none

theorem pending_has_no_value (cursor : Cursor E) (pending : cursor.todo ≠ []) :
    takeValue cursor = none := by
  cases cursor with
  | mk todo values reads actions =>
      cases todo <;> simp_all [takeValue]

structure Waiting (S D E : Type) where
  state : S
  declaration : D
  remaining : List D
  cursor : Cursor E

def resume (combine : Nat → Nat → Nat) (waiting : Waiting S D E) :
    Option (Waiting S D E) :=
  (tick combine waiting.cursor).map fun cursor => {waiting with cursor}

theorem resume_retains_selection (combine : Nat → Nat → Nat)
    (before after : Waiting S D E) (step : resume combine before = some after) :
    after.state = before.state ∧ after.declaration = before.declaration ∧
      after.remaining = before.remaining := by
  unfold resume at step
  cases next : tick combine before.cursor <;> simp [next] at step
  next cursor => subst after; exact ⟨rfl, rfl, rfl⟩

structure Plan (S V E : Type) where
  task : Task E
  consume : Nat → Next S V

def direct (combine : Nat → Nat → Nat) (plan : Plan S V E) : Evaluation S V E :=
  ⟨plan.consume (plan.task.value combine), plan.task.reads⟩

def fromCursor (plan : Plan S V E) (cursor : Cursor E) : Option (Evaluation S V E) :=
  (takeValue cursor).map fun value => ⟨plan.consume value, cursor.reads⟩

def start (task : Task E) : Cursor E := ⟨task.code, [], [], 0⟩

theorem completed_task_consumes_produced_value (combine : Nat → Nat → Nat)
    (plan : Plan S V E) :
    (completion combine (start plan.task)).bind (fromCursor plan) = some (direct combine plan) := by
  have done := compiled_task_executes combine plan.task [] [] [] 0
  simpa [completion, start, execute, fromCursor, takeValue, direct] using
    congrArg (fun outcome => outcome.bind (fromCursor plan)) done

def executed (combine : Nat → Nat → Nat) (plan : Plan S V E) : Evaluation S V E :=
  ((completion combine (start plan.task)).bind (fromCursor plan)).getD ⟨.blocked, []⟩

theorem executed_eq_direct (combine : Nat → Nat → Nat) (plan : Plan S V E) :
    executed combine plan = direct combine plan := by
  simp [executed, completed_task_consumes_produced_value]

def resumedScan (combine : Nat → Nat → Nat) (eligible : S → D → Bool)
    (plan : S → D → Plan S V E) (state : S) : List D → Result D V E
  | [] => ⟨.exhausted, [], []⟩
  | d :: rest =>
      if eligible state d then
        let result := executed combine (plan state d)
        match result.next with
        | .terminal value => ⟨.terminal value, [d], result.reads⟩
        | .blocked => ⟨.blocked, [d], result.reads⟩
        | .rollback next => prepend d result.reads (resumedScan combine eligible plan next rest)
      else resumedScan combine eligible plan state rest

theorem resumable_scan_refines_selection (combine : Nat → Nat → Nat)
    (eligible : S → D → Bool) (plan : S → D → Plan S V E) (state : S) (decls : List D) :
    resumedScan combine eligible plan state decls =
      scan eligible (fun state d => direct combine (plan state d)) state decls := by
  induction decls generalizing state with
  | nil => rfl
  | cons d rest ih =>
      simp only [resumedScan, scan, executed_eq_direct]
      split
      next yes =>
        split <;> simp_all
      next no => exact ih state

theorem stable_resumption_refines_selection (combine : Nat → Nat → Nat)
    (eligible eligible' : S → D → Bool) (plan : S → D → Plan S V E)
    (evaluate : S → D → Evaluation S V E) (state : S) (decls : List D)
    (stable : ∀ point ∈ visited eligible evaluate state decls,
      agreesAt eligible eligible' evaluate (fun state d => direct combine (plan state d)) point) :
    resumedScan combine eligible' plan state decls = scan eligible evaluate state decls := by
  rw [resumable_scan_refines_selection]
  exact scan_eq_of_reached_agreement _ _ _ _ _ _ stable

structure Published (S D V E : Type) where
  waiting : Option (Waiting S D E)
  evaluations : List D
  values : List (Option V)

def publish (plan : Plan S V E) (state : Published S D V E) : Published S D V E :=
  match state.waiting with
  | none => state
  | some waiting =>
      match fromCursor plan waiting.cursor with
      | some ⟨.terminal value, _⟩ =>
          ⟨none, state.evaluations ++ [waiting.declaration], state.values ++ [value]⟩
      | _ => state

theorem blocked_cannot_publish (plan : Plan S V E) (state : Published S D V E)
    (waiting : Waiting S D E) (held : state.waiting = some waiting)
    (pending : waiting.cursor.todo ≠ []) : publish plan state = state := by
  simp [publish, held, fromCursor, pending_has_no_value _ pending]

theorem completed_terminal_publishes_once (plan : Plan S V E)
    (state : Published S D V E) (waiting : Waiting S D E) (value : Option V)
    (held : state.waiting = some waiting)
    (ready : fromCursor plan waiting.cursor = some ⟨.terminal value, waiting.cursor.reads⟩) :
    (publish plan state).evaluations = state.evaluations ++ [waiting.declaration] ∧
    (publish plan state).values = state.values ++ [value] ∧
    publish plan (publish plan state) = publish plan state := by
  simp [publish, held, ready]

def prerequisite : Task String := .combine (.read "size" 20) (.read "scale" 35)
def weightPlan : Plan Unit Nat String := ⟨prerequisite, fun n => .terminal (some n)⟩
def scheduled : Published Unit Nat Nat String :=
  ⟨some ⟨(), 7, [8], start prerequisite⟩, [], []⟩

theorem scheduling_is_not_completion :
    (publish weightPlan scheduled).values = [] ∧
    prerequisite.value Nat.mul = 700 ∧ (20 : Nat) ≠ 700 := by decide

def unsupported : Cursor String := ⟨[.unsupported "metric-cycle-or-missing-producer"], [20], [], 0⟩

theorem unsupported_stays_blocked_not_invalid :
    tick Nat.mul unsupported = none ∧ takeValue unsupported = none ∧
    completion Nat.mul unsupported = none := by decide

end SelectedResumption
