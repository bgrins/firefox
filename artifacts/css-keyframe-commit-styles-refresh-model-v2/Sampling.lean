import Context

namespace KeyframeSampling
open KeyframeContext

structure Effects where
  providerStart : Rat
  providerFinish : Rat
  consumerStart : Expression
  consumerFinish : Expression

structure Sample where
  providerProgress : Rat
  consumerProgress : Rat

def providerValue (effects : Effects) (sample : Sample) : Rat :=
  interpolate effects.providerStart effects.providerFinish sample.providerProgress

def consumerValue (effects : Effects) (sample : Sample) : Rat :=
  let context := providerValue effects sample
  interpolate (evaluate context effects.consumerStart)
    (evaluate context effects.consumerFinish) sample.consumerProgress

structure State where
  provider : Rat
  consumer : Rat
  providerReady : Bool := false
  consumerReady : Bool := false

inductive Task where
  | provider
  | consumer
  deriving DecidableEq

def step (effects : Effects) (sample : Sample) (state : State) : Task → State
  | .provider => { state with provider := providerValue effects sample, providerReady := true }
  | .consumer => { state with
      consumer := interpolate (evaluate state.provider effects.consumerStart)
        (evaluate state.provider effects.consumerFinish) sample.consumerProgress
      consumerReady := true }

def run (effects : Effects) (sample : Sample) : State → List Task → State
  | state, [] => state
  | state, task :: rest => run effects sample (step effects sample state task) rest

def ordered : Bool → List Task → Bool
  | _, [] => true
  | _, .provider :: rest => ordered true rest
  | ready, .consumer :: rest => ready && ordered ready rest

def Current (effects : Effects) (sample : Sample) (state : State) : Prop :=
  (state.providerReady = true → state.provider = providerValue effects sample) ∧
  (state.consumerReady = true → state.consumer = consumerValue effects sample)

theorem run_preserves_current (effects : Effects) (sample : Sample) (tasks : List Task)
    (state : State) (valid : Current effects sample state)
    (order : ordered state.providerReady tasks = true) :
    Current effects sample (run effects sample state tasks) := by
  induction tasks generalizing state with
  | nil => exact valid
  | cons task rest ih =>
    cases task with
    | provider =>
      apply ih
      · exact ⟨fun _ => rfl, valid.2⟩
      · exact order
    | consumer =>
      have ready : state.providerReady = true := (Bool.and_eq_true_iff.mp order).1
      apply ih
      · constructor
        · exact valid.1
        · intro _
          simp only [step, consumerValue, valid.1 ready]
      · exact (Bool.and_eq_true_iff.mp order).2

theorem run_consumer_ready (effects : Effects) (sample : Sample) (tasks : List Task)
    (state : State) (present : Task.consumer ∈ tasks) :
    (run effects sample state tasks).consumerReady = true := by
  have preserve : ∀ (tasks : List Task) (state : State), state.consumerReady = true →
      (run effects sample state tasks).consumerReady = true := by
    intro tasks
    induction tasks with
    | nil => intro state h; exact h
    | cons task rest ih =>
      intro state h
      cases task <;> apply ih <;> simp [step, h]
  induction tasks generalizing state with
  | nil => simp at present
  | cons task rest ih =>
    rcases List.mem_cons.mp present with first | later
    · subst task
      exact preserve rest (step effects sample state .consumer) rfl
    · exact ih (step effects sample state task) later

def beginSample (state : State) : State :=
  { state with providerReady := false, consumerReady := false }

theorem ordered_sample_correct (effects : Effects) (sample : Sample) (tasks : List Task)
    (state : State) (order : ordered false tasks = true)
    (present : Task.consumer ∈ tasks) :
    (run effects sample (beginSample state) tasks).consumer = consumerValue effects sample := by
  have initial : Current effects sample (beginSample state) := by simp [Current, beginSample]
  exact (run_preserves_current effects sample tasks (beginSample state) initial order).2
    (run_consumer_ready effects sample tasks (beginSample state) present)

def tick (effects : Effects) (sample : Sample) (state : State) : State :=
  run effects sample (beginSample state) [.provider, .consumer]

def history (effects : Effects) : State → List Sample → List Rat
  | _, [] => []
  | state, sample :: rest =>
    let updated := tick effects sample state
    updated.consumer :: history effects updated rest

theorem history_correct (effects : Effects) (samples : List Sample) (state : State) :
    history effects state samples = samples.map (consumerValue effects) := by
  induction samples generalizing state with
  | nil => rfl
  | cons sample rest ih =>
    have correct := ordered_sample_correct effects sample [.provider, .consumer] state rfl (by simp)
    simpa only [history, List.map_cons, tick, correct] using
      congrArg (List.cons (consumerValue effects sample)) (ih (tick effects sample state))

def staleTick (effects : Effects) (sample : Sample) (state : State) : State :=
  step effects sample (beginSample state) .consumer

def witness : Effects := ⟨200, 300, .literal 100, .provider⟩
def first : Sample := ⟨1/4, 1/4⟩
def changed : Sample := ⟨3/4, 1/4⟩
def seed : State := ⟨0, 0, false, false⟩
def retained : State := tick witness first seed

theorem stale_provider_counterexample :
    (staleTick witness changed retained).consumer ≠ consumerValue witness changed := by
  decide +kernel

example : history witness seed [first, ⟨1/4, 3/4⟩, changed, ⟨3/4, 3/4⟩] =
    [525/4, 775/4, 575/4, 925/4] := by decide +kernel
example : (staleTick witness changed retained).consumer = 525/4 := by decide +kernel
example : ordered false [.consumer, .provider] = false := by decide +kernel
example : ordered false [.provider, .provider, .consumer, .provider, .consumer] = true := by decide +kernel

end KeyframeSampling
