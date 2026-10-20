import Std
namespace TypeInvalidation

inductive Subject where
  | root
  | descendant (id : Nat)
  | pseudo (id : Nat)
  deriving Repr, DecidableEq

inductive Predicate where
  | always
  | activeType (name : Nat)
  | both (left right : Predicate)
  | either (left right : Predicate)
  | negated (inner : Predicate)
  deriving Repr, DecidableEq

def evaluate (active : Bool) (types : List Nat) : Predicate → Bool
  | .always => true
  | .activeType name => active && types.contains name
  | .both l r => evaluate active types l && evaluate active types r
  | .either l r => evaluate active types l || evaluate active types r
  | .negated p => !evaluate active types p

theorem evaluate_membership_congr (active : Bool) (xs ys : List Nat)
    (same : ∀ name, name ∈ xs ↔ name ∈ ys) (predicate : Predicate) :
    evaluate active xs predicate = evaluate active ys predicate := by
  induction predicate with
  | always => rfl
  | activeType name =>
    have equal : xs.contains name = ys.contains name := by
      apply Bool.eq_iff_iff.mpr
      simpa using same name
    simp only [evaluate, equal]
  | both l r ihl ihr => simp [evaluate, ihl, ihr]
  | either l r ihl ihr => simp [evaluate, ihl, ihr]
  | negated inner ih => simp [evaluate, ih]

structure Rule where
  target : Subject
  condition : Predicate
  value : Nat
  deriving Repr, DecidableEq

def resolve (active : Bool) (types : List Nat) (subject : Subject)
    (base : Nat) : List Rule → Nat
  | [] => base
  | rule :: rules => resolve active types subject
      (if rule.target = subject ∧ evaluate active types rule.condition = true
        then rule.value else base) rules

theorem resolve_membership_congr (active : Bool) (xs ys : List Nat)
    (same : ∀ name, name ∈ xs ↔ name ∈ ys) (subject : Subject) (base : Nat)
    (rules : List Rule) : resolve active xs subject base rules = resolve active ys subject base rules := by
  induction rules generalizing base with
  | nil => rfl
  | cons rule rules ih =>
    simp only [resolve, evaluate_membership_congr active xs ys same rule.condition]
    exact ih _

structure Environment where
  owner : Option Nat
  rootPresent : Bool
  composedDocument : Bool
  presContext : Bool
  subjects : List Subject
  base : Subject → Nat
  rules : List Rule

def Environment.live (e : Environment) : Bool :=
  e.rootPresent && e.composedDocument && e.presContext

structure State where
  types : Nat → List Nat
  cache : Subject → Nat
  pending : Bool
  helperCalls : Nat
  requests : Nat

def activeTypes (e : Environment) (s : State) : List Nat :=
  match e.owner with
  | none => []
  | some owner => s.types owner

def expected (e : Environment) (s : State) (subject : Subject) : Nat :=
  resolve e.owner.isSome (activeTypes e s) subject (e.base subject) e.rules

def Coherent (e : Environment) (s : State) : Prop :=
  e.live = true → ∀ subject ∈ e.subjects,
    s.cache subject = expected e s subject ∨ s.pending = true

inductive Edit where
  | add (name : Nat)
  | delete (name : Nat)
  | clear
  deriving Repr, DecidableEq

def edit (xs : List Nat) (op : Edit) (success : Bool) : List Nat × Bool :=
  if !success then (xs, false) else
  match op with
  | .add name => if name ∈ xs then (xs, false) else (xs ++ [name], true)
  | .delete name => if name ∈ xs then (xs.erase name, true) else (xs, false)
  | .clear => if xs.isEmpty then (xs, false) else ([], true)

theorem ineffective_unchanged (xs : List Nat) (op : Edit) (success : Bool)
    (h : (edit xs op success).2 = false) : (edit xs op success).1 = xs := by
  cases success <;> cases op <;> simp_all [edit] <;> split at h <;> simp_all

theorem failure_unchanged (xs : List Nat) (op : Edit) :
    edit xs op false = (xs, false) := by simp [edit]

def helperCalled (s : State) (actor : Nat) (op : Edit) (success : Bool) : Bool :=
  (edit (s.types actor) op success).2

def notified (e : Environment) (s : State) (actor : Nat) (op : Edit)
    (success : Bool) : Bool :=
  false

def mutate (e : Environment) (s : State) (actor : Nat) (op : Edit)
    (success : Bool) : State :=
  let result := edit (s.types actor) op success
  let notify := notified e s actor op success
  { types := fun id => if id = actor then result.1 else s.types id
    cache := s.cache
    pending := s.pending || notify
    helperCalls := s.helperCalls + if result.2 then 1 else 0
    requests := s.requests + if notify then 1 else 0 }

theorem mutation_cache (e : Environment) (s : State) (actor : Nat) (op : Edit)
    (success : Bool) : (mutate e s actor op success).cache = s.cache := rfl

theorem mutation_other_types (e : Environment) (s : State) (actor other : Nat)
    (op : Edit) (success : Bool) (h : other ≠ actor) :
    (mutate e s actor op success).types other = s.types other := by simp [mutate, h]

theorem old_owner_no_notification (e : Environment) (s : State) (actor : Nat)
    (op : Edit) (success : Bool) (h : e.owner ≠ some actor) :
    notified e s actor op success = false := by simp [notified, h]

theorem absent_presentation_no_notification (e : Environment) (s : State)
    (actor : Nat) (op : Edit) (success : Bool) (h : e.live = false) :
    notified e s actor op success = false := by simp [notified, h]

theorem effective_active_request (e : Environment) (s : State) (actor : Nat)
    (op : Edit) (success : Bool) (live : e.live = true)
    (owner : e.owner = some actor) (effective : helperCalled s actor op success = true) :
    notified e s actor op success = true := by simp [notified, live, owner, effective]

theorem silent_current_types (e : Environment) (s : State) (actor : Nat)
    (op : Edit) (success : Bool) (live : e.live = true)
    (silent : notified e s actor op success = false) :
    activeTypes e (mutate e s actor op success) = activeTypes e s := by
  cases ho : e.owner with
  | none => simp [activeTypes, ho]
  | some id =>
    by_cases same : id = actor
    · subst id
      have he : (edit (s.types actor) op success).2 = false := by
        simpa [notified, helperCalled, ho, live] using silent
      simp [activeTypes, ho, mutate, ineffective_unchanged _ _ _ he]
    · simp [activeTypes, ho, mutate, same]

theorem mutation_preserves (e : Environment) (s : State) (actor : Nat)
    (op : Edit) (success : Bool) (h : Coherent e s) :
    Coherent e (mutate e s actor op success) := by
  intro live subject member
  by_cases notify : notified e s actor op success = true
  · right; simp [mutate, notify]
  · have silent : notified e s actor op success = false := Bool.eq_false_iff.mpr notify
    have same := silent_current_types e s actor op success live silent
    rcases h live subject member with fresh | pending
    · left
      simpa [expected, mutation_cache, same] using fresh
    · right; simp [mutate, pending]

def covered (e : Environment) (visited : List Subject) : Bool :=
  e.subjects.all (fun subject => visited.contains subject)

def flush (e : Environment) (s : State) (visited : List Subject) : State :=
  { s with
    cache := fun subject => if s.pending ∧ subject ∈ visited
      then expected e s subject else s.cache subject
    pending := s.pending && !covered e visited }

theorem flush_expected (e : Environment) (s : State) (visited : List Subject)
    (subject : Subject) : expected e (flush e s visited) subject = expected e s subject := rfl

theorem covered_member (e : Environment) (visited : List Subject)
    (h : covered e visited = true) (subject : Subject) (member : subject ∈ e.subjects) :
    subject ∈ visited := by
  have := List.all_eq_true.mp h subject member
  simpa using this

theorem flush_preserves (e : Environment) (s : State) (visited : List Subject)
    (h : Coherent e s) : Coherent e (flush e s visited) := by
  intro live subject member
  rcases h live subject member with fresh | pending
  · left
    rw [flush_expected]
    change (if s.pending ∧ subject ∈ visited then expected e s subject else s.cache subject) = _
    split <;> simp_all
  · by_cases seen : subject ∈ visited
    · left
      rw [flush_expected]
      change (if s.pending ∧ subject ∈ visited then expected e s subject else s.cache subject) = _
      simp [pending, seen]
    · right
      have incomplete : covered e visited = false := by
        apply Bool.eq_false_iff.mpr
        intro complete
        exact seen (covered_member e visited complete subject member)
      simp [flush, pending, incomplete]

theorem complete_flush_clean (e : Environment) (s : State) (visited : List Subject)
    (complete : covered e visited = true) : (flush e s visited).pending = false := by
  simp [flush, complete]

theorem complete_flush_observation (e : Environment) (s : State)
    (visited : List Subject) (h : Coherent e s) (live : e.live = true)
    (complete : covered e visited = true) (subject : Subject) (member : subject ∈ e.subjects) :
    (flush e s visited).cache subject = expected e (flush e s visited) subject := by
  rcases flush_preserves e s visited h live subject member with fresh | pending
  · exact fresh
  · rw [complete_flush_clean e s visited complete] at pending
    contradiction

inductive Action where
  | mutation (actor : Nat) (op : Edit) (success : Bool)
  | delivery (visited : List Subject)
  deriving Repr, DecidableEq

def step (e : Environment) (s : State) : Action → State
  | .mutation actor op success => mutate e s actor op success
  | .delivery visited => flush e s visited

def run (e : Environment) : State → List Action → State
  | s, [] => s
  | s, action :: rest => run e (step e s action) rest

theorem step_preserves (e : Environment) (s : State) (action : Action)
    (h : Coherent e s) : Coherent e (step e s action) := by
  cases action with
  | mutation actor op success => exact mutation_preserves e s actor op success h
  | delivery visited => exact flush_preserves e s visited h

theorem history_preserves (e : Environment) (s : State) (actions : List Action)
    (h : Coherent e s) : Coherent e (run e s actions) := by
  induction actions generalizing s with
  | nil => exact h
  | cons action rest ih => exact ih _ (step_preserves e s action h)

theorem history_then_flush_observation (e : Environment) (s : State)
    (actions : List Action) (visited : List Subject) (h : Coherent e s)
    (live : e.live = true) (complete : covered e visited = true)
    (subject : Subject) (member : subject ∈ e.subjects) :
    (flush e (run e s actions) visited).cache subject =
      expected e (run e s actions) subject := by
  exact complete_flush_observation e _ visited (history_preserves e s actions h)
    live complete subject member

end TypeInvalidation
