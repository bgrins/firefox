namespace RegisteredNumber

inductive Unit where
  | px | em
  deriving DecidableEq, Repr

inductive Dim where
  | number | length
  deriving DecidableEq, Repr

inductive Raw where
  | number (n : Nat)
  | length (unit : Unit) (n : Nat)
  | quotient (left right : Raw)
  | sum (left right : Raw)
  deriving DecidableEq, Repr

def quotientDim : Dim → Dim → Option Dim
  | .number, .number => some .number
  | .length, .length => some .number
  | .length, .number => some .length
  | .number, .length => none

def infer : Raw → Option Dim
  | .number _ => some .number
  | .length _ _ => some .length
  | .quotient a b => do quotientDim (← infer a) (← infer b)
  | .sum a b => do
      let da ← infer a
      let db ← infer b
      if da = db then some da else none

def needsFont : Raw → Bool
  | .number _ => false
  | .length u _ => u == .em
  | .quotient a b | .sum a b => needsFont a || needsFont b

structure Admitted where
  raw : Raw
  valid : infer raw = some .number

def admit (raw : Raw) : Option Admitted :=
  if h : infer raw = some .number then some ⟨raw, h⟩ else none

inductive Provider where
  | ready (raw : Raw)
  | invalid
  | pending
  deriving DecidableEq, Repr

inductive Expr where
  | value (raw : Raw)
  | reference (key : Nat) (fallback : Expr)
  deriving DecidableEq, Repr

inductive Selected where
  | value (raw : Raw)
  | demand (key : Nat)
  deriving DecidableEq, Repr

def select (env : Nat → Provider) : Expr → Selected
  | .value raw => .value raw
  | .reference k fallback =>
      match env k with
      | .ready raw => .value raw
      | .invalid => select env fallback
      | .pending => .demand k

inductive Plan where
  | invalid
  | ready (raw : Raw) (font : Bool)
  | demand (key : Nat)
  deriving DecidableEq, Repr

def planRaw (raw : Raw) : Plan :=
  match admit raw with
  | none => .invalid
  | some admitted => .ready admitted.raw (needsFont admitted.raw)

def plan (env : Nat → Provider) (expr : Expr) : Plan :=
  match select env expr with
  | .value raw => planRaw raw
  | .demand k => .demand k

def scheduledFont : Plan → Bool
  | .ready _ font => font
  | _ => false

def eagerFlags : Expr → Bool
  | .value raw => needsFont raw
  | .reference _ fallback => eagerFlags fallback

def hasReference : Expr → Bool
  | .value _ => false
  | .reference _ _ => true

def seedMutation (env : Nat → Provider) (e : Expr) : Bool :=
  eagerFlags e || scheduledFont (plan env e)

def visitorMutation (env : Nat → Provider) (e : Expr) : Bool :=
  (hasReference e && eagerFlags e) || scheduledFont (plan env e)

def typeMaskMutation (_env : Nat → Provider) (_e : Expr) : Bool := false

def selectedTokenMutation (env : Nat → Provider) (e : Expr) : Bool :=
  match select env e with
  | .value raw => needsFont raw
  | .demand _ => false

theorem admit_sound {r : Raw} {a : Admitted} (h : admit r = some a) :
    a.raw = r ∧ infer r = some .number := by
  unfold admit at h
  split at h
  next good => cases h; exact ⟨rfl, good⟩
  next => contradiction

theorem admit_complete (r : Raw) (h : infer r = some .number) :
    ∃ a, admit r = some a ∧ a.raw = r := by
  exact ⟨⟨r, h⟩, by simp [admit, h], rfl⟩

theorem rejected_has_no_schedule (r : Raw) (h : infer r ≠ some .number) :
    planRaw r = .invalid ∧ scheduledFont (planRaw r) = false := by
  simp [planRaw, admit, h, scheduledFont]

theorem admitted_schedule_exact (r : Raw) (h : infer r = some .number) :
    planRaw r = .ready r (needsFont r) := by
  simp [planRaw, admit, h]

theorem ready_requires_admission {r out : Raw} {font : Bool}
    (h : planRaw r = .ready out font) :
    out = r ∧ infer r = some .number ∧ font = needsFont r := by
  by_cases good : infer r = some .number
  · simp [planRaw, admit, good] at h
    exact ⟨h.1.symm, good, h.2.symm⟩
  · simp [planRaw, admit, good] at h

theorem ready_excludes_fallback (env : Nat → Provider) (k : Nat) (r : Raw)
    (fallback : Expr) (h : env k = .ready r) :
    plan env (.reference k fallback) = planRaw r := by
  simp [plan, select, h]

theorem fallback_replacement_invariant (env : Nat → Provider) (k : Nat) (r : Raw)
    (a b : Expr) (h : env k = .ready r) :
    plan env (.reference k a) = plan env (.reference k b) := by
  simp [ready_excludes_fallback env k r _ h]

theorem invalid_uses_fallback (env : Nat → Provider) (k : Nat)
    (fallback : Expr) (h : env k = .invalid) :
    plan env (.reference k fallback) = plan env fallback := by
  simp [plan, select, h]

theorem pending_is_not_invalid (env : Nat → Provider) (k : Nat)
    (fallback : Expr) (h : env k = .pending) :
    plan env (.reference k fallback) = .demand k := by
  simp [plan, select, h]

theorem wrong_type_ready_does_not_retry (env : Nat → Provider) (k : Nat)
    (r : Raw) (fallback : Expr) (h : env k = .ready r)
    (bad : infer r ≠ some .number) :
    plan env (.reference k fallback) = .invalid := by
  rw [ready_excludes_fallback env k r fallback h]
  exact (rejected_has_no_schedule r bad).1

theorem selection_refinement (a b : Nat → Provider) (x y : Expr)
    (h : select a x = select b y) : plan a x = plan b y := by
  simp only [plan, h]

theorem bare_length_rejected (u : Unit) (n : Nat) :
    planRaw (.length u n) = .invalid := by
  simp [planRaw, admit, infer]

theorem length_ratio_admitted (u v : Unit) (n d : Nat) :
    planRaw (.quotient (.length u n) (.length v d)) =
      .ready (.quotient (.length u n) (.length v d)) ((u == .em) || (v == .em)) := by
  simp [planRaw, admit, infer, quotientDim, needsFont]

theorem relative_ratio_requires_font (n d : Nat) :
    scheduledFont (planRaw (.quotient (.length .em n) (.length .px d))) = true := by
  simp [length_ratio_admitted, scheduledFont]

theorem selected_invalid_length_no_context (env : Nat → Provider)
    (e : Expr) (u : Unit) (n : Nat) (h : select env e = .value (.length u n)) :
    plan env e = .invalid := by
  simp [plan, h, bare_length_rejected]

def eval (font : Nat) : Raw → Nat
  | .number n => n
  | .length .px n => n
  | .length .em n => n * font
  | .quotient a b => eval font a / eval font b
  | .sum a b => eval font a + eval font b

theorem no_font_leaves_is_context_independent (r : Raw) (a b : Nat)
    (h : needsFont r = false) : eval a r = eval b r := by
  induction r with
  | number n => rfl
  | length u n => cases u <;> simp_all [needsFont, eval]
  | quotient x y hx hy =>
      simp only [needsFont, Bool.or_eq_false_iff] at h
      simp [eval, hx h.1, hy h.2]
  | sum x y hx hy =>
      simp only [needsFont, Bool.or_eq_false_iff] at h
      simp [eval, hx h.1, hy h.2]

theorem numeric_ratio_uses_current_font (font : Nat) :
    eval font (.quotient (.length .em 1) (.length .px 1)) = font := by
  simp [eval]

inductive CycleDecision where
  | invalidate | defer | retain
  deriving DecidableEq, Repr

def withCyclePolicy (policy : Plan → CycleDecision) (p : Plan) : Bool × CycleDecision :=
  (scheduledFont p, policy p)

theorem scheduling_independent_of_cycle_policy
    (a b : Plan → CycleDecision) (p : Plan) :
    (withCyclePolicy a p).1 = (withCyclePolicy b p).1 := rfl

theorem seed_false_edge_general (env : Nat → Provider) (n : Nat) :
    seedMutation env (.value (.length .em n)) = true ∧
    scheduledFont (plan env (.value (.length .em n))) = false := by
  simp [seedMutation, eagerFlags, needsFont, plan, select, bare_length_rejected, scheduledFont]

theorem visitor_false_edge_general (env : Nat → Provider) (k n : Nat)
    (fallback : Expr) (ready : env k = .ready (.number n))
    (flagged : eagerFlags fallback = true) :
    visitorMutation env (.reference k fallback) = true ∧
    scheduledFont (plan env (.reference k fallback)) = false := by
  simp [visitorMutation, hasReference, eagerFlags, flagged,
    ready_excludes_fallback env k (.number n) fallback ready,
    planRaw, admit, infer, needsFont, scheduledFont]

end RegisteredNumber
