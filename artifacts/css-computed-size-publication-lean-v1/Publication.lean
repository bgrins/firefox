import Std

namespace SizePublication

inductive Effect where
  | family | textScale | size | inheritedZoom
  deriving DecidableEq, Repr

structure State where
  size : Nat
  published : Option Nat := none
  consumers : List Nat := []
  effects : List Effect := []
  deriving DecidableEq, Repr

inductive Event where
  | apply (effect : Effect) (result : Nat)
  | publish
  | consume
  deriving DecidableEq, Repr

def compatible (s : State) (value : Nat) : Bool :=
  s.published.all (· == value)

def step (s : State) : Event → Option State
  | .apply effect value =>
      if effect ∈ s.effects ∨ compatible s value = false then none
      else some { s with size := value, effects := effect :: s.effects }
  | .publish =>
      if s.published.isSome then none else some { s with published := some s.size }
  | .consume =>
      match s.published with
      | none => none
      | some value => some { s with consumers := value :: s.consumers }

def Safe (s : State) : Prop :=
  (∀ value, s.published = some value → value = s.size) ∧
  (∀ value ∈ s.consumers, value = s.size) ∧ s.effects.Nodup ∧
  (s.published = none → s.consumers = [])

theorem initial_safe (size : Nat) : Safe ⟨size, none, [], []⟩ := by
  simp [Safe]

theorem compatible_preserves_published (s : State) (value : Nat)
    (h : compatible s value = true) :
    ∀ old, s.published = some old → old = value := by
  intro old hp
  simpa [compatible, hp] using h

theorem step_preserves_safe (s t : State) (event : Event)
    (hs : Safe s) (ht : step s event = some t) : Safe t := by
  rcases hs with ⟨hp, hc, he, hnopub⟩
  cases event with
  | apply effect value =>
      simp only [step] at ht
      split at ht
      · contradiction
      · rename_i allowed
        have hn : effect ∉ s.effects := (not_or.mp allowed).1
        have hv : compatible s value = true := by simpa using (not_or.mp allowed).2
        cases ht
        refine ⟨compatible_preserves_published s value hv, ?_, List.nodup_cons.mpr ⟨hn, he⟩, hnopub⟩
        intro old member
        cases hpub : s.published with
        | none =>
            simp [hnopub hpub] at member
        | some frozen =>
            exact (hc old member).trans ((hp frozen hpub).symm.trans (compatible_preserves_published s value hv frozen hpub))
  | publish =>
      simp only [step] at ht
      split at ht
      · contradiction
      · cases ht
        exact ⟨by intro value h; cases h; rfl, hc, he, by simp⟩
  | consume =>
      simp only [step] at ht
      split at ht
      · contradiction
      · rename_i value hpub
        cases ht
        refine ⟨hp, ?_, he, by simp [hpub]⟩
        intro old member
        rcases List.mem_cons.mp member with rfl | member
        · exact hp _ hpub
        · exact hc old member

def run (s : State) : List Event → Option State
  | [] => some s
  | event :: rest => (step s event).bind (fun next => run next rest)

theorem accepted_trace_preserves_safe (events : List Event) (s t : State)
    (hs : Safe s) (ht : run s events = some t) : Safe t := by
  induction events generalizing s with
  | nil =>
      simp only [run, Option.some.injEq] at ht
      subst t
      exact hs
  | cons event rest ih =>
      simp only [run] at ht
      cases hstep : step s event with
      | none => simp [hstep] at ht
      | some next =>
          exact ih next (step_preserves_safe s next event hs hstep) (by simpa [hstep] using ht)

def used : State := ⟨20, some 20, [20], [.size]⟩

def invalidateAfterWrite (s : State) (value : Nat) : State :=
  { s with size := value, published := none }

theorem invalidation_does_not_repair_consumer :
    (invalidateAfterWrite used 30).consumers = [20] ∧
    (invalidateAfterWrite used 30).size = 30 := by decide

theorem late_invalidation_is_unsafe : ¬Safe (invalidateAfterWrite used 30) := by
  intro h
  have unequal : (20 : Nat) ≠ 30 := by decide
  exact unequal (h.2.1 20 (by decide))

theorem consumed_values_stable_after_trace (events : List Event) (s t : State)
    (hs : Safe s) (ht : run s events = some t) :
    ∀ value ∈ t.consumers, value = t.size :=
  (accepted_trace_preserves_safe events s t hs ht).2.1

theorem effects_unique_after_trace (events : List Event) (s t : State)
    (hs : Safe s) (ht : run s events = some t) : t.effects.Nodup :=
  (accepted_trace_preserves_safe events s t hs ht).2.2.1

theorem later_hook_change_rejected : step used (.apply .family 30) = none := by decide
theorem duplicate_size_effect_rejected : step used (.apply .size 20) = none := by decide
theorem stable_later_effect_allowed :
    step used (.apply .family 20) = some ⟨20, some 20, [20], [.family, .size]⟩ := by decide
theorem consume_requires_publication : step ⟨20, none, [], []⟩ .consume = none := by decide
theorem ordered_effects_complete :
    run ⟨10, none, [], []⟩ [.apply .family 12, .apply .textScale 15,
      .apply .size 20, .publish, .consume, .apply .inheritedZoom 20] =
      some ⟨20, some 20, [20], [.inheritedZoom, .size, .textScale, .family]⟩ := by decide

end SizePublication
