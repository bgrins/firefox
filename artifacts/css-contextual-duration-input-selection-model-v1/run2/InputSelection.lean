import Std

namespace InputSelection

inductive Owner | css | script
  deriving DecidableEq, Repr

structure Snapshot (D : Type) where
  cached : Option D
  applied : D
  owner : Owner
  deriving DecidableEq, Repr

def Coherent {D : Type} (s : Snapshot D) : Prop :=
  ∀ key, s.cached = some key → s.owner = .css → s.applied = key

abbrev Certified {D : Type} (required : D) (s : Snapshot D) : Prop :=
  s.cached = some required ∧ (s.owner = .css → s.applied = required)

def commit {D : Type} (s : Snapshot D) (captured selected : D) : Snapshot D :=
  { cached := some captured
    applied := if s.owner = .css then selected else s.applied
    owner := s.owner }

def verify {D : Type} [DecidableEq D]
    (s : Snapshot D) (captured selected : D) : Snapshot D :=
  if s.cached = some captured then s else commit s captured selected

theorem verify_certifies {D : Type} [DecidableEq D]
    (s : Snapshot D) (captured selected required : D)
    (old : Coherent s) (honestCapture : captured = required)
    (honestSelection : selected = required) :
    Certified required (verify s captured selected) := by
  subst captured
  subst selected
  by_cases equal : s.cached = some required
  · exact ⟨by simp [verify, equal],
           by simpa [verify, equal] using old required equal⟩
  · constructor
    · simp [verify, equal, commit]
    · intro css
      have owned : s.owner = .css := by simpa [verify, equal, commit] using css
      simp [verify, equal, commit, owned]

theorem changed_css_requires_selected_oracle {D : Type} [DecidableEq D]
    (s : Snapshot D) (required selected : D)
    (changed : s.cached ≠ some required) (css : s.owner = .css) :
    Certified required (verify s required selected) ↔ selected = required := by
  simp [Certified, verify, changed, commit, css]

theorem script_override_preserved {D : Type} [DecidableEq D]
    (s : Snapshot D) (captured selected : D) (script : s.owner = .script) :
    (verify s captured selected).applied = s.applied ∧
    (verify s captured selected).owner = .script := by
  by_cases equal : s.cached = some captured
  · simp [verify, equal, script]
  · simp [verify, equal, commit, script]

def initial : Snapshot Nat := ⟨some 1000, 1000, .css⟩
def hybrid24 : Snapshot Nat := verify initial 1500 2000

theorem cache_freshness_not_applied_correctness :
    hybrid24.cached = some 1500 ∧ hybrid24.applied = 2000 ∧
    ¬ Certified 1500 hybrid24 ∧
    (verify hybrid24 1500 1500).applied = 2000 ∧
    ¬ Certified 1500 (verify hybrid24 1500 1500) := by decide

structure VariableInput where
  declared : Nat
  animated : Option Nat
  tainted : Bool
  fallback : Nat
  deriving DecidableEq, Repr

def referenceValue (i : VariableInput) : Nat := i.animated.getD i.declared

def requiredDuration (i : VariableInput) : Nat :=
  if i.tainted then i.fallback else referenceValue i

def taintedInput (declared : Nat) : VariableInput :=
  ⟨declared, some 2500, true, 1500⟩

def untaintedInput (declared : Nat) : VariableInput :=
  ⟨declared, none, false, 1500⟩

theorem taint_fallback_is_input_obligation (a b fallback : Nat)
    (animatedA animatedB : Option Nat) :
    requiredDuration ⟨a, animatedA, true, fallback⟩ = fallback ∧
    requiredDuration ⟨b, animatedB, true, fallback⟩ = fallback := by
  simp [requiredDuration]

def erased : Snapshot Nat := verify initial 2000 2000

theorem taint_erased_snapshot_counterexample :
    Coherent erased ∧ erased.cached = some 2000 ∧ erased.applied = 2000 ∧
    ¬ Certified (requiredDuration (taintedInput 2000)) erased ∧
    requiredDuration (taintedInput 1000) = 1500 ∧
    requiredDuration (taintedInput 2000) = 1500 ∧
    Certified 1500 (verify initial 1500 1500) ∧
    requiredDuration (untaintedInput 1000) = 1000 ∧
    requiredDuration (untaintedInput 2000) = 2000 := by
  constructor
  · intro key equal css
    simpa [erased, verify, initial, commit] using equal
  · decide

end InputSelection
