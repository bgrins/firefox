import FontDemand

namespace RootFontProvider

open FontConsumerDemand

structure Metrics where
  font : FontState
  lineHeight : Nat
  deriving DecidableEq, Repr

inductive RootUnit where
  | rem | rlh
  deriving DecidableEq, Repr

inductive Target where
  | root | child | rootPseudo
  deriving DecidableEq, Repr

inductive Property where
  | fontSize | lineHeight | other
  deriving DecidableEq, Repr

inductive Base where
  | initial | root
  deriving DecidableEq, Repr

def selected : Target → Property → RootUnit → Base
  | .root, .fontSize, _ => .initial
  | .root, .lineHeight, .rlh => .initial
  | _, _, _ => .root

inductive Observation where
  | font (inputs : Inputs)
  | line (value : Nat)
  deriving DecidableEq, Repr

def observe (metrics : Metrics) : RootUnit → Observation
  | .rem => .font (reads metrics.font .em)
  | .rlh => .line metrics.lineHeight

structure Record where
  revision : Nat
  value : Metrics
  deriving DecidableEq, Repr

structure State where
  revision : Nat
  desired : Metrics
  cache : Option Record
  job : Option Record
  deriving DecidableEq, Repr

def Coherent (s : State) (r : Record) : Prop :=
  r.revision ≤ s.revision ∧ (r.revision = s.revision → r.value = s.desired)

def Valid (s : State) : Prop :=
  (∀ r, s.cache = some r → Coherent s r) ∧
  (∀ r, s.job = some r → Coherent s r)

def initial (m : Metrics) : State := ⟨0, m, some ⟨0, m⟩, none⟩

def invalidate (s : State) (m : Metrics) : State :=
  { s with revision := s.revision + 1, desired := m }

def begin (s : State) : State :=
  match s.job with
  | some _ => s
  | none => { s with job := some ⟨s.revision, s.desired⟩ }

def finish (s : State) : State :=
  match s.job with
  | none => s
  | some r =>
    if r.revision = s.revision then { s with cache := some r, job := none }
    else { s with job := none }

inductive Action where
  | invalidate (value : Metrics)
  | begin | finish
  deriving DecidableEq, Repr

def step (s : State) : Action → State
  | .invalidate m => invalidate s m
  | .begin => begin s
  | .finish => finish s

def run : State → List Action → State
  | s, [] => s
  | s, a :: rest => run (step s a) rest

def provider (s : State) : Option Metrics :=
  s.cache.bind fun r => if r.revision = s.revision then some r.value else none

def read (initialMetrics : Metrics) (s : State) (target : Target)
    (property : Property) (unit : RootUnit) : Option Observation :=
  match selected target property unit with
  | .initial => some (observe initialMetrics unit)
  | .root => (provider s).map fun m => observe m unit

def expected (initialMetrics : Metrics) (s : State) (target : Target)
    (property : Property) (unit : RootUnit) : Observation :=
  observe (if selected target property unit = .initial then initialMetrics else s.desired) unit

theorem initial_valid (m : Metrics) : Valid (initial m) := by
  simp [Valid, initial, Coherent]

theorem invalidate_valid {s : State} (h : Valid s) (m : Metrics) :
    Valid (invalidate s m) := by
  have lift : ∀ r, Coherent s r → Coherent (invalidate s m) r := by
    intro r hr
    constructor
    · simp only [invalidate]; omega
    · intro eq
      simp only [invalidate] at eq
      have := hr.1
      omega
  exact ⟨fun r eq => lift r (h.1 r eq), fun r eq => lift r (h.2 r eq)⟩

theorem begin_valid {s : State} (h : Valid s) : Valid (begin s) := by
  cases eq : s.job with
  | some r => simpa [begin, eq] using h
  | none =>
    constructor
    · simpa [begin, eq, Coherent] using h.1
    · intro r hr
      simp [begin, eq] at hr
      cases hr
      simp [Coherent, begin, eq]

theorem finish_valid {s : State} (h : Valid s) : Valid (finish s) := by
  cases eq : s.job with
  | none => simpa [finish, eq] using h
  | some r =>
    by_cases current : r.revision = s.revision
    · constructor
      · intro v hv
        simp [finish, eq, current] at hv
        cases hv
        simpa [Coherent, finish, eq, current] using h.2 r eq
      · simp [finish, eq, current]
    · constructor
      · simpa [Coherent, finish, eq, current] using h.1
      · simp [finish, eq, current]

theorem step_valid {s : State} (h : Valid s) (a : Action) : Valid (step s a) := by
  cases a with
  | invalidate m => exact invalidate_valid h m
  | begin => exact begin_valid h
  | finish => exact finish_valid h

theorem run_valid {s : State} (h : Valid s) (actions : List Action) :
    Valid (run s actions) := by
  induction actions generalizing s with
  | nil => exact h
  | cons a rest ih => exact ih (step_valid h a)

theorem provider_current {s : State} (h : Valid s) {value : Metrics}
    (got : provider s = some value) : value = s.desired := by
  obtain ⟨r, stored, result⟩ := Option.bind_eq_some_iff.mp got
  split at result
  next eq =>
    simp only [Option.some.injEq] at result
    subst value
    exact (h.1 r stored).2 eq
  next => contradiction

theorem history_read_sound (m initialMetrics : Metrics) (actions : List Action)
    (target : Target) (property : Property) (unit : RootUnit) (value : Observation)
    (got : read initialMetrics (run (initial m) actions) target property unit = some value) :
    value = expected initialMetrics (run (initial m) actions) target property unit := by
  have valid := run_valid (initial_valid m) actions
  cases base : selected target property unit with
  | initial => simpa [read, base, expected] using got.symm
  | root =>
    simp only [read, base] at got
    obtain ⟨v, known, output⟩ := Option.map_eq_some_iff.mp got
    have := provider_current valid known
    simp [expected, base, ← output, this]

theorem stale_finish_no_publication (s : State) (r : Record)
    (job : s.job = some r) (stale : r.revision ≠ s.revision) :
    (finish s).cache = s.cache ∧ (finish s).job = none := by
  simp [finish, job, stale]

theorem cancellation_dirties_provider {s : State} (h : Valid s) (m : Metrics) :
    provider (invalidate s m) = none := by
  cases eq : s.cache with
  | none => simp [provider, invalidate, eq]
  | some r =>
    have bound := (h.1 r eq).1
    have ne : r.revision ≠ s.revision + 1 := by omega
    simp [provider, invalidate, eq, ne]

theorem finish_begin_current (s : State) (idle : s.job = none) :
    provider (finish (begin s)) = some s.desired := by
  simp [provider, finish, begin, idle]

theorem discard_then_refresh (s : State) (r : Record)
    (job : s.job = some r) (stale : r.revision ≠ s.revision) :
    provider (finish (begin (finish s))) = some s.desired := by
  simp [provider, finish, begin, job, stale]

theorem root_font_independent (i : Metrics) (s t : State) (unit : RootUnit) :
    read i s .root .fontSize unit = read i t .root .fontSize unit := by
  cases unit <;> rfl

theorem root_line_rem_uses_root (i : Metrics) (s : State) :
    read i s .root .lineHeight .rem = (provider s).map (fun m => observe m .rem) := rfl

theorem pseudo_requires_current (i : Metrics) (s : State) (unit : RootUnit)
    (dirty : provider s = none) : read i s .rootPseudo .fontSize unit = none := by
  cases unit <;> simp [read, selected, dirty]

def initialMetrics : Metrics := ⟨⟨16, 0, false⟩, 19⟩
def underlying : Metrics := ⟨⟨23, 0, false⟩, 37⟩
def animated : Metrics := ⟨⟨32, 0, false⟩, 37⟩
def dirty : State := invalidate (initial animated) underlying
def staleJob : State := invalidate (begin { initial animated with job := none }) underlying

theorem identity_and_freshness_independent :
    read initialMetrics dirty .root .fontSize .rem = some (.font (.size 16)) ∧
    read initialMetrics dirty .child .fontSize .rem = none ∧
    read initialMetrics (finish (begin dirty)) .child .fontSize .rem = some (.font (.size 23)) ∧
    read initialMetrics (finish (begin dirty)) .root .fontSize .rem = some (.font (.size 16)) := by
  decide

end RootFontProvider
