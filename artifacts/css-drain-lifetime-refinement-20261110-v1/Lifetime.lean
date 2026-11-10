import Phases

namespace DrainLifetime
open CertifiedPath (Tree)
open DescendingPhases (StrictDesc normal application)

inductive Origin where
  | initial
  | ancestor (producer event : Nat)
  deriving DecidableEq, Repr

structure Cell where
  present : Bool
  lifetime : Nat
  clears : Nat
  ticket : Option Origin
  admittedFrom : Option Origin
  deriving DecidableEq, Repr

def initial : Cell := ⟨false, 0, 0, some .initial, none⟩

def clear (cause : Origin) (c : Cell) : Cell :=
  if c.present then { c with present := false, clears := c.clears + 1, ticket := some cause }
  else c

def ensure (c : Cell) : Cell :=
  if c.present then c
  else { c with present := true, lifetime := c.lifetime + 1, ticket := none, admittedFrom := c.ticket }

def Valid (c : Cell) : Prop :=
  c.ticket.isSome = !c.present ∧ c.lifetime + (if c.present then 0 else 1) = c.clears + 1

def ValidOrigin (t : Tree) (target : Nat) : Origin → Prop
  | .initial => True
  | .ancestor producer _ => StrictDesc t producer target

instance (t : Tree) (target : Nat) (o : Origin) : Decidable (ValidOrigin t target o) := by
  cases o <;> unfold ValidOrigin <;> infer_instance

def Causal (t : Tree) (target : Nat) (c : Cell) : Prop :=
  ∀ o, c.ticket = some o → ValidOrigin t target o

def clearDescendants (t : Tree) (producer event : Nat) (cells : Nat → Cell) : Nat → Cell :=
  fun target => if target ≤ t.size ∧ StrictDesc t producer target then clear (.ancestor producer event) (cells target)
                else cells target

def ensureAt (target : Nat) (cells : Nat → Cell) : Nat → Cell :=
  fun node => if node = target then ensure (cells node) else cells node

theorem initial_valid : Valid initial := by simp [Valid, initial]

theorem initial_causal (t : Tree) (node : Nat) : Causal t node initial := by
  intro o h; cases h; trivial

theorem clear_absent (cause) (c : Cell) (h : c.present = false) : clear cause c = c := by
  simp [clear, h]

theorem ensure_present (c : Cell) (h : c.present = true) : ensure c = c := by
  simp [ensure, h]

theorem clear_valid (cause) (c : Cell) (h : Valid c) : Valid (clear cause c) := by
  cases hp : c.present <;> simp_all [clear, Valid] <;> omega

theorem ensure_valid (c : Cell) (h : Valid c) : Valid (ensure c) := by
  cases hp : c.present <;> simp_all [ensure, Valid] <;> omega

theorem ensure_has_origin (c : Cell) (valid : Valid c) (absent : c.present = false) :
    ∃ o, (ensure c).admittedFrom = some o ∧ c.ticket = some o := by
  have ticket : c.ticket.isSome = true := by simpa [absent] using valid.1
  cases ht : c.ticket with
  | none => simp [ht] at ticket
  | some o => exact ⟨o, by simp [ensure, absent, ht], rfl⟩

theorem ensure_causal_origin (t : Tree) (node) (c : Cell) (valid : Valid c)
    (causal : Causal t node c) (absent : c.present = false) :
    ∃ o, (ensure c).admittedFrom = some o ∧ ValidOrigin t node o := by
  obtain ⟨o, admitted, ticket⟩ := ensure_has_origin c valid absent
  exact ⟨o, admitted, causal o ticket⟩

theorem ensure_ticket_consumed (c : Cell) : (ensure c).present = true := by
  cases hp : c.present <;> simp [ensure, hp]

theorem ensure_idempotent (c : Cell) : ensure (ensure c) = ensure c := by
  exact ensure_present _ (ensure_ticket_consumed c)

theorem clear_idempotent (cause other) (c : Cell) : clear other (clear cause c) = clear cause c := by
  cases hp : c.present <;> simp [clear, hp]

theorem no_self_descendant (t : Tree) (node) : ¬ StrictDesc t node node := by
  intro h; have less := DescendingPhases.descendant_rank t h; omega

theorem producer_preserved (t : Tree) (producer event) (cells : Nat → Cell) :
    clearDescendants t producer event cells producer = cells producer := by
  simp [clearDescendants, no_self_descendant]

theorem descendant_ticket (t : Tree) (producer event target) (cells : Nat → Cell)
    (bound : target ≤ t.size) (desc : StrictDesc t producer target) (present : (cells target).present = true) :
    (clearDescendants t producer event cells target).ticket = some (.ancestor producer event) := by
  simp [clearDescendants, bound, desc, clear, present]

theorem clear_preserves_causality (t : Tree) (producer event target) (cells : Nat → Cell)
    (old : Causal t target (cells target)) : Causal t target (clearDescendants t producer event cells target) := by
  by_cases desc : target ≤ t.size ∧ StrictDesc t producer target
  · cases hp : (cells target).present
    · simpa [clearDescendants, desc, clear, hp] using old
    · intro o h
      have eq : Origin.ancestor producer event = o := by simpa [clearDescendants, desc, clear, hp] using h
      rw [← eq]; exact desc.2
  · simpa [clearDescendants, desc] using old

theorem ensure_preserves_causality (t : Tree) (node) (c : Cell)
    (old : Causal t node c) : Causal t node (ensure c) := by
  cases hp : c.present
  · intro o h; simp [ensure, hp] at h
  · simpa [ensure, hp] using old

theorem lifetime_bound (c : Cell) (valid : Valid c) : c.lifetime ≤ c.clears + 1 := by
  have := valid.2; omega

inductive Dispatch (t : Tree) : Nat → List Bool → List Bool → Prop where
  | fire (front rest : List Bool) (choice : Nat → Nat → Bool) :
      Dispatch t front.length (front ++ true :: rest) (DescendingPhases.dispatch t 0 front rest choice)

theorem dispatch_erases {t source before after} (h : Dispatch t source before after) :
    DescendingPhases.Step t 0 before after := by
  cases h with
  | fire front rest choice => exact DescendingPhases.full_dispatch_step t 0 front rest choice

structure Model where
  pending : List Bool
  cells : Nat → Cell
  clock : Nat

inductive Step (t : Tree) : Model → Model → Prop where
  | normal (node : Nat) (bound : node ≤ t.size) (before : Model) (after)
      (fire : Dispatch t (normal node) before.pending after) :
      Step t before ⟨after, ensureAt node before.cells, before.clock + 1⟩
  | application (producer : Nat) (bound : producer ≤ t.size) (before : Model) (after)
      (fire : Dispatch t (application producer) before.pending after) :
      Step t before ⟨after, clearDescendants t producer before.clock before.cells, before.clock + 1⟩

theorem step_erases {t before after} (h : Step t before after) :
    DescendingPhases.Step t 0 before.pending after.pending := by
  cases h <;> apply dispatch_erases <;> assumption

theorem step_valid {t before after} (h : Step t before after)
    (valid : ∀ n, Valid (before.cells n)) : ∀ n, Valid (after.cells n) := by
  intro n
  cases h with
  | normal node bound before after fire =>
    simp only [ensureAt]
    split
    · exact ensure_valid _ (valid n)
    · exact valid n
  | application producer bound before after fire =>
    simp only [clearDescendants]
    split
    · exact clear_valid _ _ (valid n)
    · exact valid n

theorem step_causal {t before after} (h : Step t before after)
    (causal : ∀ n, Causal t n (before.cells n)) : ∀ n, Causal t n (after.cells n) := by
  intro n
  cases h with
  | normal node bound before after fire =>
    simp only [ensureAt]
    split
    · exact ensure_preserves_causality _ _ _ (causal n)
    · exact causal n
  | application producer bound before after fire => exact clear_preserves_causality _ _ _ _ _ (causal n)

theorem step_clear_bound {t before after} (h : Step t before after) (node) :
    (after.cells node).clears ≤ (before.cells node).clears + 1 := by
  cases h with
  | normal target bound before after fire =>
    simp only [ensureAt]; split
    · cases hp : (before.cells node).present <;> simp [ensure, hp]
    · omega
  | application producer bound before after fire =>
    simp only [clearDescendants]; split
    · cases hp : (before.cells node).present <;> simp [clear, hp]
    · omega

inductive History (t : Tree) : Nat → Model → Model → Prop where
  | nil (s) : History t 0 s s
  | cons {n a b c} : Step t a b → History t n b c → History t (n + 1) a c

theorem history_erases {t count before after} (h : History t count before after) :
    DescendingPhases.History t 0 count before.pending after.pending := by
  induction h with
  | nil s => exact .zero _
  | cons step tail ih => exact .next (step_erases step) ih

theorem history_valid {t count before after} (h : History t count before after)
    (valid : ∀ n, Valid (before.cells n)) : ∀ n, Valid (after.cells n) := by
  induction h with
  | nil s => exact valid
  | cons step tail ih => exact ih (step_valid step valid)

theorem history_clear_bound {t count before after} (h : History t count before after) (node) :
    (after.cells node).clears ≤ (before.cells node).clears + count := by
  induction h with
  | nil s => omega
  | cons step tail ih => have one := step_clear_bound step node; omega

theorem recreated_lifetime_budget {t count before after} (h : History t count before after)
    (valid : ∀ n, Valid (before.cells n)) (node) :
    (after.cells node).lifetime ≤ (before.cells node).clears + DescendingPhases.weight before.pending + 1 := by
  have hv := lifetime_bound _ (history_valid h valid node)
  have hc := history_clear_bound h node
  have hb := DescendingPhases.history_budget (history_erases h)
  omega


theorem step_clock {t before after} (h : Step t before after) : after.clock = before.clock + 1 := by
  cases h <;> rfl

theorem history_clock {t count before after} (h : History t count before after) :
    after.clock = before.clock + count := by
  induction h with
  | nil s => omega
  | cons step tail ih => have hs := step_clock step; omega

theorem history_causal {t count before after} (h : History t count before after)
    (causal : ∀ n, Causal t n (before.cells n)) : ∀ n, Causal t n (after.cells n) := by
  induction h with
  | nil s => exact causal
  | cons step tail ih => exact ih (step_causal step causal)

theorem closed_productive_budget {t count before after} (h : History t count before after) :
    count ≤ DescendingPhases.weight before.pending := by
  have bound := DescendingPhases.history_budget (history_erases h)
  omega

theorem no_infinite_closed_steps (t : Tree) (stream : Nat → Model)
    (steps : ∀ n, Step t (stream n) (stream (n + 1))) : False := by
  exact DescendingPhases.no_infinite_productive_run t 0 (fun n => (stream n).pending)
    (fun n => step_erases (steps n))

def InitialOnly (c : Cell) : Prop := c.ticket = some .initial → c.lifetime = 0

theorem initial_only : InitialOnly initial := by simp [InitialOnly, initial]

theorem clear_initial_only (p event) (c : Cell) (h : InitialOnly c) :
    InitialOnly (clear (.ancestor p event) c) := by
  cases hp : c.present <;> simp_all [clear, InitialOnly]

theorem ensure_initial_only (c : Cell) (h : InitialOnly c) : InitialOnly (ensure c) := by
  cases hp : c.present <;> simp_all [ensure, InitialOnly]

theorem step_initial_only {t before after} (h : Step t before after)
    (valid : ∀ n, InitialOnly (before.cells n)) : ∀ n, InitialOnly (after.cells n) := by
  intro n
  cases h with
  | normal node bound before after fire =>
    simp only [ensureAt]; split
    · exact ensure_initial_only _ (valid n)
    · exact valid n
  | application producer bound before after fire =>
    simp only [clearDescendants]; split
    · exact clear_initial_only _ _ _ (valid n)
    · exact valid n

theorem history_initial_only {t count before after} (h : History t count before after)
    (valid : ∀ n, InitialOnly (before.cells n)) : ∀ n, InitialOnly (after.cells n) := by
  induction h with
  | nil s => exact valid
  | cons step tail ih => exact ih (step_initial_only step valid)

def smallTree : Tree := ⟨2, fun _ => 0, by intro n; omega⟩
def readyCells : Nat → Cell := fun _ => ensure initial
def start : Model := ⟨[false, true, false, false, false, false], readyCells, 0⟩
def childChoice (target _source : Nat) : Bool := target == normal 1
def middle : Model :=
  ⟨DescendingPhases.dispatch smallTree 0 [false] [false, false, false, false] childChoice,
    clearDescendants smallTree 0 0 readyCells, 1⟩
def finish : Model :=
  ⟨DescendingPhases.dispatch smallTree 0 [false, false] [false, false, false] (fun _ _ => false),
    ensureAt 1 middle.cells, 2⟩

theorem demo_application : Step smallTree start middle := by
  exact .application 0 (by decide) start _ (.fire [false] [false, false, false, false] childChoice)

theorem demo_normal : Step smallTree middle finish := by
  apply Step.normal 1 (by decide) middle
  have hm : middle.pending = [false, false, true, false, false, false] := by decide +kernel
  rw [hm]
  exact .fire [false, false] [false, false, false] (fun _ _ => false)

theorem demo_history : History smallTree 2 start finish :=
  .cons demo_application (.cons demo_normal (.nil finish))

def unrestrictedRenewal (c : Cell) : Cell := ensure (clear (.ancestor 1 0) c)

theorem unrestricted_renews (c : Cell) (present : c.present = true) :
    (unrestrictedRenewal c).lifetime = c.lifetime + 1 := by
  simp [unrestrictedRenewal, clear, ensure, present]

theorem self_origin_not_valid : ¬ ValidOrigin smallTree 1 (.ancestor 1 0) := by
  exact no_self_descendant smallTree 1

def freeRenewal (s : Model) : Model :=
  { s with cells := fun n => if n = 1 then unrestrictedRenewal (s.cells n) else s.cells n }

theorem free_renewal_keeps_phase (s : Model) : (freeRenewal s).pending = s.pending := rfl

theorem free_renewal_advances_lifetime (s : Model) (present : (s.cells 1).present = true) :
    ((freeRenewal s).cells 1).lifetime = (s.cells 1).lifetime + 1 := by
  simpa [freeRenewal] using unrestricted_renews (s.cells 1) present

end DrainLifetime
