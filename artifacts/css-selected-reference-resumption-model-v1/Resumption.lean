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
          | read edge value =>
              simp only [tick, Option.some.injEq] at step
              subst after
              simp
          | combine =>
              cases values with
              | nil => simp [tick] at step
              | cons right restValues =>
                  cases restValues with
                  | nil => simp [tick] at step
                  | cons left values =>
                      simp only [tick, Option.some.injEq] at step
                      subst after
                      simp

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


theorem execution_produces_actual_steps (combine : Nat → Nat → Nat)
    (code : List (Instruction E)) (values : List Nat) (reads : List E) (actions : Nat)
    (after : Cursor E) (done : execute combine code values reads actions = some after) :
    Advances combine ⟨code, values, reads, actions⟩ after := by
  induction code generalizing values reads actions with
  | nil =>
      simp only [execute, Option.some.injEq] at done
      subst after
      exact .refl _
  | cons instruction rest ih =>
      cases instruction with
      | unsupported edge => simp [execute] at done
      | read edge value =>
          exact .next rfl (ih (value :: values) (reads ++ [edge]) (actions + 1) done)
      | combine =>
          cases values with
          | nil => simp [execute] at done
          | cons right restValues =>
              cases restValues with
              | nil => simp [execute] at done
              | cons left values =>
                  exact .next rfl (ih (combine left right :: values) reads (actions + 1) done)

theorem finite_task_progress (combine : Nat → Nat → Nat) (task : Task E) :
    Advances combine ⟨task.code, [], [], 0⟩
      ⟨[], [task.value combine], task.reads, task.code.length⟩ := by
  apply execution_produces_actual_steps
  simpa [execute] using compiled_task_executes combine task [] [] [] 0

theorem task_children_have_smaller_action_rank (left right : Task E) :
    left.code.length < (Task.combine left right).code.length ∧
    right.code.length < (Task.combine left right).code.length := by
  simp [Task.code]
  omega

def takeValue (cursor : Cursor E) : Option Nat :=
  match cursor.todo, cursor.values with
  | [], [value] => some value
  | _, _ => none

theorem pending_has_no_value (cursor : Cursor E) (pending : cursor.todo ≠ []) :
    takeValue cursor = none := by
  cases cursor with
  | mk todo values reads actions =>
      cases todo <;> simp_all [takeValue]

structure Plan (S V E : Type) where
  task : Task E
  consume : Nat → Next S V


structure Waiting (S D V E : Type) where
  state : S
  declaration : D
  remaining : List D
  plan : Plan S V E
  cursor : Cursor E

def resume (combine : Nat → Nat → Nat) (waiting : Waiting S D V E) :
    Option (Waiting S D V E) :=
  (tick combine waiting.cursor).map fun cursor => {waiting with cursor}

theorem resume_retains_selection (combine : Nat → Nat → Nat)
    (before after : Waiting S D V E) (step : resume combine before = some after) :
    after.state = before.state ∧ after.declaration = before.declaration ∧
      after.remaining = before.remaining ∧ after.plan = before.plan := by
  unfold resume at step
  cases next : tick combine before.cursor <;> simp [next] at step
  next cursor => subst after; exact ⟨rfl, rfl, rfl, rfl⟩


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


theorem paused_task_consumes_same_value (combine : Nat → Nat → Nat)
    (plan : Plan S V E) (paused : Cursor E)
    (progress : Advances combine (start plan.task) paused) :
    (completion combine paused).bind (fromCursor plan) = some (direct combine plan) := by
  rw [← finite_pauses_preserve_completion combine (start plan.task) paused progress]
  exact completed_task_consumes_produced_value combine plan

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
  waiting : Option (Waiting S D V E)
  evaluations : List D
  values : List (Option V)

def publish (state : Published S D V E) : Published S D V E :=
  match state.waiting with
  | none => state
  | some waiting =>
      match fromCursor waiting.plan waiting.cursor with
      | some ⟨.terminal value, _⟩ =>
          ⟨none, state.evaluations ++ [waiting.declaration], state.values ++ [value]⟩
      | _ => state

theorem blocked_cannot_publish (state : Published S D V E)
    (waiting : Waiting S D V E) (held : state.waiting = some waiting)
    (pending : waiting.cursor.todo ≠ []) : publish state = state := by
  simp [publish, held, fromCursor, pending_has_no_value _ pending]

theorem completed_terminal_publishes_once
    (state : Published S D V E) (waiting : Waiting S D V E) (value : Option V)
    (held : state.waiting = some waiting)
    (ready : fromCursor waiting.plan waiting.cursor = some ⟨.terminal value, waiting.cursor.reads⟩) :
    (publish state).evaluations = state.evaluations ++ [waiting.declaration] ∧
    (publish state).values = state.values ++ [value] ∧
    publish (publish state) = publish state := by
  simp [publish, held, ready]

def prerequisite : Task String := .combine (.read "size" 20) (.read "scale" 35)
def weightPlan : Plan Unit Nat String := ⟨prerequisite, fun n => .terminal (some n)⟩
def scheduled : Published Unit Nat Nat String :=
  ⟨some ⟨(), 7, [8], weightPlan, start prerequisite⟩, [], []⟩

theorem scheduling_is_not_completion :
    (publish scheduled).values = [] ∧
    prerequisite.value Nat.mul = 700 ∧ (20 : Nat) ≠ 700 := by decide

def unsupported : Cursor String := ⟨[.unsupported "metric-cycle-or-missing-producer"], [20], [], 0⟩

theorem unsupported_stays_blocked_not_invalid :
    tick Nat.mul unsupported = none ∧ takeValue unsupported = none ∧
    completion Nat.mul unsupported = none := by decide


def rollbackPlan (_ : Nat) (declaration : Nat) : Plan Nat Nat String :=
  if declaration = 0 then
    ⟨.read "rollback" 2, fun next => .rollback next⟩
  else if declaration = 1 then
    ⟨.read "loser" 99, fun value => .terminal (some value)⟩
  else
    ⟨prerequisite, fun value => .terminal (some value)⟩

def rollbackEligible (state declaration : Nat) : Bool := state ≤ declaration

theorem actual_children_then_rollback_and_winner :
    resumedScan Nat.mul rollbackEligible rollbackPlan 0 [0, 1, 2, 3] =
      ⟨.terminal (some 700), [0, 2], ["rollback", "size", "scale"]⟩ := by decide

def pausedWeight : Cursor String :=
  ⟨[.read "scale" 35, .combine], [20], ["size"], 1⟩

def completedWeight : Cursor String := ⟨[], [700], ["size", "scale"], 3⟩

theorem child_production_changes_the_resumed_result :
    tick Nat.mul (start prerequisite) = some pausedWeight ∧
    takeValue pausedWeight = none ∧
    completion Nat.mul pausedWeight = some completedWeight ∧
    fromCursor weightPlan completedWeight = some ⟨.terminal (some 700), ["size", "scale"]⟩ := by decide

def completedPublication : Published Unit Nat Nat String :=
  ⟨some ⟨(), 7, [8], weightPlan, completedWeight⟩, [], []⟩

theorem retrying_completion_does_not_republish :
    (publish (publish completedPublication)).values = [some 700] ∧
    (publish (publish completedPublication)).evaluations = [7] := by decide

end SelectedResumption
