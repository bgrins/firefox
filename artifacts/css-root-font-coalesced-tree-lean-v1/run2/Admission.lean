import Watches

namespace FontUnitAdmission

structure State where
  registry : AttributeWatches.State
  fast : List Nat
  deriving DecidableEq, Repr

def empty : State := ⟨AttributeWatches.empty, []⟩
def register (ownerOf : Nat → Nat) (s : State) (id : Nat) (e : AttributeWatches.Entry) : State :=
  ⟨AttributeWatches.install s.registry id e, ownerOf e.target :: s.fast⟩
def unregister (s : State) (id : Nat) : State :=
  ⟨AttributeWatches.remove s.registry id, s.fast⟩
def destroyOwner (ownerOf : Nat → Nat) (s : State) (owner : Nat) : State :=
  ⟨{ s.registry with
      active := s.registry.active.filter fun pair => ownerOf pair.2.target != owner
      published := s.registry.published.filter fun pair => ownerOf pair.2.target != owner },
    s.fast.filter fun t => t != owner⟩

def Consistent (ownerOf : Nat → Nat) (s : State) : Prop :=
  ∀ id e, (id, e) ∈ s.registry.active → ownerOf e.target ∈ s.fast

def hasAnimations (ownerOf : Nat → Nat) (s : State) (target : Nat) : Bool :=
  s.fast.contains (ownerOf target) && s.registry.active.any (fun pair => pair.2.target == target)

def admits (ownerOf : Nat → Nat) (normal hint retainedFlag : Bool) (s : State) (target : Nat) : Bool :=
  hint && (retainedFlag || (normal && hasAnimations ownerOf s target))

theorem empty_consistent (ownerOf : Nat → Nat) : Consistent ownerOf empty := by
  intro id e member
  simp [empty, AttributeWatches.empty] at member

theorem register_consistent (ownerOf : Nat → Nat) (s : State) (id : Nat)
    (e : AttributeWatches.Entry) (h : Consistent ownerOf s) :
    Consistent ownerOf (register ownerOf s id e) := by
  intro other entry member
  simp only [register, AttributeWatches.install, List.mem_cons] at member
  rcases member with same | old
  · cases same
    simp [register]
  · have prior := (List.mem_filter.mp old).1
    exact List.mem_cons_of_mem _ (h other entry prior)

theorem unregister_consistent (ownerOf : Nat → Nat) (s : State) (id : Nat)
    (h : Consistent ownerOf s) : Consistent ownerOf (unregister s id) := by
  intro other entry member
  exact h other entry (List.mem_filter.mp member).1

theorem destroy_consistent (ownerOf : Nat → Nat) (s : State) (owner : Nat)
    (h : Consistent ownerOf s) : Consistent ownerOf (destroyOwner ownerOf s owner) := by
  intro id entry member
  obtain ⟨prior, survives⟩ := List.mem_filter.mp member
  exact List.mem_filter.mpr ⟨h id entry prior, survives⟩

inductive Event where
  | register (id : Nat) (e : AttributeWatches.Entry)
  | unregister (id : Nat)
  | destroy (owner : Nat)

def step (ownerOf : Nat → Nat) (s : State) : Event → State
  | .register id e => register ownerOf s id e
  | .unregister id => unregister s id
  | .destroy owner => destroyOwner ownerOf s owner

def run (ownerOf : Nat → Nat) (events : List Event) : State := events.foldl (step ownerOf) empty

theorem step_consistent (ownerOf : Nat → Nat) (s : State) (event : Event)
    (h : Consistent ownerOf s) : Consistent ownerOf (step ownerOf s event) := by
  cases event with
  | register id e => exact register_consistent ownerOf s id e h
  | unregister id => exact unregister_consistent ownerOf s id h
  | destroy owner => exact destroy_consistent ownerOf s owner h

theorem finite_history_consistent (ownerOf : Nat → Nat) (events : List Event) :
    Consistent ownerOf (run ownerOf events) := by
  have general : ∀ xs : List Event, ∀ s, Consistent ownerOf s →
      Consistent ownerOf (xs.foldl (step ownerOf) s) := by
    intro xs
    induction xs with
    | nil => intro s h; exact h
    | cons event rest ih => intro s h; exact ih _ (step_consistent ownerOf s event h)
  exact general events empty (empty_consistent ownerOf)

theorem member_has_animations (ownerOf : Nat → Nat) (s : State) (id : Nat)
    (e : AttributeWatches.Entry) (h : Consistent ownerOf s)
    (member : (id, e) ∈ s.registry.active) : hasAnimations ownerOf s e.target = true := by
  simp only [hasAnimations, Bool.and_eq_true]
  constructor
  · exact List.contains_iff_mem.mpr (h id e member)
  · apply List.any_eq_true.mpr
    exact ⟨(id, e), member, by simp⟩

theorem registered_normal_hint_admitted (ownerOf : Nat → Nat) (events : List Event)
    (id : Nat) (e : AttributeWatches.Entry) (retainedFlag : Bool)
    (member : (id, e) ∈ (run ownerOf events).registry.active) :
    admits ownerOf true true retainedFlag (run ownerOf events) e.target = true := by
  simp [admits, member_has_animations ownerOf _ id e (finite_history_consistent ownerOf events) member]

theorem old_admission_preserved (ownerOf : Nat → Nat) (normal hint retainedFlag : Bool)
    (s : State) (target : Nat) (old : (hint && retainedFlag) = true) :
    admits ownerOf normal hint retainedFlag s target = true := by
  have parts : hint = true ∧ retainedFlag = true := by
    simpa only [Bool.and_eq_true] using old
  obtain ⟨a,b⟩ := parts
  simp [admits,a,b]

theorem animation_only_unchanged (ownerOf : Nat → Nat) (hint retainedFlag : Bool)
    (s : State) (target : Nat) :
    admits ownerOf false hint retainedFlag s target = (hint && retainedFlag) := by simp [admits]

theorem absent_hint_no_admission (ownerOf : Nat → Nat) (normal retainedFlag : Bool)
    (s : State) (target : Nat) : admits ownerOf normal false retainedFlag s target = false := rfl

def idOwner : Nat → Nat := fun n => n
def oneOwner : Nat → Nat := fun _ => 1
def literal : AttributeWatches.Entry := ⟨7, 46, []⟩
def shared : State := run idOwner [.register 1 literal, .register 2 literal, .unregister 1]
def retargeted : State := run idOwner [.register 1 literal, .register 1 {literal with target := 9}]
def clearFastOnOneRemoval : State := { shared with fast := [] }

theorem surviving_literal_admitted : admits idOwner true true false shared 7 = true := by decide +kernel

theorem sole_cancel_not_admitted :
    admits idOwner true true false (run idOwner [.register 1 literal, .unregister 1]) 7 = false := by decide +kernel

theorem retarget_uses_new_owner :
    admits idOwner true true false retargeted 7 = false ∧
    admits idOwner true true false retargeted 9 = true := by decide +kernel

theorem destruction_preserves_other_target :
    let s := run idOwner [.register 1 literal, .register 2 {literal with target := 9}, .destroy 7]
    admits idOwner true true false s 7 = false ∧ admits idOwner true true false s 9 = true := by decide +kernel

theorem premature_fast_clear_loses_survivor :
    ¬ Consistent idOwner clearFastOnOneRemoval ∧ admits idOwner true true false clearFastOnOneRemoval 7 = false := by
  constructor
  · intro h
    have absent := h 2 literal (by decide +kernel)
    exact List.not_mem_nil absent
  · decide +kernel

theorem shared_owner_keeps_other_pseudo :
    let s := run oneOwner [.register 1 literal, .register 2 {literal with target := 9}, .unregister 1]
    admits oneOwner true true false s 7 = false ∧ admits oneOwner true true false s 9 = true := by decide +kernel

theorem owner_destruction_removes_all_pseudos :
    let s := run oneOwner [.register 1 literal, .register 2 {literal with target := 9}, .destroy 1]
    admits oneOwner true true false s 7 = false ∧ admits oneOwner true true false s 9 = false := by decide +kernel

end FontUnitAdmission
