import Std

namespace InterpolationProvenance

structure Value (P U : Type) where
  payload : P
  urlData : U
  tainted : Bool

def combine (op : P → P → Option P) (a b : Value P U) : Option (Value P U) :=
  match op a.payload b.payload with
  | none => none
  | some payload => some ⟨payload, a.urlData, a.tainted || b.tainted⟩

def firstOnly (op : P → P → Option P) (a b : Value P U) : Option (Value P U) :=
  match op a.payload b.payload with
  | none => none
  | some payload => some ⟨payload, a.urlData, a.tainted⟩

def optionalCombine (op : P → P → Option P) : Option (Value P U) → Option (Value P U) → Option (Option (Value P U))
  | some a, some b => (combine op a b).map some
  | none, none => some none
  | _, _ => none

def sample (op : P → P → Option P) (a b : Value P U) (right : Bool) : Value P U :=
  (combine op a b).getD (if right then b else a)

def evidence (inputs : List Bool) : Bool := inputs.any id

inductive Image where
  | none
  | url
  deriving DecidableEq, Repr

def bundleObserver (v : Value P U) : Image := if v.tainted then .none else .url
def directObserver (_v : Value P U) : Image := .url

theorem payload_preserved (op : P → P → Option P) (a b : Value P U) :
    (combine op a b).map Value.payload = op a.payload b.payload := by
  unfold combine
  cases op a.payload b.payload <;> rfl

theorem failure_unchanged (op : P → P → Option P) (a b : Value P U) :
    combine op a b = none ↔ op a.payload b.payload = none := by
  unfold combine
  cases op a.payload b.payload <;> simp

theorem successful_record (op : P → P → Option P) (a b : Value P U) (out : Value P U)
    (h : combine op a b = some out) :
    op a.payload b.payload = some out.payload ∧ out.urlData = a.urlData ∧
      out.tainted = evidence [a.tainted, b.tainted] := by
  unfold combine at h
  split at h
  · contradiction
  · cases h
    simp_all [evidence]

theorem either_input_retained (op : P → P → Option P) (a b : Value P U) (out : Value P U)
    (h : combine op a b = some out) (ht : a.tainted = true ∨ b.tainted = true) :
    out.tainted = true := by
  obtain ⟨_, _, ht'⟩ := successful_record op a b out h
  rw [ht']
  rcases ht with ht | ht <;> simp [evidence, ht]

theorem clean_inputs_remain_clean (op : P → P → Option P) (a b : Value P U) (out : Value P U)
    (h : combine op a b = some out) (ha : a.tainted = false) (hb : b.tainted = false) :
    out.tainted = false := by
  obtain ⟨_, _, ht⟩ := successful_record op a b out h
  simp [ht, evidence, ha, hb]

theorem failed_discrete_selection (op : P → P → Option P) (a b : Value P U) (right : Bool)
    (h : op a.payload b.payload = none) :
    sample op a b right = if right then b else a := by
  simp [sample, combine, h]

theorem optional_invalid_pair (op : P → P → Option P) :
    optionalCombine (U := U) op none none = some none := rfl

theorem optional_mismatch (op : P → P → Option P) (a : Value P U) :
    optionalCombine op (some a) none = none ∧ optionalCombine op none (some a) = none := by
  exact ⟨rfl, rfl⟩

theorem old_failure_same (op : P → P → Option P) (a b : Value P U)
    (h : op a.payload b.payload = none) : firstOnly op a b = combine op a b := by
  simp [firstOnly, combine, h]

theorem bundle_rejects_either (op : P → P → Option P) (a b : Value P U) (out : Value P U)
    (h : combine op a b = some out) (ht : a.tainted = true ∨ b.tainted = true) :
    bundleObserver out = .none ∧ directObserver out = .url := by
  simp [bundleObserver, directObserver, either_input_retained op a b out h ht]

theorem clean_bundle_accepts (op : P → P → Option P) (a b : Value P U) (out : Value P U)
    (h : combine op a b = some out) (ha : a.tainted = false) (hb : b.tainted = false) :
    bundleObserver out = .url := by
  simp [bundleObserver, clean_inputs_remain_clean op a b out h ha hb]

inductive Expr (P U : Type) where
  | leaf : Value P U → Expr P U
  | pair : Expr P U → Expr P U → Expr P U

def Expr.origins : Expr P U → List Bool
  | .leaf v => [v.tainted]
  | .pair a b => a.origins ++ b.origins

def Expr.eval (op : P → P → Option P) : Expr P U → Option (Value P U)
  | .leaf v => some v
  | .pair a b => do combine op (← a.eval op) (← b.eval op)

theorem finite_success_provenance (op : P → P → Option P) (e : Expr P U) (out : Value P U)
    (h : e.eval op = some out) : out.tainted = evidence e.origins := by
  induction e generalizing out with
  | leaf v =>
    have hv : v = out := by simpa [Expr.eval] using h
    subst out
    simp [Expr.origins, evidence]
  | pair a b ia ib =>
    cases ha : a.eval op with
    | none => simp [Expr.eval, ha] at h
    | some va =>
      cases hb : b.eval op with
      | none => simp [Expr.eval, ha, hb] at h
      | some vb =>
        have hc : combine op va vb = some out := by simpa [Expr.eval, ha, hb] using h
        obtain ⟨_, _, ht⟩ := successful_record op va vb out hc
        rw [ht]
        simp [Expr.origins, evidence, ia va ha, ib vb hb, List.any_append]

def clean : Value Nat Unit := ⟨12, (), false⟩
def dirty : Value Nat Unit := ⟨8, (), true⟩
def sum (a b : Nat) : Option Nat := some (a + b)

theorem repaired_witness : (combine sum clean dirty).map bundleObserver = some .none := rfl
theorem omission_witness : (firstOnly sum clean dirty).map bundleObserver = some .url := rfl
theorem distinct_observers : (combine sum clean dirty).map bundleObserver ≠
    (firstOnly sum clean dirty).map bundleObserver := by decide

#print axioms payload_preserved
#print axioms failure_unchanged
#print axioms successful_record
#print axioms either_input_retained
#print axioms clean_inputs_remain_clean
#print axioms failed_discrete_selection
#print axioms optional_invalid_pair
#print axioms optional_mismatch
#print axioms old_failure_same
#print axioms bundle_rejects_either
#print axioms clean_bundle_accepts
#print axioms finite_success_provenance
#print axioms repaired_witness
#print axioms omission_witness
#print axioms distinct_observers

end InterpolationProvenance
