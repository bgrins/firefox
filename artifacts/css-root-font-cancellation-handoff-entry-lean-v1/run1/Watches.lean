import Obligations

namespace AttributeWatches

structure Query where
  name : Nat
  value : Option Nat
  deriving DecidableEq, Repr

structure Entry where
  target : Nat
  endpoint : Nat
  queries : List Query
  deriving DecidableEq, Repr

structure Watch where
  target : Nat
  names : List Nat
  deriving DecidableEq, Repr

structure State where
  active : List (Nat × Entry)
  published : List (Nat × Watch)
  pending : List Nat
  deriving DecidableEq, Repr

def empty : State := ⟨[], [], []⟩
def publish (e : Entry) : Watch := ⟨e.target, e.queries.map Query.name⟩
def eraseId {α : Type} (id : Nat) (xs : List (Nat × α)) : List (Nat × α) :=
  xs.filter fun pair => pair.1 != id

def install (s : State) (id : Nat) (e : Entry) : State :=
  ⟨(id, e) :: eraseId id s.active, (id, publish e) :: eraseId id s.published, s.pending⟩

def remove (s : State) (id : Nat) : State :=
  ⟨eraseId id s.active, eraseId id s.published, s.pending⟩

def watching (s : State) (target name : Nat) : Bool :=
  s.published.any fun pair => pair.2.target == target && pair.2.names.contains name

def change (s : State) (target name : Nat) : State :=
  { s with pending := if watching s target name then target :: s.pending else s.pending }

def Published (s : State) : Prop :=
  s.published = s.active.map fun pair => (pair.1, publish pair.2)

def entryAt (s : State) (id : Nat) : Option Entry :=
  (s.active.find? fun pair => pair.1 == id).map Prod.snd

def watchAt (s : State) (id : Nat) : Option Watch :=
  (s.published.find? fun pair => pair.1 == id).map Prod.snd

theorem erase_map (xs : List (Nat × Entry)) (id : Nat) :
    eraseId id (xs.map fun pair => (pair.1, publish pair.2)) =
      (eraseId id xs).map fun pair => (pair.1, publish pair.2) := by
  induction xs with
  | nil => rfl
  | cons pair rest ih =>
    simp only [eraseId] at *
    by_cases h : pair.1 = id <;> simp [h, ih]

theorem empty_published : Published empty := rfl

theorem install_published (s : State) (id : Nat) (e : Entry) (h : Published s) :
    Published (install s id e) := by
  simp only [Published, install, List.map_cons]
  rw [h, erase_map]

theorem remove_published (s : State) (id : Nat) (h : Published s) :
    Published (remove s id) := by
  simp only [Published, remove]
  rw [h, erase_map]

theorem change_published (s : State) (target name : Nat) (h : Published s) :
    Published (change s target name) := h

theorem published_covers_query (s : State) (id : Nat) (e : Entry) (q : Query)
    (h : Published s) (active : (id, e) ∈ s.active) (queried : q ∈ e.queries) :
    watching s e.target q.name = true := by
  have names : q.name ∈ (publish e).names := List.mem_map.mpr ⟨q, queried, rfl⟩
  have member : (id, publish e) ∈ s.published := by
    rw [h]
    exact List.mem_map.mpr ⟨(id, e), active, rfl⟩
  simp only [watching, List.any_eq_true]
  exact ⟨(id, publish e), member, by
    simp only [Bool.and_eq_true, List.contains_iff_mem]
    exact ⟨by simp [publish], names⟩⟩

theorem missing_read_is_published (e : Entry) (name : Nat)
    (h : (⟨name, none⟩ : Query) ∈ e.queries) : name ∈ (publish e).names :=
  List.mem_map.mpr ⟨⟨name, none⟩, h, rfl⟩

theorem install_replaces_watch (s : State) (id : Nat) (e : Entry) :
    watchAt (install s id e) id = some (publish e) := by
  simp [watchAt, install]

theorem endpoint_irrelevant_to_publication (e : Entry) (value : Nat) :
    publish { e with endpoint := value } = publish e := rfl

theorem remove_preserves_other_watch (s : State) (removed survivor : Nat) (w : Watch)
    (different : survivor ≠ removed) (h : (survivor, w) ∈ s.published) :
    (survivor, w) ∈ (remove s removed).published := by
  simp [remove, eraseId, List.mem_filter, h, different]

theorem other_effect_keeps_coverage (s : State) (removed survivor : Nat)
    (e : Entry) (q : Query) (h : Published s) (different : survivor ≠ removed)
    (active : (survivor, e) ∈ s.active) (queried : q ∈ e.queries) :
    watching (remove s removed) e.target q.name = true := by
  apply published_covers_query _ survivor e q (remove_published s removed h) _ queried
  simp [remove, eraseId, List.mem_filter, active, different]

theorem covered_change_admits (s : State) (target name : Nat)
    (h : watching s target name = true) : target ∈ (change s target name).pending := by
  simp [change, h]

theorem queried_change_admits (s : State) (id : Nat) (e : Entry) (q : Query)
    (h : Published s) (active : (id, e) ∈ s.active) (queried : q ∈ e.queries) :
    e.target ∈ (change s e.target q.name).pending :=
  covered_change_admits _ _ _ (published_covers_query s id e q h active queried)

inductive Event where
  | install (id : Nat) (e : Entry)
  | remove (id : Nat)
  | change (target name : Nat)
  deriving DecidableEq, Repr

def step (s : State) : Event → State
  | .install id e => install s id e
  | .remove id => remove s id
  | .change target name => change s target name

def run (events : List Event) : State := events.foldl step empty

theorem step_published (s : State) (event : Event) (h : Published s) : Published (step s event) := by
  cases event with
  | install id e => exact install_published s id e h
  | remove id => exact remove_published s id h
  | change target name => exact change_published s target name h

theorem finite_history_published (events : List Event) : Published (run events) := by
  have general : ∀ (xs : List Event) (s : State), Published s → Published (xs.foldl step s) := by
    intro xs
    induction xs with
    | nil => intro s h; exact h
    | cons event rest ih => intro s h; exact ih _ (step_published s event h)
  exact general events empty empty_published

theorem finite_history_covers (events : List Event) (id : Nat) (e : Entry) (q : Query)
    (active : (id, e) ∈ (run events).active) (queried : q ∈ e.queries) :
    watching (run events) e.target q.name = true :=
  published_covers_query _ id e q (finite_history_published events) active queried

def projection (s : State) (context : Nat → Nat) : AnimationObligations.State :=
  ⟨context, context, fun _ => false,
   fun id => (entryAt s id).map fun e =>
     ⟨e.target, true, none, decide (e.target ∈ s.pending)⟩, false⟩

theorem delivered_normal_builds_current (s : State) (context : Nat → Nat)
    (id : Nat) (e : Entry) (active : entryAt s id = some e)
    (admitted : e.target ∈ s.pending) :
    (AnimationObligations.normalPass (projection s context)).effects id =
      some ⟨e.target, true, some (e.target, context e.target), false⟩ := by
  simp [AnimationObligations.normalPass, projection, active, admitted]

end AttributeWatches
