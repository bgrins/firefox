import Std
set_option autoImplicit false
namespace Nesting

structure Triple where
  ids : Nat
  classes : Nat
  types : Nat
  deriving DecidableEq, Repr

def zero : Triple := ⟨0, 0, 0⟩
def add (a b : Triple) : Triple := ⟨a.ids + b.ids, a.classes + b.classes, a.types + b.types⟩
def clamp (a : Triple) : Triple := ⟨min 1023 a.ids, min 1023 a.classes, min 1023 a.types⟩
def lexMax (a b : Triple) : Triple :=
  if a.ids > b.ids then a else if a.ids < b.ids then b
  else if a.classes > b.classes then a else if a.classes < b.classes then b
  else if a.types > b.types then a else b

def pack (a : Triple) : Nat := a.ids * 1048576 + a.classes * 1024 + a.types
def unpack (a : Nat) : Triple := ⟨a / 1048576, (a / 1024) % 1024, a % 1024⟩
def bounded (a : Triple) : Prop := a.ids ≤ 1023 ∧ a.classes ≤ 1023 ∧ a.types ≤ 1023

theorem add_zero (a : Triple) : add a zero = a := by cases a; simp [add, zero]
theorem zero_add (a : Triple) : add zero a = a := by cases a; simp [add, zero]
theorem add_comm (a b : Triple) : add a b = add b a := by cases a; cases b; simp [add, Nat.add_comm]
theorem add_assoc (a b c : Triple) : add (add a b) c = add a (add b c) := by
  cases a; cases b; cases c; simp [add, Nat.add_assoc]
theorem add_left_comm (a b c : Triple) : add a (add b c) = add b (add a c) := by
  rw [← add_assoc, add_comm a b, add_assoc]
theorem clamp_bounded (a : Triple) : bounded (clamp a) := by
  exact ⟨Nat.min_le_left _ _, Nat.min_le_left _ _, Nat.min_le_left _ _⟩
theorem clamp_idempotent (a : Triple) : clamp (clamp a) = clamp a := by
  cases a; simp [clamp]
theorem clamp_identity (a : Triple) (h : bounded a) : clamp a = a := by
  cases a; simp only [bounded] at h; simp [clamp, Nat.min_eq_right h.1, Nat.min_eq_right h.2.1, Nat.min_eq_right h.2.2]

theorem min_add_min (a b limit : Nat) : min limit (a + min limit b) = min limit (a + b) := by omega

theorem clamp_add_subtotal (a b : Triple) : clamp (add a (clamp b)) = clamp (add a b) := by
  cases a; cases b; simp [clamp, add, min_add_min]
theorem clamp_add_both (a b : Triple) : clamp (add (clamp a) (clamp b)) = clamp (add a b) := by
  rw [clamp_add_subtotal, add_comm, clamp_add_subtotal, add_comm]

theorem pack_roundtrip (a : Triple) (h : bounded a) : unpack (pack a) = a := by
  cases a with
  | mk i c t =>
    simp only [bounded] at h
    simp only [pack, unpack, Triple.mk.injEq]
    omega

theorem pack_bound (a : Triple) (h : bounded a) : pack a ≤ 1073741823 := by
  unfold pack bounded at *; omega

structure Flags where
  pseudo : Bool := false
  slotted : Bool := false
  part : Bool := false
  parent : Bool := false
  host : Bool := false
  scope : Bool := false
  deriving DecidableEq, Repr

def emptyFlags : Flags := {}
def union (a b : Flags) : Flags :=
  ⟨a.pseudo || b.pseudo, a.slotted || b.slotted, a.part || b.part,
   a.parent || b.parent, a.host || b.host, a.scope || b.scope⟩
def allowedParent (a : Flags) : Flags := { a with pseudo := false, slotted := false, part := false }
def validParent (a : Flags) : Prop := a.pseudo = false ∧ a.slotted = false ∧ a.part = false

theorem allowed_has_no_forbidden (a : Flags) : validParent (allowedParent a) := by simp [validParent, allowedParent]
theorem valid_parent_unchanged (a : Flags) (h : validParent a) : allowedParent a = a := by
  cases a; simp only [validParent] at h; simp_all [allowedParent]
theorem allowed_preserves_parent (a : Flags) : (allowedParent a).parent = a.parent := rfl
theorem allowed_preserves_host (a : Flags) : (allowedParent a).host = a.host := rfl
theorem allowed_preserves_scope (a : Flags) : (allowedParent a).scope = a.scope := rfl

structure Value where
  spec : Triple
  flags : Flags
  deriving DecidableEq, Repr

def empty : Value := ⟨zero, emptyFlags⟩
def plus (a b : Value) : Value := ⟨add a.spec b.spec, union a.flags b.flags⟩
def maximum (a b : Value) : Value := ⟨lexMax a.spec b.spec, union a.flags b.flags⟩
def suppress (a : Value) : Value := ⟨zero, a.flags⟩
def storeHeader (a : Value) : Value := ⟨clamp a.spec, a.flags⟩

inductive Expr where
  | leaf (value : Value)
  | parent
  | sum (left right : Expr)
  | max (left right : Expr)
  | whereZero (child : Expr)
  | header (child : Expr)
  deriving Repr

def eval (parent : Value) : Expr → Value
  | .leaf value => value
  | .parent => parent
  | .sum a b => plus (eval parent a) (eval parent b)
  | .max a b => maximum (eval parent a) (eval parent b)
  | .whereZero child => suppress (eval parent child)
  | .header child => storeHeader (eval parent child)

def substitute (parent : Value) : Expr → Expr
  | .leaf value => .leaf value
  | .parent => .leaf parent
  | .sum a b => .sum (substitute parent a) (substitute parent b)
  | .max a b => .max (substitute parent a) (substitute parent b)
  | .whereZero child => .whereZero (substitute parent child)
  | .header child => .header (substitute parent child)

theorem substitution_evaluation (expr : Expr) (parent unused : Value) :
    eval unused (substitute parent expr) = eval parent expr := by
  induction expr <;> simp_all [substitute, eval]

def resolved : Expr → Bool
  | .leaf _ => true
  | .parent => false
  | .sum a b | .max a b => resolved a && resolved b
  | .whereZero a | .header a => resolved a

theorem substitution_resolved (expr : Expr) (parent : Value) : resolved (substitute parent expr) = true := by
  induction expr <;> simp_all [substitute, resolved]

theorem substitution_noop_when_resolved (expr : Expr) (parent : Value) (h : resolved expr = true) :
    substitute parent expr = expr := by
  induction expr <;> simp_all [resolved, substitute]

theorem where_specificity_zero (expr : Expr) (parent : Value) : (eval parent (.whereZero expr)).spec = zero := rfl
theorem where_flags_retained (expr : Expr) (parent : Value) : (eval parent (.whereZero expr)).flags = (eval parent expr).flags := rfl

def noParentFlags : Expr → Prop
  | .leaf value => value.flags.parent = false
  | .parent => True
  | .sum a b | .max a b => noParentFlags a ∧ noParentFlags b
  | .whereZero a | .header a => noParentFlags a

theorem parent_flag_removed (expr : Expr) (parent : Value)
    (h : noParentFlags expr) (hp : parent.flags.parent = false) :
    (eval parent expr).flags.parent = false := by
  induction expr <;> simp_all [noParentFlags, eval, plus, maximum, suppress, storeHeader, union]

def fullSum (parent : Triple) : List (Bool × Triple) → Triple
  | [] => zero
  | (direct, value) :: rest => add (if direct then parent else value) (fullSum parent rest)
def directSum (parent : Triple) : List (Bool × Triple) → Triple
  | [] => zero
  | (direct, _) :: rest => add (if direct then parent else zero) (directSum parent rest)
def otherSum : List (Bool × Triple) → Triple
  | [] => zero
  | (direct, value) :: rest => add (if direct then zero else value) (otherSum rest)

theorem sum_partition (items : List (Bool × Triple)) (parent : Triple) :
    fullSum parent items = add (directSum parent items) (otherSum items) := by
  induction items with
  | nil => simp [fullSum, directSum, otherSum, add_zero]
  | cons head rest ih =>
    obtain ⟨direct, value⟩ := head
    cases direct <;> simp [fullSum, directSum, otherSum, ih, zero_add, add_assoc, add_left_comm]

def optimizedSum (parent : Triple) (items : List (Bool × Triple)) : Triple :=
  clamp (add (directSum parent items) (clamp (otherSum items)))

theorem optimized_bounded_sum (items : List (Bool × Triple)) (parent : Triple) :
    optimizedSum parent items = clamp (fullSum parent items) := by
  rw [optimizedSum, clamp_add_subtotal, sum_partition]

theorem packed_delta_borrows :
    clamp (add ⟨0, 1, 0⟩ (unpack (pack ⟨1, 0, 0⟩ - pack ⟨0, 1, 0⟩))) ≠ ⟨1, 0, 0⟩ := by decide

theorem saturated_total_loses_residual :
    clamp (add ⟨1, 0, 0⟩ ⟨0, 1023 - 1000, 0⟩) ≠ clamp (add ⟨1, 0, 0⟩ ⟨0, 1000, 0⟩) := by decide

theorem clamp_not_lexmax_homomorphism :
    clamp (lexMax ⟨1024, 0, 0⟩ ⟨1023, 1, 0⟩) ≠ lexMax (clamp ⟨1024, 0, 0⟩) (clamp ⟨1023, 1, 0⟩) := by decide

end Nesting
