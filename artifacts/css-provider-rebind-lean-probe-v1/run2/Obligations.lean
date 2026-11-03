import Std

namespace AnimationObligations

abbrev Stamp := Nat × Nat

structure Effect where
  target : Nat
  sensitive : Bool
  built : Option Stamp
  pending : Bool
  deriving DecidableEq, Repr

structure State where
  context : Nat → Nat
  ordinary : Nat → Nat
  ordinaryPending : Nat → Bool
  effects : Nat → Option Effect
  animationPending : Bool

def initial : State :=
  ⟨fun _ => 0, fun _ => 0, fun _ => false, fun _ => none, false⟩

def change (s : State) (target : Nat) : State :=
  { s with
    context := fun t => if t = target then s.context t + 1 else s.context t
    ordinaryPending := fun t => if t = target then true else s.ordinaryPending t
    effects := fun i => (s.effects i).map fun e =>
      if e.target = target ∧ e.sensitive = true then { e with pending := true } else e }

def register (s : State) (id target : Nat) (sensitive : Bool) : State :=
  { s with effects := fun i => if i = id then
      match s.effects i with
      | none => some ⟨target, sensitive, none, true⟩
      | some e => some e
    else s.effects i }

def cancel (s : State) (id : Nat) : State :=
  { s with effects := fun i => if i = id then none else s.effects i
           animationPending := true }

def retarget (s : State) (id target : Nat) : State :=
  { s with effects := fun i => if i = id then
      (s.effects i).map fun e => { e with target := target, pending := true }
    else s.effects i }

def cascade (s : State) : State :=
  { s with ordinary := fun t => if s.ordinaryPending t then s.context t else s.ordinary t
           ordinaryPending := fun _ => false }

def animationPass (s : State) : State :=
  if s.animationPending then { cascade s with animationPending := false } else s

def normalPass (s : State) : State :=
  { cascade s with effects := fun i => (s.effects i).map fun e =>
      if e.pending then { e with built := some (e.target, s.context e.target), pending := false }
      else e }

def drain (s : State) : State := normalPass (animationPass s)

def OrdinaryConserved (s : State) : Prop :=
  ∀ t, s.ordinary t = s.context t ∨ s.ordinaryPending t = true

def EffectsConserved (s : State) : Prop :=
  ∀ i e, s.effects i = some e → e.sensitive = true →
    e.built = some (e.target, s.context e.target) ∨ e.pending = true

def Conserved (s : State) : Prop := OrdinaryConserved s ∧ EffectsConserved s

def Fresh (s : State) : Prop :=
  (∀ t, s.ordinary t = s.context t) ∧
  (∀ i e, s.effects i = some e → e.sensitive = true →
    e.built = some (e.target, s.context e.target))

theorem initial_conserved : Conserved initial := by
  simp [Conserved, OrdinaryConserved, EffectsConserved, initial]

theorem change_conserved (s : State) (target : Nat) (h : Conserved s) :
    Conserved (change s target) := by
  constructor
  · intro t
    by_cases ht : t = target
    · simp [change, ht]
    · simpa [change, ht] using h.1 t
  · intro i e he hs
    cases old : s.effects i with
    | none => simp [change, old] at he
    | some prior =>
      by_cases hit : prior.target = target ∧ prior.sensitive = true
      · simp [change, old, hit] at he
        subst e
        simp
      · simp [change, old, hit] at he
        subst e
        have ne : prior.target ≠ target := by
          intro eq
          exact hit ⟨eq, hs⟩
        simpa [change, ne] using h.2 i prior old hs

theorem register_conserved (s : State) (id target : Nat) (sensitive : Bool)
    (h : Conserved s) : Conserved (register s id target sensitive) := by
  refine ⟨h.1, ?_⟩
  intro i e he hs
  by_cases hi : i = id
  · subst i
    cases old : s.effects id with
    | none =>
      simp [register, old] at he
      subst e
      simp
    | some prior =>
      simp [register, old] at he
      subst e
      exact h.2 id prior old hs
  · exact h.2 i e (by simpa [register, hi] using he) hs

theorem cancel_conserved (s : State) (id : Nat) (h : Conserved s) :
    Conserved (cancel s id) := by
  refine ⟨h.1, ?_⟩
  intro i e he hs
  by_cases hi : i = id
  · simp [cancel, hi] at he
  · exact h.2 i e (by simpa [cancel, hi] using he) hs

theorem retarget_conserved (s : State) (id target : Nat) (h : Conserved s) :
    Conserved (retarget s id target) := by
  refine ⟨h.1, ?_⟩
  intro i e he hs
  by_cases hi : i = id
  · subst i
    cases old : s.effects id with
    | none => simp [retarget, old] at he
    | some prior =>
      simp [retarget, old] at he
      subst e
      simp
  · exact h.2 i e (by simpa [retarget, hi] using he) hs

theorem cascade_fresh_ordinary (s : State) (h : OrdinaryConserved s) :
    ∀ t, (cascade s).ordinary t = (cascade s).context t := by
  intro t
  cases hp : s.ordinaryPending t with
  | true => simp [cascade, hp]
  | false =>
    have eq := h t
    simpa [cascade, hp] using eq

theorem animation_conserved (s : State) (h : Conserved s) :
    Conserved (animationPass s) := by
  cases hp : s.animationPending with
  | false => simpa [animationPass, hp] using h
  | true =>
    constructor
    · intro t
      left
      simpa [animationPass, hp] using cascade_fresh_ordinary s h.1 t
    · simpa [animationPass, hp, EffectsConserved, cascade] using h.2

theorem normal_fresh (s : State) (h : Conserved s) : Fresh (normalPass s) := by
  refine ⟨cascade_fresh_ordinary s h.1, ?_⟩
  intro i e he hs
  cases old : s.effects i with
  | none => simp [normalPass, old] at he
  | some prior =>
    cases hp : prior.pending with
    | true =>
      simp [normalPass, old, hp] at he
      subst e
      rfl
    | false =>
      simp [normalPass, old, hp] at he
      subst e
      have eq := h.2 i prior old hs
      simpa [normalPass, cascade, hp] using eq

theorem fresh_conserved (s : State) (h : Fresh s) : Conserved s :=
  ⟨fun t => Or.inl (h.1 t), fun i e he hs => Or.inl (h.2 i e he hs)⟩

inductive Event where
  | change (target : Nat)
  | register (id target : Nat) (sensitive : Bool)
  | cancel (id : Nat)
  | retarget (id target : Nat)
  | animationPass
  | normalPass
  deriving DecidableEq, Repr

def step (s : State) : Event → State
  | .change target => change s target
  | .register id target sensitive => register s id target sensitive
  | .cancel id => cancel s id
  | .retarget id target => retarget s id target
  | .animationPass => animationPass s
  | .normalPass => normalPass s

def run (s : State) (events : List Event) : State := events.foldl step s

theorem step_conserved (s : State) (event : Event) (h : Conserved s) :
    Conserved (step s event) := by
  cases event with
  | change t => exact change_conserved s t h
  | register i t b => exact register_conserved s i t b h
  | cancel i => exact cancel_conserved s i h
  | retarget i t => exact retarget_conserved s i t h
  | animationPass => exact animation_conserved s h
  | normalPass => exact fresh_conserved _ (normal_fresh s h)

theorem run_conserved (events : List Event) (s : State) (h : Conserved s) :
    Conserved (run s events) := by
  induction events generalizing s with
  | nil => exact h
  | cons event events ih => exact ih _ (step_conserved s event h)

theorem finite_batch_drains_fresh (events : List Event) :
    Fresh (drain (run initial events)) :=
  normal_fresh _ (animation_conserved _ (run_conserved events initial initial_conserved))

theorem cancel_preserves_other_effect (s : State) (cancelled survivor : Nat)
    (h : survivor ≠ cancelled) : (cancel s cancelled).effects survivor = s.effects survivor := by
  simp [cancel, h]

theorem drain_preserves_context (s : State) : (drain s).context = s.context := by
  cases h : s.animationPending <;> simp [drain, normalPass, animationPass, cascade, h]

def changes (target : Nat) : List Event → Nat
  | [] => 0
  | event :: rest => (if event = .change target then 1 else 0) + changes target rest

theorem step_context (s : State) (event : Event) (target : Nat) :
    (step s event).context target =
      s.context target + if event = .change target then 1 else 0 := by
  cases event <;> simp [step, change, register, cancel, retarget, normalPass, cascade]
  · rename_i other
    by_cases h : target = other
    · simp [h]
    · simp [h, Ne.symm h]
  · cases h : s.animationPending <;> simp [animationPass, cascade, h]

theorem run_context_count (events : List Event) (s : State) (target : Nat) :
    (run s events).context target = s.context target + changes target events := by
  induction events generalizing s with
  | nil => simp [run, changes]
  | cons event events ih =>
    change (run (step s event) events).context target = _
    rw [ih, step_context]
    simp [changes, Nat.add_assoc]

theorem surviving_effect_latest (events : List Event) (id : Nat) (e : Effect)
    (alive : (drain (run initial events)).effects id = some e)
    (sensitive : e.sensitive = true) :
    e.built = some (e.target, changes e.target events) := by
  have h := (finite_batch_drains_fresh events).2 id e alive sensitive
  rw [drain_preserves_context, run_context_count] at h
  simpa [initial] using h

theorem ordinary_latest (events : List Event) (target : Nat) :
    (drain (run initial events)).ordinary target = changes target events := by
  have h := (finite_batch_drains_fresh events).1 target
  rw [drain_preserves_context, run_context_count] at h
  simpa [initial] using h

theorem retarget_preserves_other_effect (s : State) (moved survivor target : Nat)
    (h : survivor ≠ moved) :
    (retarget s moved target).effects survivor = s.effects survivor := by
  simp [retarget, h]

end AnimationObligations

