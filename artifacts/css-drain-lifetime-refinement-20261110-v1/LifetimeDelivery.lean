import Lifetime
import Accounting

namespace DrainLifetimeDelivery
open DrainLifetime
open CertifiedPath (Tree)

structure Metadata where
  pseudoType : Nat
  pseudoArgument : Nat
  level : LifetimeLedger.Level
  generation : Nat
  deriving DecidableEq, Repr

def key (c : Cell) (m : Metadata) : LifetimeLedger.Key :=
  ⟨c.lifetime, m.pseudoType, m.pseudoArgument, m.level, m.generation⟩

abbrev Ledgers := Nat → LifetimeLedger.State

def requestAdmission (target : Nat) (c : Cell) (m : Metadata) (ledgers : Ledgers) : Ledgers :=
  if c.present then ledgers else
    fun node => if node = target then LifetimeLedger.request (ledgers node) (key (ensure c) m)
                else ledgers node

def NoFuture (ledger : LifetimeLedger.State) (c : Cell) : Prop :=
  ∀ k, c.lifetime < k.lifetime → LifetimeLedger.Fresh ledger k

def complete (target : Nat) (done : LifetimeLedger.Key) (ledgers : Ledgers) : Ledgers :=
  fun node => if node = target then LifetimeLedger.install (ledgers node) (fun k => k == done)
              else ledgers node


theorem empty_no_future (c : Cell) : NoFuture LifetimeLedger.empty c := by
  intro k _
  simp [LifetimeLedger.Fresh, LifetimeLedger.empty]

theorem clear_preserves_no_future (ledger : LifetimeLedger.State) (c : Cell) (origin)
    (h : NoFuture ledger c) : NoFuture ledger (clear origin c) := by
  cases present : c.present <;> simpa [NoFuture, clear, present] using h

theorem ensure_preserves_no_future (ledger : LifetimeLedger.State) (c : Cell)
    (h : NoFuture ledger c) : NoFuture ledger (ensure c) := by
  intro k later
  apply h k
  cases present : c.present <;> simp [ensure, present] at later <;> omega

theorem request_at_current_preserves_no_future (ledger : LifetimeLedger.State)
    (c : Cell) (m : Metadata) (h : NoFuture ledger c) :
    NoFuture (LifetimeLedger.request ledger (key c m)) c := by
  intro k later
  have different : k ≠ key c m := by
    intro same
    have equal := congrArg LifetimeLedger.Key.lifetime same
    simp [key] at equal
    omega
  obtain ⟨required, installed, retired⟩ := h k later
  simp [LifetimeLedger.Fresh, LifetimeLedger.request, different, required, installed, retired]

theorem admission_preserves_no_future (target) (c : Cell) (m : Metadata)
    (ledgers : Ledgers) (h : NoFuture (ledgers target) c) :
    NoFuture (requestAdmission target c m ledgers target) (ensure c) := by
  cases present : c.present
  · simp only [requestAdmission, present, Bool.false_eq_true, ↓reduceIte]
    exact request_at_current_preserves_no_future _ _ _ (ensure_preserves_no_future _ _ h)
  · simpa [requestAdmission, ensure, present] using h

theorem recreated_key_fresh (c : Cell) (m : Metadata) (ledger : LifetimeLedger.State)
    (absent : c.present = false) (fresh : NoFuture ledger c) :
    LifetimeLedger.Fresh ledger (key (ensure c) m) := by
  apply fresh
  simp [key, ensure, absent]

theorem admission_requests_new_key (target) (c : Cell) (m : Metadata) (ledgers : Ledgers)
    (absent : c.present = false) :
    (requestAdmission target c m ledgers target).required (key (ensure c) m) = true := by
  simp [requestAdmission, absent, LifetimeLedger.request]

theorem admission_conserved (target) (c : Cell) (m : Metadata) (ledgers : Ledgers)
    (conserved : ∀ node, LifetimeLedger.Conserved (ledgers node)) :
    ∀ node, LifetimeLedger.Conserved (requestAdmission target c m ledgers node) := by
  intro node
  cases hp : c.present
  · simp only [requestAdmission, hp, Bool.false_eq_true, ↓reduceIte]
    split
    · exact LifetimeLedger.request_conserved _ _ (conserved node)
    · exact conserved node
  · simpa [requestAdmission, hp] using conserved node

theorem admission_unsettled (target) (c : Cell) (m : Metadata) (ledgers : Ledgers)
    (absent : c.present = false) (fresh : NoFuture (ledgers target) c) :
    LifetimeLedger.settled (requestAdmission target c m ledgers target) (key (ensure c) m) = false := by
  simp only [requestAdmission, absent, Bool.false_eq_true, ↓reduceIte]
  exact LifetimeLedger.fresh_request_unsettled _ _ (recreated_key_fresh c m _ absent fresh)

theorem different_key_completion_preserves (ledger : LifetimeLedger.State) (done observed : LifetimeLedger.Key)
    (different : observed ≠ done) :
    LifetimeLedger.settled (LifetimeLedger.install ledger (fun k => k == done)) observed =
      LifetimeLedger.settled ledger observed := by
  have neq : (observed == done) = false := by
    change decide (observed = done) = false
    simp [different]
  simp [LifetimeLedger.install, LifetimeLedger.settled, neq]

theorem different_identity_completion_preserves (doneTarget observedTarget : Nat)
    (done observed : LifetimeLedger.Key) (ledgers : Ledgers)
    (different : doneTarget ≠ observedTarget ∨ observed ≠ done) :
    LifetimeLedger.settled (complete doneTarget done ledgers observedTarget) observed =
      LifetimeLedger.settled (ledgers observedTarget) observed := by
  by_cases same : observedTarget = doneTarget
  · rcases different with otherTarget | otherKey
    · exact False.elim (otherTarget same.symm)
    · simpa [complete, same] using different_key_completion_preserves (ledgers doneTarget) done observed otherKey
  · simp [complete, same]

theorem new_lifetime_key_differs (c : Cell) (oldMeta newMeta : Metadata) (absent : c.present = false) :
    key (ensure c) newMeta ≠ key c oldMeta := by
  intro same
  have life := congrArg LifetimeLedger.Key.lifetime same
  simp [key, ensure, absent] at life

theorem old_completion_cannot_settle_recreated (target) (c : Cell) (oldMeta newMeta : Metadata)
    (ledgers : Ledgers) (absent : c.present = false) (fresh : NoFuture (ledgers target) c) :
    LifetimeLedger.settled
      (complete target (key c oldMeta) (requestAdmission target c newMeta ledgers) target)
      (key (ensure c) newMeta) = false := by
  rw [different_identity_completion_preserves target target (key c oldMeta) (key (ensure c) newMeta)
      (requestAdmission target c newMeta ledgers) (Or.inr (new_lifetime_key_differs c oldMeta newMeta absent))]
  exact admission_unsettled target c newMeta ledgers absent fresh

theorem normal_cell_is_admission_cell (target) (before : Model) :
    ensureAt target before.cells target = ensure (before.cells target) := by simp [ensureAt]

theorem ensure_existing_does_not_request (target) (c : Cell) (m : Metadata) (ledgers : Ledgers)
    (present : c.present = true) : requestAdmission target c m ledgers = ledgers := by simp [requestAdmission, present]

structure Joint where
  model : Model
  ledgers : Ledgers

def normalJoint (target : Nat) (m : Metadata) (before : Joint) (after : List Bool) : Joint :=
  ⟨⟨after, ensureAt target before.model.cells, before.model.clock + 1⟩,
    requestAdmission target (before.model.cells target) m before.ledgers⟩

def applicationJoint (t : Tree) (producer : Nat) (before : Joint) (after : List Bool) : Joint :=
  ⟨⟨after, clearDescendants t producer before.model.clock before.model.cells, before.model.clock + 1⟩,
    before.ledgers⟩

inductive JointStep (t : Tree) : Joint → Joint → Prop where
  | normal (target) (bound : target ≤ t.size) (m) (before : Joint) (after)
      (fire : Dispatch t (DescendingPhases.normal target) before.model.pending after) :
      JointStep t before (normalJoint target m before after)
  | application (producer) (bound : producer ≤ t.size) (before : Joint) (after)
      (fire : Dispatch t (DescendingPhases.application producer) before.model.pending after) :
      JointStep t before (applicationJoint t producer before after)

theorem joint_erases {t before after} (h : JointStep t before after) :
    DrainLifetime.Step t before.model after.model := by
  cases h with
  | normal target bound m before after fire => exact .normal target bound before.model after fire
  | application producer bound before after fire => exact .application producer bound before.model after fire

theorem joint_conserved {t before after} (h : JointStep t before after)
    (conserved : ∀ node, LifetimeLedger.Conserved (before.ledgers node)) :
    ∀ node, LifetimeLedger.Conserved (after.ledgers node) := by
  cases h with
  | normal target bound m before after fire => exact admission_conserved target _ m _ conserved
  | application producer bound before after fire => exact conserved


theorem joint_no_future {t before after} (step : JointStep t before after)
    (h : ∀ node, NoFuture (before.ledgers node) (before.model.cells node)) :
    ∀ node, NoFuture (after.ledgers node) (after.model.cells node) := by
  cases step with
  | normal target bound m before after fire =>
    intro node
    by_cases same : node = target
    · subst node
      simpa [normalJoint, ensureAt] using
        admission_preserves_no_future target (before.model.cells target) m before.ledgers (h target)
    · cases present : (before.model.cells target).present <;>
        simpa [normalJoint, ensureAt, requestAdmission, same, present] using h node
  | application producer bound before after fire =>
    intro node
    simp only [applicationJoint, clearDescendants]
    split
    · exact clear_preserves_no_future _ _ _ (h node)
    · exact h node

theorem clearing_does_not_discharge (t : Tree) (producer) (before : Joint) (after) :
    (applicationJoint t producer before after).ledgers = before.ledgers := rfl

theorem joint_normal_cause_and_request (t : Tree) (target) (m : Metadata) (before : Joint) (after)
    (valid : Valid (before.model.cells target))
    (causal : Causal t target (before.model.cells target))
    (absent : (before.model.cells target).present = false)
    (fresh : NoFuture (before.ledgers target) (before.model.cells target)) :
    ∃ o, ((normalJoint target m before after).model.cells target).admittedFrom = some o ∧
      ValidOrigin t target o ∧
      ((normalJoint target m before after).ledgers target).required
        (key ((normalJoint target m before after).model.cells target) m) = true ∧
      LifetimeLedger.settled ((normalJoint target m before after).ledgers target)
        (key ((normalJoint target m before after).model.cells target) m) = false := by
  obtain ⟨o, origin, validOrigin⟩ := ensure_causal_origin t target _ valid causal absent
  refine ⟨o, ?_, validOrigin, ?_, ?_⟩
  · simpa [normalJoint, ensureAt] using origin
  · simpa [normalJoint, ensureAt] using admission_requests_new_key target _ m before.ledgers absent
  · simpa [normalJoint, ensureAt] using admission_unsettled target _ m before.ledgers absent fresh

theorem joint_old_completion_isolated (target) (oldMeta newMeta : Metadata) (before : Joint) (after)
    (absent : (before.model.cells target).present = false)
    (fresh : NoFuture (before.ledgers target) (before.model.cells target)) :
    LifetimeLedger.settled
      (complete target (key (before.model.cells target) oldMeta)
        (normalJoint target newMeta before after).ledgers target)
      (key ((normalJoint target newMeta before after).model.cells target) newMeta) = false := by
  simpa [normalJoint, ensureAt] using old_completion_cannot_settle_recreated target
    (before.model.cells target) oldMeta newMeta before.ledgers absent fresh

theorem no_infinite_joint_productive_steps (t : Tree) (stream : Nat → Joint)
    (steps : ∀ n, JointStep t (stream n) (stream (n + 1))) : False := by
  exact no_infinite_closed_steps t (fun n => (stream n).model) (fun n => joint_erases (steps n))

end DrainLifetimeDelivery
