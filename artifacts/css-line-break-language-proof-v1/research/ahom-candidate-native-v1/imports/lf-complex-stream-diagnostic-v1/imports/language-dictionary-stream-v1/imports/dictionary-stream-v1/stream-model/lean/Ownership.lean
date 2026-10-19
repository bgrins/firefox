import Std

namespace HyphenOwnership

structure Limits where
  word : Nat
  before : Nat
  after : Nat
  deriving DecidableEq, Repr

def resolve (word before after : Option Nat) : Limits :=
  let b := before.getD 2
  let a := after.getD 2
  ⟨max (word.getD 5) (b + a), b, a⟩

def saturate (l : Limits) : Limits :=
  ⟨min 255 l.word, min 255 l.before, min 255 l.after⟩

theorem resolved_total (w b a : Option Nat) :
    (resolve w b a).before + (resolve w b a).after ≤ (resolve w b a).word := by
  exact Nat.le_max_right _ _

theorem saturation_exact (l : Limits) (w : l.word ≤ 255)
    (b : l.before ≤ 255) (a : l.after ≤ 255) : saturate l = l := by
  cases l
  simp_all [saturate, Nat.min_eq_right]

theorem resolved_component_bounds (w b a : Option Nat) :
    (resolve w b a).before ≤ (resolve w b a).word ∧
      (resolve w b a).after ≤ (resolve w b a).word := by
  have := resolved_total w b a
  omega

theorem saturated_component_bounds (l : Limits)
    (hb : l.before ≤ l.word) (ha : l.after ≤ l.word) :
    (saturate l).before ≤ (saturate l).word ∧
      (saturate l).after ≤ (saturate l).word := by
  simp only [saturate]
  omega

theorem native_style_sum_does_not_overflow (b a : Nat)
    (hb : b ≤ 2147483647) (ha : a ≤ 2147483647) : b + a < 4294967296 := by
  omega

theorem native_end_guard_no_underflow (l : Limits) (units : Nat)
    (ha : l.after ≤ l.word) (wordGuard : l.word ≤ units) (nonempty : 0 < units) :
    max 1 l.after ≤ units := by omega

structure Character where
  unit : Nat
  node : Nat
  original : Nat
  transformed : Nat
  sink : Nat
  sinkOffset : Nat
  limits : Limits
  language : Option Nat
  automatic : Bool
  suppress : Bool
  deriving DecidableEq, Repr

structure Word where
  characters : List Character
  owner : Option Limits
  deriving DecidableEq, Repr

structure State where
  current : Limits
  pending : List Character
  captured : Option Limits
  completed : List Word
  finalized : List Nat
  deriving DecidableEq, Repr

inductive Event where
  | setLimits (limits : Limits)
  | contribute (character : Character)
  | boundary
  | invisibleWhitespace
  | finalize (sink : Nat)
  deriving DecidableEq, Repr

def flush (s : State) : State :=
  { s with pending := [], captured := none, completed := if s.pending.isEmpty then s.completed
      else s.completed ++ [⟨s.pending, s.captured⟩] }

def step (s : State) : Event → State
  | .setLimits l => {s with current := l}
  | .contribute c => {s with pending := c :: s.pending, captured := some (c.limits)}
  | .boundary => flush s
  | .invisibleWhitespace => flush s
  | .finalize sink => {s with finalized := s.finalized ++ [sink]}

def run (s : State) (events : List Event) := events.foldl step s

def owner (characters : List Character) : Option Limits :=
  characters.head?.map Character.limits

def coherent (s : State) : Prop := s.captured = owner s.pending

theorem step_coherent (s : State) (h : coherent s) (e : Event) :
    coherent (step s e) := by
  cases e <;> simp_all [coherent, step, flush, owner]

theorem run_coherent (s : State) (h : coherent s) (events : List Event) :
    coherent (run s events) := by
  induction events generalizing s with
  | nil => exact h
  | cons e es ih => exact ih (step s e) (step_coherent s h e)

theorem partition_invariant (s : State) (a b : List Event) :
    run s (a ++ b) = run (run s a) b := by
  exact List.foldl_append

theorem arbitrary_partition (s : State) (chunks : List (List Event)) :
    chunks.foldl run s = run s chunks.flatten := by
  induction chunks generalizing s with
  | nil => rfl
  | cons c cs ih =>
    simp only [List.foldl_cons, List.flatten_cons]
    rw [ih, partition_invariant]

theorem setter_cannot_capture (s : State) (l : Limits) :
    (step s (.setLimits l)).captured = s.captured := rfl

theorem boundary_uses_pending (s : State) (l : Limits) :
    (flush (step s (.setLimits l))).completed = (flush s).completed := rfl

theorem invisible_uses_pending (s : State) (l : Limits) :
    (step (step s (.setLimits l)) .invisibleWhitespace).completed =
      (flush s).completed := rfl

theorem nonempty_capture (s : State) (c : Character) :
    (step s (.contribute c)).captured = some c.limits := rfl

theorem uniform_owner (c : Character) (rest : List Character) (l : Limits)
    (h : ∀ x ∈ c :: rest, x.limits = l) : owner (c :: rest) = some l := by
  simp [owner, h c (by simp)]

def clampRange (bound start finish : Nat) : Nat × Nat :=
  (min start bound, min finish bound)

theorem clamped_range_order (bound start finish : Nat) (h : start ≤ finish) :
    (clampRange bound start finish).1 ≤ (clampRange bound start finish).2 := by
  simp only [clampRange]
  omega

theorem clamped_range_bounds (bound start finish : Nat) :
    (clampRange bound start finish).1 ≤ bound ∧
      (clampRange bound start finish).2 ≤ bound := by
  exact ⟨Nat.min_le_right _ _, Nat.min_le_right _ _⟩

theorem stale_range_empty (bound start finish : Nat)
    (hs : bound ≤ start) (he : bound ≤ finish) :
    clampRange bound start finish = (bound, bound) := by
  simp [clampRange, Nat.min_eq_right hs, Nat.min_eq_right he]

def project (source : List Character) (start count : Nat) :=
  (source.drop start).take count

theorem project_partition (source : List Character) (start a b : Nat) :
    project source start (a + b) =
      project source start a ++ project source (start + a) b := by
  simpa [project, List.drop_drop, Nat.add_comm] using
    (List.take_add (l := source.drop start) (i := a) (j := b))

inductive BreakKind where
  | none | normal | hyphen | emergency
  deriving DecidableEq, Repr

structure Position where
  utf16Index : Nat
  wordUnits : Nat
  prefixCount : Nat
  totalCount : Nat
  dictionary : Bool
  visited : Bool
  deriving DecidableEq, Repr

def preliminary (l : Limits) (p : Position) : Prop :=
  p.visited = true ∧ p.dictionary = true ∧ l.word ≤ p.wordUnits ∧
  l.before ≤ p.prefixCount ∧ p.utf16Index < p.wordUnits - max 1 l.after

instance (l : Limits) (p : Position) : Decidable (preliminary l p) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _))

def accepted (l : Limits) (p : Position) : Prop :=
  preliminary l p ∧ l.word ≤ p.totalCount ∧ l.after ≤ p.totalCount - p.prefixCount

instance (l : Limits) (p : Position) : Decidable (accepted l p) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _))

def speculative (l : Limits) (p : Position) (old : BreakKind) : BreakKind :=
  let written := if preliminary l p then BreakKind.hyphen else old
  if preliminary l p ∧ (p.totalCount < l.word ∨ p.totalCount - p.prefixCount < l.after)
  then old else written

def declarative (l : Limits) (p : Position) (old : BreakKind) : BreakKind :=
  if accepted l p then .hyphen else old

theorem filter_equivalence (l : Limits) (p : Position) (old : BreakKind) :
    speculative l p old = declarative l p old := by
  simp only [speculative, declarative, accepted]
  by_cases h : preliminary l p <;> by_cases hw : l.word ≤ p.totalCount <;>
    by_cases hs : l.after ≤ p.totalCount - p.prefixCount <;> simp_all <;> omega

theorem no_invented_break (l : Limits) (p : Position) (old : BreakKind)
    (h : speculative l p old ≠ old) :
    p.dictionary = true ∧ l.word ≤ p.totalCount ∧ l.before ≤ p.prefixCount ∧
      l.after ≤ p.totalCount - p.prefixCount := by
  rw [filter_equivalence] at h
  unfold declarative at h
  split at h
  next ha => exact ⟨ha.1.2.1, ha.2.1, ha.1.2.2.2.1, ha.2.2⟩
  next => exact False.elim (h rfl)

theorem rejected_restores (l : Limits) (p : Position) (old : BreakKind)
    (h : ¬ accepted l p) : speculative l p old = old := by
  rw [filter_equivalence]
  simp [declarative, h]

theorem write_index_bound (l : Limits) (p : Position) (h : preliminary l p) :
    p.utf16Index + 1 < p.wordUnits := by
  have := h.2.2.2.2
  have : 1 ≤ max 1 l.after := Nat.le_max_left _ _
  omega

def sinkWrite (clusterStart previousSpace : Bool) (old new : BreakKind) : BreakKind :=
  if new == .none || (!clusterStart && !previousSpace) then old else new

theorem zero_preserves (clusterStart previousSpace : Bool) (old : BreakKind) :
    sinkWrite clusterStart previousSpace old .none = old := by
  simp [sinkWrite]

theorem nonzero_replaces (old new : BreakKind) (h : new ≠ .none) :
    sinkWrite true false old new = new := by
  simp [sinkWrite, h]

theorem stale_hyphen_survives_zero : sinkWrite true false .hyphen .none = .hyphen := rfl

theorem emergency_kind_can_be_replaced :
    sinkWrite true false .emergency .normal = .normal := rfl

structure Cache where
  generation : Nat
  policyGeneration : Nat
  flags : List BreakKind
  deriving DecidableEq, Repr

def rebuild (generation : Nat) (computed : List BreakKind) : Cache :=
  ⟨generation, generation, computed⟩

def refresh (cache : Cache) (generation : Nat) (computed : List BreakKind) : Cache :=
  if cache.policyGeneration = generation then cache else rebuild generation computed

theorem invalidated_fresh (cache : Cache) (generation : Nat) (computed : List BreakKind)
    (h : cache.policyGeneration ≠ generation) :
    refresh cache generation computed = rebuild generation computed := by
  simp [refresh, h]

theorem finalization_kept_for_empty (s : State) (sink : Nat) :
    (step s (.finalize sink)).finalized = s.finalized ++ [sink] := rfl

def nativeStep (s : State) : Event → State
  | .contribute c => {s with pending := c :: s.pending, captured := some s.current}
  | e => step s e

def suppliedCorrectly (s : State) : Event → Prop
  | .contribute c => c.limits = s.current
  | _ => True

def admitted : State → List Event → Prop
  | _, [] => True
  | s, e :: rest => suppliedCorrectly s e ∧ admitted (step s e) rest

def nativeRun (s : State) (events : List Event) := events.foldl nativeStep s

theorem supplied_step_refinement (s : State) (e : Event)
    (h : suppliedCorrectly s e) : nativeStep s e = step s e := by
  cases e <;> simp_all [nativeStep, suppliedCorrectly, step]

theorem supplied_trace_refinement (s : State) (events : List Event)
    (h : admitted s events) : nativeRun s events = run s events := by
  induction events generalizing s with
  | nil => rfl
  | cons e rest ih =>
    change nativeRun (nativeStep s e) rest = run (step s e) rest
    rw [supplied_step_refinement s e h.1]
    exact ih (step s e) h.2

theorem native_capture_policy (s : State) (events : List Event)
    (h : coherent s) (hp : admitted s events) :
    coherent (nativeRun s events) := by
  rw [supplied_trace_refinement s events hp]
  exact run_coherent s h events

def flushFailure (s : State) (partialCallbacks : List Word) : State :=
  { s with pending := [], captured := none, completed := s.completed ++ partialCallbacks }

def effectiveCaptured (pending : List Character) (stored : Limits) : Option Limits :=
  if pending.isEmpty then none else some stored

theorem native_cleanup_forgets_stale_capture (stored : Limits) :
    effectiveCaptured [] stored = none := rfl

theorem native_nonempty_capture_is_visible (c : Character) (rest : List Character)
    (stored : Limits) : effectiveCaptured (c :: rest) stored = some stored := rfl

theorem failure_clears_pending (s : State) (callbacks : List Word) :
    (flushFailure s callbacks).pending = [] ∧
      (flushFailure s callbacks).captured = none := by
  exact ⟨rfl, rfl⟩

theorem uniform_native_owner (s : State) (events : List Event)
    (h : coherent s) (hp : admitted s events) (c : Character)
    (rest : List Character) (l : Limits)
    (pending : (nativeRun s events).pending = c :: rest)
    (uniform : ∀ x ∈ c :: rest, x.limits = l) :
    (nativeRun s events).captured = some l := by
  have hc := native_capture_policy s events h hp
  unfold coherent at hc
  rw [pending, uniform_owner c rest l uniform] at hc
  exact hc

#print axioms saturated_component_bounds
#print axioms native_style_sum_does_not_overflow
#print axioms native_end_guard_no_underflow
#print axioms supplied_trace_refinement
#print axioms native_capture_policy
#print axioms uniform_native_owner
#print axioms native_cleanup_forgets_stale_capture
#print axioms native_nonempty_capture_is_visible
#print axioms failure_clears_pending
#print axioms run_coherent
#print axioms arbitrary_partition
#print axioms uniform_owner
#print axioms project_partition
#print axioms filter_equivalence
#print axioms no_invented_break
#print axioms write_index_bound
#print axioms invalidated_fresh
end HyphenOwnership
