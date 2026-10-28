namespace LinearPositionGuard

inductive Position where
  | absent
  | known
  | deferred
  deriving DecidableEq, Repr

open Position

def suppliedResolves : Position → Bool
  | deferred => false
  | _ => true

def oldGuard : Position → Position → Bool
  | absent, second => suppliedResolves second
  | known, _ => true
  | deferred, _ => false

def fixedGuard (first second : Position) : Bool :=
  suppliedResolves first && suppliedResolves second

def allPresentResolve (first second : Position) : Prop :=
  (first ≠ absent → first = known) ∧
  (second ≠ absent → second = known)

instance (first second : Position) : Decidable (allPresentResolve first second) :=
  inferInstanceAs (Decidable ((_ → _) ∧ (_ → _)))

theorem fixed_guard_exact (first second : Position) :
    fixedGuard first second = true ↔ allPresentResolve first second := by
  cases first <;> cases second <;> decide

theorem old_first_present_counterexample :
    oldGuard known deferred = true ∧ ¬allPresentResolve known deferred := by
  decide

theorem fixed_never_expands_acceptance (first second : Position) :
    fixedGuard first second = true → oldGuard first second = true := by
  cases first <;> cases second <;> decide

theorem optional_known_inputs_preserved (first second : Position)
    (h : allPresentResolve first second) :
    fixedGuard first second = true ∧ oldGuard first second = true := by
  have fixed := (fixed_guard_exact first second).mpr h
  exact ⟨fixed, fixed_never_expands_acceptance first second fixed⟩

end LinearPositionGuard
