import FontDemand

namespace FontReadinessPhase
open FontConsumerDemand

structure Progress where
  requested : Demand
  fulfilled : Demand
  deriving DecidableEq, Repr

def request (p : Progress) (d : Demand) : Progress :=
  { p with requested := join p.requested d }

def requestBatches (p : Progress) : List (List FontConsumerDemand.Unit) → Progress
  | [] => p
  | batch :: rest => requestBatches (request p (summary batch)) rest

inductive Answer where
  | ready | pending
  deriving DecidableEq, Repr

def answer (p : Progress) (d : Demand) : Answer :=
  if Covers p.fulfilled d then .ready else .pending

theorem request_batches_exact (p : Progress) (batches : List (List FontConsumerDemand.Unit)) :
    requestBatches p batches =
      ⟨accumulate p.requested batches, p.fulfilled⟩ := by
  induction batches generalizing p with
  | nil => rfl
  | cons batch rest ih =>
      simpa [requestBatches, request, accumulate] using (ih (request p (summary batch)))

theorem later_requests_preserve_completed_answers (p : Progress)
    (batches : List (List FontConsumerDemand.Unit)) (d : Demand) :
    answer (requestBatches p batches) d = answer p d := by
  rw [request_batches_exact]
  rfl

theorem size_complete_metrics_pending (requested : Demand)
    (batches : List (List FontConsumerDemand.Unit)) :
    answer (requestBatches ⟨requested, .size⟩ batches) .size = .ready ∧
    answer (requestBatches ⟨requested, .size⟩ batches) .metrics = .pending := by
  simp only [later_requests_preserve_completed_answers]
  simp [answer, Covers, rank]

theorem served_reads_are_final (p : Progress) (unit : FontConsumerDemand.Unit)
    (actual final : FontState) (certificate : Ready p.fulfilled actual final)
    (served : answer p (demand unit) = .ready) :
    reads actual unit = reads final unit := by
  have covered : Covers p.fulfilled (demand unit) := by
    simpa [answer] using served
  exact (ready_single_iff unit actual final).mp
    (ready_weaken p.fulfilled (demand unit) actual final covered certificate)

def complete (p : Progress) (certified : Demand) : Progress :=
  { p with fulfilled := join p.fulfilled certified }

theorem completion_preserves_served_answers (p : Progress) (certified need : Demand)
    (served : answer p need = .ready) :
    answer (complete p certified) need = .ready := by
  rcases p with ⟨requested, fulfilled⟩
  cases fulfilled <;> cases certified <;> cases need <;>
    simp_all [answer, complete, Covers, rank, join]

inductive Node where
  | size | sizeAlias | weight | metrics | metricAlias
  deriving DecidableEq, Repr

def requires : Node → Node → Prop
  | .sizeAlias, .size => True
  | .weight, .sizeAlias => True
  | .metrics, .size => True
  | .metrics, .weight => True
  | .metricAlias, .size => True
  | .metricAlias, .metrics => True
  | _, _ => False

def level : Node → Nat
  | .size => 0
  | .sizeAlias => 1
  | .weight => 2
  | .metrics => 3
  | .metricAlias => 4

inductive Path (edge : α → α → Prop) : α → α → Prop
  | one {a b} : edge a b → Path edge a b
  | more {a b c} : edge a b → Path edge b c → Path edge a c

theorem path_decreases (edge : α → α → Prop) (rank : α → Nat)
    (decreases : ∀ a b, edge a b → rank b < rank a)
    (path : Path edge a b) : rank b < rank a := by
  induction path with
  | one h => exact decreases _ _ h
  | more h _ ih => exact Nat.lt_trans ih (decreases _ _ h)

theorem separated_dependencies_acyclic (node : Node) : ¬ Path requires node node := by
  intro h
  have decreasing : ∀ a b, requires a b → level b < level a := by
    intro a b h
    cases a <;> cases b <;> simp_all [requires, level]
  exact Nat.lt_irrefl _ (path_decreases requires level decreasing h)

inductive Projected where
  | fontSize | sizeAlias | weight | metricAlias
  deriving DecidableEq, Repr

def project : Node → Projected
  | .size | .metrics => .fontSize
  | .sizeAlias => .sizeAlias
  | .weight => .weight
  | .metricAlias => .metricAlias

def merged (a b : Projected) : Prop :=
  ∃ x y, requires x y ∧ project x = a ∧ project y = b

theorem merging_creates_false_cycle : Path merged .fontSize .fontSize := by
  apply Path.more (b := .weight)
  · exact ⟨.metrics, .weight, trivial, rfl, rfl⟩
  apply Path.more (b := .sizeAlias)
  · exact ⟨.weight, .sizeAlias, trivial, rfl, rfl⟩
  exact Path.one ⟨.sizeAlias, .size, trivial, rfl, rfl⟩

def metricBackref (a b : Node) : Prop :=
  (a = .metrics ∧ b = .weight) ∨ (a = .weight ∧ b = .metricAlias) ∨
    (a = .metricAlias ∧ b = .metrics)

theorem genuine_metric_wait_cycle : Path metricBackref .metrics .metrics := by
  apply Path.more (b := Node.weight)
  · exact Or.inl ⟨rfl, rfl⟩
  apply Path.more (b := Node.metricAlias)
  · exact Or.inr (Or.inl ⟨rfl, rfl⟩)
  exact Path.one (Or.inr (Or.inr ⟨rfl, rfl⟩))

end FontReadinessPhase
