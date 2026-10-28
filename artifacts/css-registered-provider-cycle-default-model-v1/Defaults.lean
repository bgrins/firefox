import GuardCycle
import Admission

namespace ProviderDefaults
open AttributeGuard (Key State participants)

inductive Outcome where
  | value (n : Nat)
  | missing | rejected | pending
  deriving DecidableEq, Repr

inductive Classified where
  | value (n : Nat)
  | missing | rejected | cyclic | pending
  deriving DecidableEq, Repr

structure Result where
  outcome : Outcome
  state : State
  deriving DecidableEq, Repr

def classify (key : Key) (r : Result) : Classified :=
  if key ∈ r.state.poisoned then .cyclic else
  match r.outcome with
  | .value n => .value n
  | .missing => .missing
  | .rejected => .rejected
  | .pending => .pending

def defaultAfter (initial : Nat) : Classified → Outcome
  | .value n => .value n
  | .missing | .rejected | .cyclic => .value initial
  | .pending => .pending

def publish (initial : Nat) (key : Key) (r : Result) : Result :=
  ⟨defaultAfter initial (classify key r), r.state⟩

def fallback (r : Result) (next : State → Result) : Result :=
  match r.outcome with
  | .missing => next r.state
  | _ => r

def guarded (markCycles : Bool) (initial : Nat) (key : Key) (s : State)
    (body : State → Result) : Result :=
  if key ∈ s.active then
    if markCycles then
      ⟨.missing, { s with poisoned := participants key s.active ++ s.poisoned }⟩
    else ⟨.value initial, s⟩
  else
    let r := body { s with active := key :: s.active }
    let done := publish initial key r
    { done with state := { done.state with active := s.active } }

inductive Expr where
  | literal (n : Nat)
  | missing | reject
  | ref (name : Nat) (otherwise : Expr)
  | plusOne (e : Expr)
  deriving DecidableEq, Repr

structure Environment where
  initial : Nat → Nat
  body : Nat → Expr

def evaluate (markCycles : Bool) (env : Environment) : Nat → Expr → State → Result
  | 0, _, s => ⟨.pending, s⟩
  | fuel + 1, expr, s =>
    match expr with
    | .literal n => ⟨.value n, s⟩
    | .missing => ⟨.missing, s⟩
    | .reject => ⟨.rejected, s⟩
    | .ref name otherwise =>
      fallback (guarded markCycles (env.initial name) (.property name) s
        (evaluate markCycles env fuel (env.body name)))
        (evaluate markCycles env fuel otherwise)
    | .plusOne e =>
      let r := evaluate markCycles env fuel e s
      match r.outcome with
      | .value n => { r with outcome := .value (n + 1) }
      | _ => r

def property (markCycles : Bool) (env : Environment) (fuel name : Nat) : Result :=
  guarded markCycles (env.initial name) (.property name) {}
    (evaluate markCycles env fuel (env.body name))

theorem marked_classifies_cyclic (key : Key) (r : Result)
    (h : key ∈ r.state.poisoned) : classify key r = .cyclic := by
  simp [classify, h]

theorem marked_defaults (initial : Nat) (key : Key) (r : Result)
    (h : key ∈ r.state.poisoned) :
    (publish initial key r).outcome = .value initial := by
  simp [publish, marked_classifies_cyclic key r h, defaultAfter]

theorem publication_preserves_participants (initial : Nat) (key : Key) (r : Result) :
    (publish initial key r).state.poisoned = r.state.poisoned := rfl

theorem all_marked_participants_default (defaults : Key → Nat) (r : Result) :
    ∀ key ∈ r.state.poisoned,
      (publish (defaults key) key r).outcome = .value (defaults key) := by
  intro key marked
  exact marked_defaults (defaults key) key r marked

theorem reentry_marks_exact_cycle (initial : Nat) (key : Key) (front suffix : List Key)
    (s : State) (body : State → Result) (fresh : key ∉ front)
    (stack : s.active = front ++ key :: suffix) :
    (guarded true initial key s body).state.poisoned =
      (front ++ [key]) ++ s.poisoned := by
  simp [guarded, stack, AttributeGuard.participants_exact key front suffix fresh]

theorem unmarked_ready_retained (initial n : Nat) (key : Key) (s : State)
    (clear : key ∉ s.poisoned) :
    (publish initial key ⟨.value n, s⟩).outcome = .value n := by
  simp [publish, classify, clear, defaultAfter]

theorem pending_not_defaulted (initial : Nat) (key : Key) (s : State)
    (clear : key ∉ s.poisoned) :
    (publish initial key ⟨.pending, s⟩).outcome = .pending := by
  simp [publish, classify, clear, defaultAfter]

theorem missing_uses_fallback (s : State) (next : State → Result) :
    fallback ⟨.missing, s⟩ next = next s := rfl

theorem rejected_does_not_retry (s : State) (next : State → Result) :
    fallback ⟨.rejected, s⟩ next = ⟨.rejected, s⟩ := rfl

theorem computed_default_excludes_fallback (n : Nat) (s : State)
    (next : State → Result) : fallback ⟨.value n, s⟩ next = ⟨.value n, s⟩ := rfl

theorem marked_survives_fallback (initial : Nat) (key : Key) (s : State)
    (next : State → Result) (marked : key ∈ s.poisoned)
    (preserves : ∀ key ∈ s.poisoned, key ∈ (next s).state.poisoned) :
    (publish initial key (fallback ⟨.missing, s⟩ next)).outcome = .value initial := by
  exact marked_defaults initial key (next s) (preserves key marked)

def mutualEnv : Environment :=
  ⟨fun n => if n = 0 then 3 else if n = 1 then 7 else 13,
   fun n => if n = 0 then .ref 1 (.literal 11)
     else if n = 1 then .plusOne (.ref 0 (.literal 11))
     else .ref 1 (.literal 17)⟩

def self : Environment :=
  ⟨fun _ => 3, fun _ => .plusOne (.ref 0 (.literal 11))⟩

def rejection : Environment :=
  ⟨fun n => if n = 0 then 3 else 7,
   fun n => if n = 0 then .reject else .ref 0 (.literal 11)⟩

theorem mutual_participants_default :
    (property true mutualEnv 12 0).outcome = .value 3 ∧
    (property true mutualEnv 12 1).outcome = .value 7 := by decide +kernel

theorem nonparticipant_uses_final_default :
    (property true mutualEnv 12 2).outcome = .value 7 ∧
    Key.property 2 ∉ (property true mutualEnv 12 2).state.poisoned := by decide +kernel

theorem early_default_hides_mutual_cycle :
    (property false mutualEnv 12 0).outcome = .value 4 ∧
    (property false mutualEnv 12 0).state.poisoned = [] := by decide +kernel

theorem self_fallback_cannot_rescue :
    (property true self 12 0).outcome = .value 3 ∧
    (property false self 12 0).outcome = .value 4 := by decide +kernel

theorem rejected_provider_publishes_default :
    (property true rejection 12 1).outcome = .value 3 := by decide +kernel

def plainMutual : Environment :=
  ⟨mutualEnv.initial,
   fun n => if n = 0 then .ref 1 (.literal 11)
     else if n = 1 then .ref 0 (.literal 11)
     else .ref 1 (.literal 17)⟩

theorem keyword_mutual_each_own_default :
    (property true plainMutual 12 0).outcome = .value 3 ∧
    (property true plainMutual 12 1).outcome = .value 7 ∧
    (property true plainMutual 12 2).outcome = .value 7 := by decide +kernel

theorem missing_fallback_control :
    fallback ⟨.missing, {}⟩ (fun s => ⟨.value 11, s⟩) = ⟨.value 11, {}⟩ := rfl

theorem prior_admission_boundary (env : Nat → RegisteredNumber.Provider) (k : Nat)
    (r : RegisteredNumber.Raw) (otherwise : RegisteredNumber.Expr)
    (ready : env k = .ready r) (bad : RegisteredNumber.infer r ≠ some .number) :
    RegisteredNumber.plan env (.reference k otherwise) = .invalid :=
  RegisteredNumber.wrong_type_ready_does_not_retry env k r otherwise ready bad

end ProviderDefaults
