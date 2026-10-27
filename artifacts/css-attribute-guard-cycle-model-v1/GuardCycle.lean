import Init

namespace AttributeGuard

inductive Key where
  | property (name : Nat)
  | attribute (name : Nat)
  deriving DecidableEq, Repr

inductive Token where
  | atom (value : Nat)
  | string (text : List Nat)
  | number (value : Nat)
  deriving DecidableEq, Repr

inductive Expr where
  | literal (tokens : List Token)
  | invalid
  | variable (name : Nat) (fallback : Expr)
  | raw (name : Nat) (fallback : Expr)
  | primitive (name : Nat) (fallback : Expr)
  | typed (name : Nat) (fallback : Expr)
  | append (left right : Expr)
  deriving DecidableEq, Repr

structure Attribute where
  text : List Nat
  expression : Expr
  primitive : Option (List Token)

structure Environment where
  properties : Nat → Expr
  attributes : Nat → Option Attribute
  accepts : Nat → List Token → Bool

structure State where
  active : List Key := []
  poisoned : List Key := []
  guardTrace : List Key := []
  deriving DecidableEq, Repr

inductive Outcome where
  | value (tokens : List Token)
  | invalid
  | exhausted
  deriving DecidableEq, Repr

structure Result where
  outcome : Outcome
  state : State
  deriving DecidableEq, Repr

structure Policy where
  finalCheck : Bool := true
  rawRecurses : Bool := false
  deriving DecidableEq, Repr

def participants (key : Key) : List Key → List Key
  | [] => []
  | current :: rest => current :: if current = key then [] else participants key rest

def finish (checked : Bool) (key : Key) (outcome : Outcome) (state : State) : Outcome :=
  if checked && decide (key ∈ state.poisoned) then .invalid else outcome

def guarded (policy : Policy) (key : Key) (state : State)
    (body : State → Result) : Result :=
  let traced := { state with guardTrace := state.guardTrace ++ [key] }
  if key ∈ state.active then
    ⟨.invalid, { traced with poisoned := participants key state.active ++ state.poisoned }⟩
  else
    let result := body { traced with active := key :: state.active }
    ⟨finish policy.finalCheck key result.outcome result.state,
      { result.state with active := state.active }⟩

def orElse (primary : Result) (fallback : State → Result) : Result :=
  match primary.outcome with
  | .invalid => fallback primary.state
  | _ => primary

def parseTyped (accepts : List Token → Bool) (result : Result) : Result :=
  match result.outcome with
  | .value tokens => if accepts tokens then result else ⟨.invalid, result.state⟩
  | _ => result

def evaluate (policy : Policy) (env : Environment) : Nat → Expr → State → Result
  | 0, _, state => ⟨.exhausted, state⟩
  | fuel + 1, expr, state =>
    match expr with
    | .literal tokens => ⟨.value tokens, state⟩
    | .invalid => ⟨.invalid, state⟩
    | .variable name fallback =>
      orElse (guarded policy (.property name) state
        (evaluate policy env fuel (env.properties name)))
        (evaluate policy env fuel fallback)
    | .raw name fallback =>
      match env.attributes name with
      | none => evaluate policy env fuel fallback state
      | some attr =>
        if policy.rawRecurses then
          orElse (guarded policy (.attribute name) state
            (evaluate policy env fuel attr.expression))
            (evaluate policy env fuel fallback)
        else ⟨.value [.string attr.text], state⟩
    | .primitive name fallback =>
      match env.attributes name with
      | none => evaluate policy env fuel fallback state
      | some attr =>
        match attr.primitive with
        | none => evaluate policy env fuel fallback state
        | some tokens => ⟨.value tokens, state⟩
    | .typed name fallback =>
      match env.attributes name with
      | none => evaluate policy env fuel fallback state
      | some attr =>
        orElse (parseTyped (env.accepts name)
          (guarded policy (.attribute name) state
            (evaluate policy env fuel attr.expression)))
          (evaluate policy env fuel fallback)
    | .append left right =>
      let first := evaluate policy env fuel left state
      match first.outcome with
      | .value tokens =>
        let second := evaluate policy env fuel right first.state
        match second.outcome with
        | .value more => ⟨.value (tokens ++ more), second.state⟩
        | _ => second
      | _ => first

def property (policy : Policy) (env : Environment) (fuel name : Nat)
    (state : State := {}) : Result :=
  guarded policy (.property name) state (evaluate policy env fuel (env.properties name))

theorem participants_exact (key : Key) (front suffix : List Key)
    (fresh : key ∉ front) :
    participants key (front ++ key :: suffix) = front ++ [key] := by
  induction front with
  | nil => simp [participants]
  | cons first rest ih =>
    have different : first ≠ key := by
      intro equal
      apply fresh
      simp [equal]
    have absent : key ∉ rest := by
      intro present
      exact fresh (List.mem_cons_of_mem first present)
    simp [participants, different, ih absent]

theorem finish_poisoned (key : Key) (value : Outcome) (state : State)
    (marked : key ∈ state.poisoned) : finish true key value state = .invalid := by
  simp [finish, marked]

theorem finish_unpoisoned (key : Key) (value : Outcome) (state : State)
    (clear : key ∉ state.poisoned) : finish true key value state = value := by
  simp [finish, clear]

theorem guard_marks_exact_cycle (key : Key) (front suffix : List Key)
    (state : State) (body : State → Result) (fresh : key ∉ front)
    (stack : state.active = front ++ key :: suffix) :
    (guarded {} key state body).state.poisoned =
      (front ++ [key]) ++ state.poisoned := by
  simp [guarded, stack, participants_exact key front suffix fresh]

theorem guard_reentry_invalid (policy : Policy) (key : Key) (state : State)
    (body : State → Result) (active : key ∈ state.active) :
    (guarded policy key state body).outcome = .invalid := by
  simp [guarded, active]

theorem guard_final_check (key : Key) (state : State) (body : State → Result)
    (fresh : key ∉ state.active)
    (marked : key ∈ (body { state with active := key :: state.active, guardTrace := state.guardTrace ++ [key] }).state.poisoned) :
    (guarded {} key state body).outcome = .invalid := by
  simp [guarded, fresh, finish, marked]

theorem guard_restores_stack (policy : Policy) (key : Key) (state : State)
    (body : State → Result) : (guarded policy key state body).state.active = state.active := by
  simp only [guarded]
  split <;> rfl

theorem value_excludes_fallback (tokens : List Token) (state : State)
    (fallback : State → Result) :
    orElse ⟨.value tokens, state⟩ fallback = ⟨.value tokens, state⟩ := rfl

theorem exhaustion_not_invalid (state : State) (fallback : State → Result) :
    orElse ⟨.exhausted, state⟩ fallback = ⟨.exhausted, state⟩ := rfl

theorem present_raw_is_literal (env : Environment) (fuel name : Nat)
    (attr : Attribute) (fallback : Expr) (state : State)
    (present : env.attributes name = some attr) :
    evaluate {} env (fuel + 1) (.raw name fallback) state =
      ⟨.value [.string attr.text], state⟩ := by
  simp [evaluate, present]

theorem valid_primitive_ignores_expression (env : Environment) (fuel name : Nat)
    (attr : Attribute) (fallback : Expr) (tokens : List Token) (state : State)
    (present : env.attributes name = some attr) (valid : attr.primitive = some tokens) :
    evaluate {} env (fuel + 1) (.primitive name fallback) state =
      ⟨.value tokens, state⟩ := by
  simp [evaluate, present, valid]

theorem missing_raw_uses_fallback (env : Environment) (fuel name : Nat)
    (fallback : Expr) (state : State) (missing : env.attributes name = none) :
    evaluate {} env (fuel + 1) (.raw name fallback) state =
      evaluate {} env fuel fallback state := by
  simp [evaluate, missing]

theorem invalid_primitive_uses_fallback (env : Environment) (fuel name : Nat)
    (attr : Attribute) (fallback : Expr) (state : State)
    (present : env.attributes name = some attr) (invalid : attr.primitive = none) :
    evaluate {} env (fuel + 1) (.primitive name fallback) state =
      evaluate {} env fuel fallback state := by
  simp [evaluate, present, invalid]

end AttributeGuard
