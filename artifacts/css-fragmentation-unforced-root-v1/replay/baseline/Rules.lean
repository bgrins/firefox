import Std
namespace Fragmentation

inductive Control where
  | auto | avoid | avoidPage | avoidColumn | avoidRegion | force
  deriving DecidableEq, Repr
inductive Ancestor where
  | auto | avoid
  deriving DecidableEq, Repr
structure BreakTypes where
  page : Bool := false
  column : Bool := false
  region : Bool := false
  deriving DecidableEq, Repr
inductive Kind where
  | a | b (block : Nat) | c
  deriving DecidableEq, Repr
inductive ContentKind where
  | box (id : Nat) | line (block ordinal : Nat) | gap | graphic (id : Nat)
  deriving DecidableEq, Repr
structure Atom where
  kind : ContentKind
  extent : Nat
  deriving DecidableEq, Repr
structure Opportunity where
  cut : Nat
  kind : Kind
  controls : List Control := []
  commonAncestors : List Ancestor := []
  ancestors : List Ancestor := []
  orphans : Nat := 2
  widows : Nat := 2
  deriving DecidableEq, Repr
inductive Stage where
  | strict | lines | avoid | endClone | bothClone
  deriving DecidableEq, Repr

def avoids (t : BreakTypes) : Control → Bool
  | .avoid => true
  | .avoidPage => t.page
  | .avoidColumn => t.column
  | .avoidRegion => t.region
  | _ => false

def Forbidden (t : BreakTypes) (c : Control) : Prop :=
  c = .avoid ∨ c = .avoidPage ∧ t.page = true ∨
  c = .avoidColumn ∧ t.column = true ∨ c = .avoidRegion ∧ t.region = true

def lineCount (block : Nat) (xs : List Atom) : Nat :=
  (xs.filter (fun a => match a.kind with | .line b _ => b == block | _ => false)).length

def noAvoidAncestors (xs : List Ancestor) : Bool := xs.all (· == .auto)
def hasForced (p : Opportunity) : Bool := p.controls.any (· == .force)
def ruleA (t : BreakTypes) (p : Opportunity) : Bool :=
  (hasForced p || p.controls.all (fun c => !avoids t c)) &&
  (!(p.controls.all (· == .auto)) || noAvoidAncestors p.commonAncestors)
def linesFit (xs : List Atom) (p : Opportunity) (b : Nat) : Bool :=
  decide (p.orphans ≤ lineCount b (xs.take p.cut)) &&
  decide (p.widows ≤ lineCount b (xs.drop p.cut))
def rules (s : Stage) (t : BreakTypes) (xs : List Atom) (p : Opportunity) : Bool :=
  match s with
  | .avoid | .endClone | .bothClone => true
  | .strict | .lines => match p.kind with
    | .a => ruleA t p
    | .b b => noAvoidAncestors p.ancestors && (s == .lines || linesFit xs p b)
    | .c => noAvoidAncestors p.ancestors

def Allowed (s : Stage) (t : BreakTypes) (xs : List Atom) (p : Opportunity) : Prop :=
  s = .avoid ∨ s = .endClone ∨ s = .bothClone ∨
  match p.kind with
  | .a => ((∃ c ∈ p.controls, c = .force) ∨ ∀ c ∈ p.controls, ¬ Forbidden t c) ∧
      ((∀ c ∈ p.controls, c = .auto) → ∀ a ∈ p.commonAncestors, a = .auto)
  | .b b => (∀ a ∈ p.ancestors, a = .auto) ∧
      (s = .lines ∨ p.orphans ≤ lineCount b (xs.take p.cut) ∧
                        p.widows ≤ lineCount b (xs.drop p.cut))
  | .c => ∀ a ∈ p.ancestors, a = .auto

theorem avoidance_refinement (t : BreakTypes) (c : Control) :
    avoids t c = true ↔ Forbidden t c := by cases c <;> simp [avoids, Forbidden]

theorem rule_refinement (s : Stage) (t : BreakTypes) (xs : List Atom) (p : Opportunity) :
    rules s t xs p = true ↔ Allowed s t xs p := by
  cases s <;> cases h : p.kind <;>
    simp [rules, Allowed, ruleA, hasForced, noAvoidAncestors, linesFit, h,
      avoidance_refinement, Bool.eq_false_iff] <;> grind

def ordinary (s : Stage) (t : BreakTypes) (xs : List Atom) (p : Opportunity) : Bool :=
  !hasForced p && rules s t xs p

def Ordinary (s : Stage) (t : BreakTypes) (xs : List Atom) (p : Opportunity) : Prop :=
  (∀ c ∈ p.controls, c ≠ .force) ∧ Allowed s t xs p

theorem ordinary_refinement (s : Stage) (t : BreakTypes) (xs : List Atom) (p : Opportunity) :
    ordinary s t xs p = true ↔ Ordinary s t xs p := by
  simp [ordinary, Ordinary, hasForced, rule_refinement, Bool.eq_false_iff]
  grind

end Fragmentation
