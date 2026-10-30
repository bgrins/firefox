import QueueState

namespace Completion

@[ext] structure State where
  value : Nat → Bool
  queued : Nat → QueueState.Entry
  flight : Nat → Bool
  unrelated : QueueState.Entry

def active (n i : Nat) : Bool := decide (0 < i ∧ i ≤ n)

def begin (s : State) : State :=
  { s with
    queued := fun i => if QueueState.eligible (s.queued i) false then
      QueueState.consume (s.queued i) else s.queued i
    flight := fun i => QueueState.eligible (s.queued i) false }

def evaluated (s : State) (i : Nat) : Bool :=
  if s.flight i then s.value (i - 1) else s.value i

def newWork (n : Nat) (s : State) (i : Nat) : Bool :=
  active n i && s.flight (i - 1) &&
  (evaluated s (i - 1) != s.value (i - 1)) &&
  (evaluated s i != evaluated s (i - 1))

def finish (n : Nat) (s : State) : State :=
  { value := evaluated s
    queued := fun i => if newWork n s i then
      (QueueState.request (s.queued i) .standard QueueState.blocked).entry
      else s.queued i
    flight := fun _ => false
    unrelated := s.unrelated }

def round (n : Nat) (s : State) : State := finish n (begin s)

def canonical (n k : Nat) (u : QueueState.Entry) : State :=
  { value := fun i => decide (i ≤ n ∧ i ≤ k)
    queued := fun i => if i = k + 1 ∧ i ≤ n then .pending else .absent
    flight := fun _ => false
    unrelated := u }

def initial (n : Nat) (u : QueueState.Entry) : State :=
  { value := fun i => decide (i = 0)
    queued := fun i => if i = 1 ∧ i ≤ n then
      (QueueState.request .absent .standard QueueState.blocked).entry else .absent
    flight := fun _ => false
    unrelated := u }

def run (n : Nat) : Nat → State → State
  | 0, s => s
  | k + 1, s => round n (run n k s)

def Covered (n : Nat) (s : State) : Prop :=
  ∀ i, 0 < i → i ≤ n → s.value i ≠ s.value (i - 1) →
    QueueState.eligible (s.queued i) false = true ∨ s.flight i = true

def Ready (n : Nat) (s : State) : Prop :=
  ∀ i, 0 < i → i ≤ n →
    QueueState.eligible (s.queued i) false = false ∧ s.flight i = false

def Fresh (n : Nat) (s : State) : Prop :=
  ∀ i, i ≤ n → s.value i = s.value 0

theorem initial_eq (n : Nat) (u : QueueState.Entry) :
    initial n u = canonical n 0 u := by
  ext i <;> simp [initial, canonical, QueueState.request, QueueState.insert,
    QueueState.post, QueueState.blocked, QueueState.safe, QueueState.admitted,
    QueueState.outside]
  omega

theorem begin_canonical (n k : Nat) (u : QueueState.Entry) :
    begin (canonical n k u) =
      State.mk (canonical n k u).value (fun _ => .absent)
        (fun i => decide (i = k + 1 ∧ i ≤ n)) u := by
  apply State.ext
  · rfl
  · funext i
    by_cases h : i = k + 1 ∧ i ≤ n
    · rcases h with ⟨rfl, bound⟩
      simp [begin, canonical, bound, QueueState.eligible, QueueState.consume]
    · simp [begin, canonical, h, QueueState.eligible, QueueState.consume]
  · funext i
    by_cases h : i = k + 1 ∧ i ≤ n
    · rcases h with ⟨rfl, bound⟩
      simp [begin, canonical, bound, QueueState.eligible]
    · simp [begin, canonical, h, QueueState.eligible]
  · rfl

theorem evaluated_frontier (n k i : Nat) (u : QueueState.Entry) :
    evaluated (begin (canonical n k u)) i = decide (i ≤ n ∧ i ≤ k + 1) := by
  rw [begin_canonical]
  simp only [evaluated, canonical, decide_eq_true_eq]
  split
  · rename_i h
    have : i - 1 ≤ n ∧ i - 1 ≤ k := by omega
    simp [this]
    omega
  · rename_i h
    by_cases hi : i ≤ n
    · have : (i ≤ k) = (i ≤ k + 1) := by apply propext; omega
      simp [hi, this]
    · simp [hi]

theorem generated_frontier (n k i : Nat) (u : QueueState.Entry) :
    newWork n (begin (canonical n k u)) i =
      decide (i = k + 2 ∧ i ≤ n) := by
  simp only [newWork, evaluated_frontier]
  rw [begin_canonical]
  simp only [canonical, active]
  by_cases hi : i = k + 2 ∧ i ≤ n
  · rcases hi with ⟨rfl, bound⟩
    have prev : k + 1 ≤ n := by omega
    simp [bound, prev]
  · by_cases a : 0 < i ∧ i ≤ n
    · have neq : i ≠ k + 2 := by omega
      simp [a, neq]
    · simp [hi, a]

theorem round_canonical (n k : Nat) (u : QueueState.Entry) :
    round n (canonical n k u) = canonical n (k + 1) u := by
  ext i
  · exact evaluated_frontier n k i u
  · simp only [round, finish, generated_frontier]
    rw [begin_canonical]
    simp [canonical, Nat.add_assoc, QueueState.request, QueueState.insert,
      QueueState.post, QueueState.blocked, QueueState.safe, QueueState.admitted,
      QueueState.outside]
  · rfl
  · rfl

theorem run_exact (n k : Nat) (u : QueueState.Entry) :
    run n k (initial n u) = canonical n k u := by
  induction k with
  | zero => exact initial_eq n u
  | succ k ih => simpa [run, ih] using round_canonical n k u

theorem canonical_covered (n k : Nat) (u : QueueState.Entry) :
    Covered n (canonical n k u) := by
  intro i pos bound dirty
  have frontier : i = k + 1 := by
    by_cases h : i = k + 1
    · exact h
    exfalso
    have same : (i ≤ k) = (i - 1 ≤ k) := by apply propext; omega
    have prev : i - 1 ≤ n := by omega
    exact dirty (by simp [canonical, bound, prev, same])
  left
  have bound' : k + 1 ≤ n := by omega
  simp [canonical, frontier, bound', QueueState.eligible]

theorem begin_preserves_coverage (n : Nat) (s : State)
    (covered : Covered n s) (idle : ∀ i, s.flight i = false) :
    Covered n (begin s) := by
  intro i pos bound dirty
  rcases covered i pos bound dirty with queued | flight
  · right
    exact queued
  · simp [idle i] at flight

theorem reachable_coverage (n k : Nat) (u : QueueState.Entry) :
    Covered n (run n k (initial n u)) ∧
    Covered n (begin (run n k (initial n u))) := by
  rw [run_exact]
  have h := canonical_covered n k u
  exact ⟨h, begin_preserves_coverage n _ h (by intro i; rfl)⟩

theorem ready_covered_fresh (n : Nat) (s : State)
    (covered : Covered n s) (ready : Ready n s) : Fresh n s := by
  intro i bound
  induction i with
  | zero => rfl
  | succ i ih =>
    have previous := ih (by omega)
    have equal : s.value (i + 1) = s.value i := by
      by_cases same : s.value (i + 1) = s.value i
      · exact same
      exfalso
      have dirty := same
      have pending := covered (i + 1) (by omega) bound (by simpa using dirty)
      obtain ⟨a, b⟩ := ready (i + 1) (by omega) bound
      rcases pending with h | h <;> simp_all
    exact equal.trans previous

theorem fixed_budget_counterexample (k : Nat) :
    (run (k + 1) k (initial (k + 1) .absent)).value (k + 1) = false ∧
    (run (k + 1) k (initial (k + 1) .absent)).value 0 = true ∧
    (run (k + 1) k (initial (k + 1) .absent)).queued (k + 1) = .pending := by
  rw [run_exact]
  simp [canonical]

theorem depth_bound_completes (n : Nat) (u : QueueState.Entry) :
    Ready n (run n n (initial n u)) ∧ Fresh n (run n n (initial n u)) ∧
    (run n n (initial n u)).unrelated = u := by
  rw [run_exact]
  have ready : Ready n (canonical n n u) := by
    intro i _ bound
    have h : ¬(i = n + 1 ∧ i ≤ n) := by omega
    simp [canonical, h, QueueState.eligible]
  exact ⟨ready, ready_covered_fresh n _ (canonical_covered n n u) ready, rfl⟩

theorem removal_is_not_evaluation :
    (begin (initial 2 .absent)).queued 1 = .absent ∧
    (begin (initial 2 .absent)).flight 1 = true ∧
    (begin (initial 2 .absent)).value 1 = false := by decide

theorem late_pending_witness :
    (round 2 (initial 2 .absent)).queued 1 = .absent ∧
    (round 2 (initial 2 .absent)).flight 1 = false ∧
    (round 2 (initial 2 .absent)).queued 2 = .pending ∧
    (round 2 (initial 2 .absent)).value 2 = false := by decide

def discard (s : State) : State :=
  { s with queued := fun _ => .absent
           flight := fun _ => false }

theorem empty_queue_without_coverage :
    Ready 2 (discard (initial 2 .absent)) ∧
    ¬ Fresh 2 (discard (initial 2 .absent)) := by
  constructor
  · intro i _ _
    exact ⟨rfl, rfl⟩
  · intro fresh
    have h := fresh 1 (by decide)
    change false = true at h
    cases h

def attemptKey (s : State) (key : Nat) : State :=
  { s with queued := fun i => if i = key then
      (QueueState.request (s.queued i) .standard QueueState.safe).entry
      else s.queued i }

theorem attempt_is_not_evaluation :
    (attemptKey (initial 1 .absent) 1).queued 1 = .attempted ∧
    (attemptKey (initial 1 .absent) 1).value 1 = false := by decide

theorem unrelated_pending_does_not_block :
    Ready 1 (run 1 1 (initial 1 .pending)) ∧
    (run 1 1 (initial 1 .pending)).unrelated = .pending := by
  exact ⟨(depth_bound_completes 1 .pending).1,
    (depth_bound_completes 1 .pending).2.2⟩

end Completion
