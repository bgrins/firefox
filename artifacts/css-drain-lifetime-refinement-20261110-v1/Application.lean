import Entry

namespace EndpointApplication

structure Version where
  generation : Nat
  value : Nat
  deriving DecidableEq, Repr

structure State where
  endpoint : Version
  installed : Version
  queue : List Version
  deriving DecidableEq, Repr

def valid (s : State) : Prop :=
  s.installed.generation ≤ s.endpoint.generation ∧
  (∀ r ∈ s.queue, r.generation ≤ s.endpoint.generation ∧
    (r.generation = s.endpoint.generation → r = s.endpoint)) ∧
  (s.installed = s.endpoint ∨ s.endpoint ∈ s.queue)

def ready (s : State) : Prop := s.queue = [] ∧ s.installed = s.endpoint

instance (s : State) : Decidable (ready s) :=
  inferInstanceAs (Decidable (s.queue = [] ∧ s.installed = s.endpoint))

def initial (value : Nat) : State := ⟨⟨0, value⟩, ⟨0, value⟩, []⟩

def refresh (value : Nat) (s : State) : State :=
  if value = s.endpoint.value then s else
  let next := Version.mk (s.endpoint.generation + 1) value
  ⟨next, s.installed, s.queue ++ [next]⟩

def apply (endpoint installed job : Version) : Version :=
  if job.generation = endpoint.generation then job else installed

def dispatch (s : State) : State :=
  match s.queue with
  | [] => s
  | job :: rest => ⟨s.endpoint, apply s.endpoint s.installed job, rest⟩

def drainValues (endpoint installed : Version) : List Version → Version
  | [] => installed
  | job :: rest => drainValues endpoint (apply endpoint installed job) rest

def drain (s : State) : State :=
  ⟨s.endpoint, drainValues s.endpoint s.installed s.queue, []⟩

theorem initial_valid (value : Nat) : valid (initial value) := by
  simp [valid, initial]

theorem refresh_valid (s : State) (value : Nat) (h : valid s) :
    valid (refresh value s) := by
  rcases h with ⟨installed, jobs, covered⟩
  by_cases unchanged : value = s.endpoint.value
  · simpa [refresh, unchanged, valid] using And.intro installed (And.intro jobs covered)
  · simp only [refresh, unchanged, ↓reduceIte, valid]
    refine ⟨by omega, ?_, Or.inr ?_⟩
    · intro r member
      simp only [List.mem_append, List.mem_singleton] at member
      rcases member with old | rfl
      · have previous := (jobs r old).1
        exact ⟨by omega, by intro impossible; omega⟩
      · exact ⟨Nat.le_refl _, fun _ => rfl⟩
    · simp

theorem stale_job_preserves_installation (endpoint installed job : Version)
    (stale : job.generation < endpoint.generation) :
    apply endpoint installed job = installed := by
  simp [apply, Nat.ne_of_lt stale]

theorem dispatch_valid (s : State) (h : valid s) : valid (dispatch s) := by
  rcases s with ⟨endpoint, installed, queue⟩
  cases queue with
  | nil => exact h
  | cons job rest =>
    rcases h with ⟨bounded, jobs, covered⟩
    have jobValid := jobs job (by simp)
    have restValid : ∀ r ∈ rest, r.generation ≤ endpoint.generation ∧
        (r.generation = endpoint.generation → r = endpoint) := by
      intro r member
      exact jobs r (by simp [member])
    by_cases current : job.generation = endpoint.generation
    · have same := jobValid.2 current
      simp only [dispatch, apply, current, ↓reduceIte, valid]
      exact ⟨by omega, restValid, Or.inl same⟩
    · simp only [dispatch, apply, current, ↓reduceIte, valid]
      refine ⟨bounded, restValid, ?_⟩
      rcases covered with already | pending
      · exact Or.inl already
      · simp only [List.mem_cons] at pending
        rcases pending with same | tail
        · exact False.elim (current (congrArg Version.generation same.symm))
        · exact Or.inr tail

theorem dispatch_decreases (s : State) (work : s.queue ≠ []) :
    (dispatch s).queue.length + 1 = s.queue.length := by
  cases s with
  | mk endpoint installed queue =>
    cases queue with
    | nil => contradiction
    | cons job rest => rfl

theorem drain_installs_current (endpoint installed : Version) (queue : List Version)
    (jobs : ∀ r ∈ queue, r.generation = endpoint.generation → r = endpoint)
    (covered : installed = endpoint ∨ endpoint ∈ queue) :
    drainValues endpoint installed queue = endpoint := by
  induction queue generalizing installed with
  | nil => simpa [drainValues] using covered
  | cons job rest ih =>
    simp only [drainValues]
    apply ih
    · intro r member
      exact jobs r (by simp [member])
    · by_cases current : job.generation = endpoint.generation
      · exact Or.inl (by simpa [apply, current] using jobs job (by simp) current)
      · simp only [apply, current, ↓reduceIte]
        rcases covered with already | pending
        · exact Or.inl already
        · simp only [List.mem_cons] at pending
          rcases pending with same | tail
          · exact False.elim (current (congrArg Version.generation same.symm))
          · exact Or.inr tail

theorem stable_drain_ready (s : State) (h : valid s) : ready (drain s) := by
  exact ⟨rfl, drain_installs_current s.endpoint s.installed s.queue
    (fun r member => (h.2.1 r member).2) h.2.2⟩

theorem drain_valid (s : State) (h : valid s) : valid (drain s) := by
  have installed := (stable_drain_ready s h).2
  change drainValues s.endpoint s.installed s.queue = s.endpoint at installed
  simp [valid, drain, installed]

inductive Action where
  | refresh (value : Nat)
  | dispatch
  | drain

def step (action : Action) (s : State) : State :=
  match action with
  | .refresh value => refresh value s
  | .dispatch => dispatch s
  | .drain => drain s

def run (actions : List Action) (s : State) : State :=
  actions.foldl (fun state action => step action state) s

theorem step_valid (s : State) (action : Action) (h : valid s) : valid (step action s) := by
  cases action with
  | refresh value => exact refresh_valid s value h
  | dispatch => exact dispatch_valid s h
  | drain => exact drain_valid s h

theorem history_valid (actions : List Action) (s : State) (h : valid s) :
    valid (run actions s) := by
  induction actions generalizing s with
  | nil => exact h
  | cons action rest ih => exact ih (step action s) (step_valid s action h)

def pass (next : Option Nat) (s : State) : State :=
  match next with
  | none => drain s
  | some value => refresh value (drain s)

def passes (changes : List (Option Nat)) (s : State) : State :=
  changes.foldl (fun state next => pass next state) s

theorem passes_valid (changes : List (Option Nat)) (s : State) (h : valid s) :
    valid (passes changes s) := by
  induction changes generalizing s with
  | nil => exact h
  | cons next rest ih =>
    apply ih
    cases next with
    | none => exact drain_valid s h
    | some value => exact refresh_valid (drain s) value (drain_valid s h)

theorem finite_changes_then_quiescent_pass_ready (changes : List (Option Nat))
    (s : State) (h : valid s) : ready (pass none (passes changes s)) := by
  exact stable_drain_ready _ (passes_valid changes s h)

def twoPasses : State := passes [some 46, some 64] (initial 46)

theorem two_pass_counterexample :
    valid twoPasses ∧ twoPasses.endpoint.value = 64 ∧
    twoPasses.installed.value = 46 ∧ twoPasses.queue = [⟨1, 64⟩] ∧ ¬ready twoPasses := by
  refine ⟨passes_valid _ _ (initial_valid _), ?_⟩
  decide +kernel

theorem normal_route_is_insufficient :
    (CancellationRoute.run CancellationRoute.forwardAll CancellationRoute.deepRoute.length
      (CancellationEntry.enter
        (CancellationEntry.reserveNormal true CancellationEntry.observed)
        CancellationRoute.deepRoute)).visited = CancellationRoute.deepRoute ∧
    ¬ready twoPasses := by
  exact ⟨CancellationEntry.reserved_route_control, two_pass_counterexample.2.2.2.2⟩

theorem stable_third_pass_control :
    ready (pass none twoPasses) ∧ (pass none twoPasses).installed.value = 64 := by
  decide +kernel

def staleThenCurrent : State := refresh 64 (refresh 48 (initial 46))

theorem stale_reply_then_current_control :
    (dispatch staleThenCurrent).installed.value = 46 ∧
    ready (dispatch (dispatch staleThenCurrent)) ∧
    (dispatch (dispatch staleThenCurrent)).installed.value = 64 := by
  decide +kernel

end EndpointApplication
