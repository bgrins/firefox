import Demand

namespace UnitFallback

inductive Path {α : Type} (edge : α → α → Prop) : α → α → Prop where
  | single {a b} : edge a b → Path edge a b
  | cons {a b c} : edge a b → Path edge b c → Path edge a c

def Cyclic {α : Type} (edge : α → α → Prop) : Prop := ∃ a, Path edge a a

theorem path_decreases {α : Type} (edge : α → α → Prop) (rank : α → Nat)
    (decreases : ∀ a b, edge a b → rank b < rank a) {a b}
    (path : Path edge a b) : rank b < rank a := by
  induction path with
  | single h => exact decreases _ _ h
  | cons h _ ih => exact Nat.lt_trans ih (decreases _ _ h)

def addUnit {α : Type} (base : α → α → Prop) (source font : α)
    (unit : Bool) (a b : α) : Prop :=
  base a b ∨ (a = source ∧ b = font ∧ unit = true)

theorem retains_all_base_edges {α : Type} (base : α → α → Prop)
    (source font : α) (unit : Bool) {a b} (h : base a b) :
    addUnit base source font unit a b := Or.inl h

theorem retains_base_cycles {α : Type} (base : α → α → Prop)
    (source font : α) (unit : Bool) (h : Cyclic base) :
    Cyclic (addUnit base source font unit) := by
  obtain ⟨a, path⟩ := h
  refine ⟨a, ?_⟩
  induction path with
  | single h => exact .single (Or.inl h)
  | cons h _ ih => exact .cons (Or.inl h) ih

theorem successful_primary_classifier_independent
    {α : Type} (classify : Option DemandFallback.Result → α)
    (lookup : String → Option DemandFallback.Expr) (fuel : Nat)
    (stack cyclic : List String) (name : String)
    (left right : DemandFallback.Expr) (r : DemandFallback.Result)
    (tokens : List String)
    (primary : DemandFallback.eval lookup fuel stack cyclic (.property name) = some r)
    (valid : r.value = some tokens) :
    classify (DemandFallback.eval lookup (fuel + 1) stack cyclic
      (.expression (.fallback name left))) =
    classify (DemandFallback.eval lookup (fuel + 1) stack cyclic
      (.expression (.fallback name right))) := by
  rw [DemandFallback.successful_primary_skips_any_fallback _ _ _ _ _ _ _ _ primary valid,
      DemandFallback.successful_primary_skips_any_fallback _ _ _ _ _ _ _ _ primary valid]

inductive Length where
  | px (value : Nat)
  | em (value : Nat)
  deriving DecidableEq, Repr

def needsFont : Length → Bool
  | .px _ => false
  | .em _ => true

def select (primary : Option Length) (fallback : Length) : Length :=
  primary.getD fallback

inductive Timing where
  | substituted
  | lexicalInventory
  deriving DecidableEq, Repr

def dependency (timing : Timing) (primary : Option Length) (fallback : Length) : Bool :=
  match timing with
  | .substituted => needsFont (select primary fallback)
  | .lexicalInventory => needsFont (select primary fallback) || needsFont fallback

theorem missing_primary_policies_agree (fallback : Length) :
    dependency .substituted none fallback = dependency .lexicalInventory none fallback := by
  cases fallback <;> rfl

inductive Node where
  | registered
  | font
  deriving DecidableEq, Repr

def edge (unit : Bool) (a b : Node) : Prop :=
  (a = .font ∧ b = .registered) ∨ (a = .registered ∧ b = .font ∧ unit = true)

private def rank : Node → Nat
  | .registered => 0
  | .font => 1

theorem cycle_iff_unit (unit : Bool) : Cyclic (edge unit) ↔ unit = true := by
  constructor
  · intro h
    cases unit with
    | true => rfl
    | false =>
      obtain ⟨a, path⟩ := h
      have dec : ∀ a b, edge false a b → rank b < rank a := by
        intro a b h
        cases a <;> cases b <;> simp_all [edge, rank]
      exact False.elim ((Nat.lt_irrefl _) (path_decreases _ _ dec path))
  · intro h
    subst unit
    exact ⟨.font, .cons (Or.inl ⟨rfl, rfl⟩)
      (.single (Or.inr ⟨rfl, rfl, rfl⟩))⟩

theorem defined_absolute_separates (pixels ems : Nat) :
    ¬ Cyclic (edge (dependency .substituted (some (.px pixels)) (.em ems))) ∧
    Cyclic (edge (dependency .lexicalInventory (some (.px pixels)) (.em ems))) := by
  constructor
  · rw [cycle_iff_unit]
    decide
  · rw [cycle_iff_unit]
    rfl

theorem selected_relative_cycle_preserved (ems : Nat) (timing : Timing) :
    Cyclic (edge (dependency timing none (.em ems))) := by
  rw [cycle_iff_unit]
  cases timing <;> rfl

end UnitFallback
