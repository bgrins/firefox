import Std

namespace CounterRangeRepresentation

inductive IntegerRep where
  | inline (value : Int)
  | boxedResolved (value : Int)
  | unresolved
  deriving DecidableEq, Repr

def inlineGet : IntegerRep → Option Int
  | .inline n => some n
  | _ => none

def resolve : IntegerRep → Option Int
  | .inline n | .boxedResolved n => some n
  | .unresolved => none

inductive Bound where
  | infinite
  | finite (integer : IntegerRep)
  deriving DecidableEq, Repr

structure Range where
  lower : Bound
  upper : Bound
  deriving DecidableEq, Repr

inductive Endpoint where
  | infinite
  | finite (value : Int)
  deriving DecidableEq, Repr

structure SemanticRange where
  lower : Endpoint
  upper : Endpoint
  deriving DecidableEq, Repr

def decodeBound : Bound → Option Endpoint
  | .infinite => some .infinite
  | .finite i => (resolve i).map Endpoint.finite

def decode (r : Range) : Option SemanticRange := do
  let lo ← decodeBound r.lower
  let hi ← decodeBound r.upper
  return ⟨lo, hi⟩

def ordered : SemanticRange → Bool
  | ⟨.finite lo, .finite hi⟩ => decide (lo ≤ hi)
  | _ => true

def member (r : SemanticRange) (n : Int) : Bool :=
  (match r.lower with | .infinite => true | .finite lo => decide (lo ≤ n)) &&
  (match r.upper with | .infinite => true | .finite hi => decide (n ≤ hi))

def finiteValid : Bound → Bool
  | .infinite => true
  | .finite i => (resolve i).isSome

def finiteOrdered : Range → Bool
  | ⟨.finite lo, .finite hi⟩ =>
    match resolve lo, resolve hi with
    | some a, some b => decide (a ≤ b)
    | _, _ => false
  | _ => true

def admitted (r : Range) : Bool :=
  finiteValid r.lower && finiteValid r.upper && finiteOrdered r

def exportWith (read : IntegerRep → Option Int) (r : Range) (n : Int) : Option Bool := do
  let lower ← match r.lower with
    | .infinite => some true
    | .finite i => (read i).map fun lo => decide (lo ≤ n)
  if !lower then return false
  match r.upper with
  | .infinite => some true
  | .finite i => (read i).map fun hi => decide (n ≤ hi)

def oldAdmitted (r : Range) : Bool := finiteOrdered r

def eachFinite (r : Range) : Prop :=
  (∀ i, r.lower = .finite i → ∃ n, resolve i = some n) ∧
  (∀ i, r.upper = .finite i → ∃ n, resolve i = some n)

private theorem bound_valid (b : Bound) :
    finiteValid b = true ↔ ∃ e, decodeBound b = some e := by
  cases b with
  | infinite => simp [finiteValid, decodeBound]
  | finite i => cases i <;> simp [finiteValid, decodeBound, resolve]

theorem admission_iff (r : Range) :
    admitted r = true ↔ ∃ s, decode r = some s ∧ ordered s = true := by
  rcases r with ⟨lo, hi⟩
  cases lo with
  | infinite =>
    cases hi with
    | infinite => simp [admitted, finiteValid, finiteOrdered, decode, decodeBound, ordered]
    | finite i => cases i <;> simp [admitted, finiteValid, finiteOrdered, decode, decodeBound, resolve, ordered]
  | finite i =>
    cases hi with
    | infinite => cases i <;> simp [admitted, finiteValid, finiteOrdered, decode, decodeBound, resolve, ordered]
    | finite j => cases i <;> cases j <;> simp [admitted, finiteValid, finiteOrdered, decode, decodeBound, resolve, ordered]

theorem every_finite_valid (r : Range) (valid : admitted r = true) : eachFinite r := by
  have values : finiteValid r.lower = true ∧ finiteValid r.upper = true ∧ finiteOrdered r = true := by
    simpa [admitted, Bool.and_eq_true, and_assoc] using valid
  have both := And.intro values.1 values.2.1
  constructor
  · intro i eq
    have h := both.1
    rw [eq] at h
    cases i <;> simp_all [finiteValid, resolve]
  · intro i eq
    have h := both.2
    rw [eq] at h
    cases i <;> simp_all [finiteValid, resolve]

theorem resolved_export (r : Range) (s : SemanticRange) (meaning : decode r = some s) (n : Int) :
    exportWith resolve r n = some (member s n) := by
  rcases s with ⟨sl, su⟩
  rcases r with ⟨lo, hi⟩
  cases lo with
  | infinite =>
    cases hi with
    | infinite =>
      simp only [decode, decodeBound, pure] at meaning
      rcases meaning with ⟨rfl, rfl⟩
      rfl
    | finite i =>
      cases i <;> simp_all [decode, decodeBound, resolve, exportWith, member]
      all_goals rcases meaning with ⟨rfl, rfl⟩; rfl
  | finite i =>
    cases hi with
    | infinite =>
      cases i <;> simp_all [decode, decodeBound, resolve, exportWith, member]
      all_goals
        rcases meaning with ⟨rfl, rfl⟩
        simp only
        split <;> simp_all <;> omega
    | finite j =>
      cases i <;> cases j <;> simp_all [decode, decodeBound, resolve, exportWith, member]
      all_goals
        rcases meaning with ⟨rfl, rfl⟩
        simp only
        split <;> simp_all <;> omega

theorem admitted_export_total (r : Range) (valid : admitted r = true) (n : Int) :
    ∃ s, decode r = some s ∧ ordered s = true ∧ exportWith resolve r n = some (member s n) := by
  obtain ⟨s, meaning, order⟩ := (admission_iff r).mp valid
  exact ⟨s, meaning, order, resolved_export r s meaning n⟩

theorem representation_independent (a b : Range) (s : SemanticRange)
    (left : decode a = some s) (right : decode b = some s) (n : Int) :
    exportWith resolve a n = exportWith resolve b n := by
  rw [resolved_export a s left n, resolved_export b s right n]

theorem inclusive_endpoints (lo hi : Int) (order : lo ≤ hi) :
    member ⟨.finite lo, .finite hi⟩ lo = true ∧
    member ⟨.finite lo, .finite hi⟩ hi = true := by
  simp [member, order]

theorem boxed_resolvable_not_inline (n : Int) :
    resolve (.boxedResolved n) = some n ∧ inlineGet (.boxedResolved n) = none := by
  simp [resolve, inlineGet]

theorem admitted_boxed_old_failure (n : Int) :
    admitted ⟨.finite (.boxedResolved n), .finite (.boxedResolved n)⟩ = true ∧
    exportWith inlineGet ⟨.finite (.boxedResolved n), .finite (.boxedResolved n)⟩ n = none ∧
    exportWith resolve ⟨.finite (.boxedResolved n), .finite (.boxedResolved n)⟩ n = some true := by
  simp [admitted, finiteValid, finiteOrdered, resolve, inlineGet, exportWith]

#print axioms admitted_boxed_old_failure
#print axioms admission_iff
#print axioms every_finite_valid
#print axioms resolved_export
#print axioms admitted_export_total
#print axioms representation_independent
#print axioms inclusive_endpoints
#print axioms boxed_resolvable_not_inline
end CounterRangeRepresentation
