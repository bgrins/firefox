import CssSemantics.TransitionMachine

namespace CssSemantics.ProviderObservation

variable {State Target Observation View Mutation : Type}

def query (admitted : State → Target → Bool)
    (force : State → Target → Option State)
    (observe : State → Target → Option Observation)
    (world : State) (target : Target) : Option (State × Observation) :=
  (if admitted world target then force world target else some world).bind fun after =>
    (observe after target).map fun value => (after, value)

theorem successful_observation (admitted : State → Target → Bool)
    (force : State → Target → Option State) (observe : State → Target → Option Observation)
    (world after : State) (target : Target) (value : Observation)
    (success : query admitted force observe world target = some (after, value)) :
    observe after target = some value := by
  simp only [query, Option.bind_eq_some_iff, Option.map_eq_some_iff] at success
  obtain ⟨next, _, observed, read, same⟩ := success
  obtain ⟨rfl, rfl⟩ := Prod.mk.inj same
  exact read

theorem successful_state (admitted : State → Target → Bool)
    (force : State → Target → Option State) (observe : State → Target → Option Observation)
    (world after : State) (target : Target) (value : Observation)
    (success : query admitted force observe world target = some (after, value)) :
    (if admitted world target then force world target else some world) = some after := by
  simp only [query, Option.bind_eq_some_iff, Option.map_eq_some_iff] at success
  obtain ⟨next, supplied, observed, _, same⟩ := success
  obtain ⟨rfl, rfl⟩ := Prod.mk.inj same
  exact supplied

def eraseResult (erase : Observation → View) (result : State × Observation) : State × View :=
  (result.1, erase result.2)

theorem query_erase (admitted : State → Target → Bool)
    (force : State → Target → Option State) (observe : State → Target → Option Observation)
    (erase : Observation → View) (world : State) (target : Target) :
    query admitted force (fun s t => (observe s t).map erase) world target =
      (query admitted force observe world target).map (eraseResult erase) := by
  cases step : (if admitted world target then force world target else some world) with
  | none => simp [query, step]
  | some after => simp [query, step, Option.map_map, eraseResult, Function.comp_def]

structure Session (State Target Observation : Type) where
  world : State
  log : List (Target × Observation)
  deriving DecidableEq, Repr

inductive Event (Mutation Target : Type) where
  | mutate (mutation : Mutation)
  | query (target : Target)
  deriving DecidableEq, Repr

def eraseSession (erase : Observation → View) (session : Session State Target Observation) :
    Session State Target View :=
  ⟨session.world, session.log.map fun item => (item.1, erase item.2)⟩

def advance (mutate : State → Mutation → Option State)
    (admitted : State → Target → Bool) (force : State → Target → Option State)
    (observe : State → Target → Option Observation)
    (session : Session State Target Observation) (event : Event Mutation Target) :
    Option (Session State Target Observation) :=
  match event with
  | .mutate token => (mutate session.world token).map fun after => ⟨after, session.log⟩
  | .query target => (query admitted force observe session.world target).map fun result =>
      ⟨result.1, session.log ++ [(target, result.2)]⟩

theorem advance_erase (mutate : State → Mutation → Option State)
    (admitted : State → Target → Bool) (force : State → Target → Option State)
    (observe : State → Target → Option Observation) (erase : Observation → View)
    (session : Session State Target Observation) (event : Event Mutation Target) :
    advance mutate admitted force (fun s t => (observe s t).map erase)
        (eraseSession erase session) event =
      (advance mutate admitted force observe session event).map (eraseSession erase) := by
  cases event with
  | mutate token =>
      cases step : mutate session.world token <;> simp [advance, eraseSession, step]
  | query target =>
      simp only [advance, eraseSession]
      rw [query_erase]
      simp [Option.map_map, eraseResult, eraseSession, Function.comp_def]

theorem history_erase (mutate : State → Mutation → Option State)
    (admitted : State → Target → Bool) (force : State → Target → Option State)
    (observe : State → Target → Option Observation) (erase : Observation → View)
    (events : List (Event Mutation Target)) (session : Session State Target Observation) :
    TransitionMachine.run (advance mutate admitted force (fun s t => (observe s t).map erase))
        (eraseSession erase session) events =
      (TransitionMachine.run (advance mutate admitted force observe) session events).map
        (eraseSession erase) := by
  induction events generalizing session with
  | nil => rfl
  | cons event rest ih =>
      simp only [TransitionMachine.run]
      rw [advance_erase]
      cases step : advance mutate admitted force observe session event with
      | none => simp
      | some next => simp [ih]

end CssSemantics.ProviderObservation
