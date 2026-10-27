import Watches

namespace AttributeWatchBits

structure BitWatch where
  target : Nat
  sensitive : Bool
  deriving DecidableEq, Repr

structure BitState where
  watches : List (Nat × BitWatch)
  pending : List Nat
  deriving DecidableEq, Repr

def abstractWatch (w : AttributeWatches.Watch) : BitWatch :=
  ⟨w.target, !w.names.isEmpty⟩

def abstractPair (pair : Nat × AttributeWatches.Watch) : Nat × BitWatch :=
  (pair.1, abstractWatch pair.2)

def empty : BitState := ⟨[], []⟩

def install (s : BitState) (id : Nat) (e : AttributeWatches.Entry) : BitState :=
  ⟨(id, abstractWatch (AttributeWatches.publish e)) :: AttributeWatches.eraseId id s.watches,
   s.pending⟩

def remove (s : BitState) (id : Nat) : BitState :=
  ⟨AttributeWatches.eraseId id s.watches, s.pending⟩

def watching (s : BitState) (target : Nat) : Bool :=
  s.watches.any fun pair => pair.2.target == target && pair.2.sensitive

def change (s : BitState) (target : Nat) : BitState :=
  { s with pending := if watching s target then target :: s.pending else s.pending }

def Simulates (fine : AttributeWatches.State) (coarse : BitState) : Prop :=
  coarse.watches = fine.published.map abstractPair ∧
  ∀ target, target ∈ fine.pending → target ∈ coarse.pending

theorem erase_abstract (xs : List (Nat × AttributeWatches.Watch)) (id : Nat) :
    AttributeWatches.eraseId id (xs.map abstractPair) =
      (AttributeWatches.eraseId id xs).map abstractPair := by
  induction xs with
  | nil => rfl
  | cons pair rest ih =>
    simp only [AttributeWatches.eraseId] at *
    by_cases h : pair.1 = id <;> simp [abstractPair, h, ih]

theorem nonempty_query_sensitive (w : AttributeWatches.Watch) (name : Nat)
    (h : name ∈ w.names) : (abstractWatch w).sensitive = true := by
  cases w with
  | mk target names =>
    cases names with
    | nil => simp at h
    | cons first rest => rfl

theorem named_watch_implies_bit (fine : AttributeWatches.State) (coarse : BitState)
    (target name : Nat) (related : Simulates fine coarse)
    (hit : AttributeWatches.watching fine target name = true) : watching coarse target = true := by
  obtain ⟨pair, member, matched⟩ := List.any_eq_true.mp hit
  have parts : (pair.2.target == target) = true ∧ pair.2.names.contains name = true := by
    simpa only [Bool.and_eq_true] using matched
  have queried : name ∈ pair.2.names := List.contains_iff_mem.mp parts.2
  apply List.any_eq_true.mpr
  refine ⟨abstractPair pair, ?_, ?_⟩
  · rw [related.1]
    exact List.mem_map.mpr ⟨pair, member, rfl⟩
  · have sensitive := nonempty_query_sensitive pair.2 name queried
    change (pair.2.target == target && (abstractWatch pair.2).sensitive) = true
    simp only [sensitive, Bool.and_true]
    exact parts.1

theorem empty_simulates : Simulates AttributeWatches.empty empty := by
  constructor
  · rfl
  · intro target member; simp [AttributeWatches.empty] at member

theorem install_simulates (fine : AttributeWatches.State) (coarse : BitState)
    (id : Nat) (e : AttributeWatches.Entry) (h : Simulates fine coarse) :
    Simulates (AttributeWatches.install fine id e) (install coarse id e) := by
  constructor
  · simp only [install, AttributeWatches.install, List.map_cons]
    rw [h.1, erase_abstract]
    rfl
  · exact h.2

theorem remove_simulates (fine : AttributeWatches.State) (coarse : BitState)
    (id : Nat) (h : Simulates fine coarse) :
    Simulates (AttributeWatches.remove fine id) (remove coarse id) := by
  constructor
  · simp only [remove, AttributeWatches.remove]
    rw [h.1, erase_abstract]
  · exact h.2

theorem change_keeps_pending (s : BitState) (changed target : Nat)
    (h : target ∈ s.pending) : target ∈ (change s changed).pending := by
  simp only [change]
  split <;> simp [h]

theorem bit_hit_admits (s : BitState) (target : Nat) (h : watching s target = true) :
    target ∈ (change s target).pending := by
  simp [change, h]

theorem change_simulates (fine : AttributeWatches.State) (coarse : BitState)
    (target name : Nat) (h : Simulates fine coarse) :
    Simulates (AttributeWatches.change fine target name) (change coarse target) := by
  constructor
  · exact h.1
  · intro queried member
    by_cases hit : AttributeWatches.watching fine target name = true
    · have coarseHit := named_watch_implies_bit fine coarse target name h hit
      simp only [AttributeWatches.change, hit, ↓reduceIte, List.mem_cons] at member
      rcases member with same | prior
      · subst queried
        exact bit_hit_admits coarse target coarseHit
      · exact change_keeps_pending coarse target queried (h.2 queried prior)
    · have prior : queried ∈ fine.pending := by
        simpa [AttributeWatches.change, hit] using member
      exact change_keeps_pending coarse target queried (h.2 queried prior)

def step (s : BitState) : AttributeWatches.Event → BitState
  | .install id e => install s id e
  | .remove id => remove s id
  | .change target _ => change s target

def run (events : List AttributeWatches.Event) : BitState := events.foldl step empty

theorem step_simulates (fine : AttributeWatches.State) (coarse : BitState)
    (event : AttributeWatches.Event) (h : Simulates fine coarse) :
    Simulates (AttributeWatches.step fine event) (step coarse event) := by
  cases event with
  | install id e => exact install_simulates fine coarse id e h
  | remove id => exact remove_simulates fine coarse id h
  | change target name => exact change_simulates fine coarse target name h

theorem finite_history_simulates (events : List AttributeWatches.Event) :
    Simulates (AttributeWatches.run events) (run events) := by
  have general : ∀ (xs : List AttributeWatches.Event) fine coarse,
      Simulates fine coarse → Simulates (xs.foldl AttributeWatches.step fine) (xs.foldl step coarse) := by
    intro xs
    induction xs with
    | nil => intro fine coarse h; exact h
    | cons event rest ih => intro fine coarse h; exact ih _ _ (step_simulates fine coarse event h)
  exact general events AttributeWatches.empty empty empty_simulates

theorem queried_mutation_admitted (events : List AttributeWatches.Event) (id : Nat)
    (e : AttributeWatches.Entry) (q : AttributeWatches.Query)
    (active : (id, e) ∈ (AttributeWatches.run events).active) (queried : q ∈ e.queries) :
    e.target ∈ (change (run events) e.target).pending := by
  exact bit_hit_admits _ _ (named_watch_implies_bit _ _ _ _
    (finite_history_simulates events) (AttributeWatches.finite_history_covers events id e q active queried))

theorem absent_mutation_admitted (events : List AttributeWatches.Event) (id : Nat)
    (e : AttributeWatches.Entry) (name : Nat)
    (active : (id, e) ∈ (AttributeWatches.run events).active)
    (queried : (⟨name, none⟩ : AttributeWatches.Query) ∈ e.queries) :
    e.target ∈ (change (run events) e.target).pending :=
  queried_mutation_admitted events id e ⟨name, none⟩ active queried

theorem survivor_mutation_admitted (events : List AttributeWatches.Event) (removed survivor : Nat)
    (e : AttributeWatches.Entry) (q : AttributeWatches.Query) (different : survivor ≠ removed)
    (active : (survivor, e) ∈ (AttributeWatches.run events).active) (queried : q ∈ e.queries) :
    e.target ∈ (change (remove (run events) removed) e.target).pending := by
  have fineHit := AttributeWatches.other_effect_keeps_coverage _ removed survivor e q
    (AttributeWatches.finite_history_published events) different active queried
  exact bit_hit_admits _ _ (named_watch_implies_bit _ _ _ _
    (remove_simulates _ _ removed (finite_history_simulates events)) fineHit)

end AttributeWatchBits
