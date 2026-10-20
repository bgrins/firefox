import Std

namespace PrimaryBit

abbrev Frame := Nat
abbrev Content := Nat

structure Layout where
  owner : Frame → Content
  area : Content → Bool

structure State where
  pointer : Content → Option Frame
  bit : Frame → Bool

def empty : State := ⟨fun _ => none, fun _ => false⟩

def Coherent (l : Layout) (s : State) : Prop :=
  ∀ f, s.bit f = decide (s.pointer (l.owner f) = some f)

def NoAreaOwner (l : Layout) : Prop := ∀ f, l.area (l.owner f) = false

def writeBit (s : State) (f : Frame) (b : Bool) : State :=
  { s with bit := fun x => if x = f then b else s.bit x }

def publish (s : State) (c : Content) (p : Option Frame) : State :=
  { s with pointer := fun x => if x = c then p else s.pointer x }

def beginSet (l : Layout) (s : State) (c : Content) (f : Frame) : State :=
  if l.area c = false ∨ l.owner f = c then writeBit s f true else s

def setPrimary (l : Layout) (s : State) (c : Content) (p : Option Frame) : State :=
  match p with
  | some f => publish (beginSet l s c f) c p
  | none =>
    let cleared := match s.pointer c with
      | none => s
      | some f =>
        if l.area c = false ∨ l.owner f = c then writeBit s f false else s
    publish cleared c none

theorem empty_coherent (l : Layout) : Coherent l empty := by
  intro f; simp [empty]

theorem own_set_preserves (l : Layout) (s : State) (c : Content) (f : Frame)
    (coherent : Coherent l s) (owner : l.owner f = c)
    (replace : s.pointer c = none ∨ s.pointer c = some f) :
    Coherent l (setPrimary l s c (some f)) := by
  intro x
  by_cases same : x = f
  · subst x; simp [setPrimary, beginSet, writeBit, publish, owner]
  · by_cases own : l.owner x = c
    · have bx : s.bit x = false := by
        rw [coherent x, own]
        rcases replace with h | h <;> simp [h, Ne.symm same]
      simp [setPrimary, beginSet, writeBit, publish, owner, same, own, bx, Ne.symm same]
    · simpa [setPrimary, beginSet, writeBit, publish, owner, same, own] using coherent x

theorem area_alias_preserves (l : Layout) (s : State) (c : Content) (f : Frame)
    (coherent : Coherent l s) (noArea : NoAreaOwner l) (area : l.area c = true) :
    Coherent l (setPrimary l s c (some f)) := by
  have notOwner : ∀ x, l.owner x ≠ c := by
    intro x h; have := noArea x; rw [h, area] at this; contradiction
  intro x
  simpa [setPrimary, beginSet, publish, area, notOwner] using coherent x

theorem clear_preserves (l : Layout) (s : State) (c : Content)
    (coherent : Coherent l s) (noArea : NoAreaOwner l)
    (ownPointer : ∀ f, s.pointer c = some f → l.area c = false → l.owner f = c) :
    Coherent l (setPrimary l s c none) := by
  intro x
  by_cases area : l.area c = true
  · have notOwner : ∀ f, l.owner f ≠ c := by
      intro f h; have := noArea f; rw [h, area] at this; contradiction
    cases h : s.pointer c <;>
      simpa [setPrimary, publish, h, area, notOwner] using coherent x
  · have ordinary : l.area c = false := by cases h : l.area c <;> simp_all
    cases h : s.pointer c with
    | none =>
      by_cases own : l.owner x = c
      · have bx : s.bit x = false := by simp [coherent x, own, h]
        simp [setPrimary, publish, h, own, bx]
      · simpa [setPrimary, publish, h, own] using coherent x
    | some f =>
      have owner := ownPointer f h ordinary
      by_cases same : x = f
      · subst x; simp [setPrimary, publish, h, ordinary, writeBit, owner]
      · by_cases own : l.owner x = c
        · have bx : s.bit x = false := by rw [coherent x, own, h]; simp [Ne.symm same]
          simp [setPrimary, publish, h, ordinary, writeBit, own, same, bx]
        · simpa [setPrimary, publish, h, ordinary, writeBit, own, same] using coherent x

def Routed (l : Layout) (s : State) : Prop :=
  ∀ c f, s.pointer c = some f → l.area c = false → l.owner f = c

theorem empty_routed (l : Layout) : Routed l empty := by
  intro c f h; simp [empty] at h

theorem publish_routed (l : Layout) (s : State) (c : Content) (p : Option Frame)
    (routed : Routed l s)
    (own : ∀ f, p = some f → l.area c = false → l.owner f = c) :
    Routed l (publish s c p) := by
  intro d f h ordinary
  by_cases same : d = c
  · subst d; exact own f (by simpa [publish] using h) ordinary
  · exact routed d f (by simpa [publish, same] using h) ordinary

theorem set_routed (l : Layout) (s : State) (c : Content) (p : Option Frame)
    (routed : Routed l s)
    (own : ∀ f, p = some f → l.area c = false → l.owner f = c) :
    Routed l (setPrimary l s c p) := by
  have same : (setPrimary l s c p).pointer = (publish s c p).pointer := by
    cases p with
    | none => cases h : s.pointer c <;> simp [setPrimary, publish, h, writeBit]; split <;> rfl
    | some f => simp only [setPrimary, beginSet]; split <;> rfl
  intro d f h ordinary
  rw [same] at h
  exact publish_routed l s c p routed own d f h ordinary

inductive Step (l : Layout) : State → State → Prop where
  | own (s c f) (owner : l.owner f = c)
      (replace : s.pointer c = none ∨ s.pointer c = some f) :
      Step l s (setPrimary l s c (some f))
  | alias (s c f) (area : l.area c = true) :
      Step l s (setPrimary l s c (some f))
  | clear (s c) : Step l s (setPrimary l s c none)

theorem step_preserves (l : Layout) (a b : State) (noArea : NoAreaOwner l)
    (coherent : Coherent l a) (routed : Routed l a) (step : Step l a b) :
    Coherent l b ∧ Routed l b := by
  cases step with
  | own c f owner replace =>
    exact ⟨own_set_preserves l a c f coherent owner replace,
      set_routed l a c (some f) routed (by intro x h _; cases h; exact owner)⟩
  | alias c f area =>
    exact ⟨area_alias_preserves l a c f coherent noArea area,
      set_routed l a c (some f) routed (by intro x _ h; simp [area] at h)⟩
  | clear c =>
    exact ⟨clear_preserves l a c coherent noArea (routed c),
      set_routed l a c none routed (by intro f h; cases h)⟩

inductive History (l : Layout) : State → State → Prop where
  | refl (s) : History l s s
  | next {s t u} : History l s t → Step l t u → History l s u

theorem history_preserves (l : Layout) (a b : State) (noArea : NoAreaOwner l)
    (coherent : Coherent l a) (routed : Routed l a) (history : History l a b) :
    Coherent l b ∧ Routed l b := by
  induction history with
  | refl => exact ⟨coherent, routed⟩
  | next _ step ih => exact step_preserves l _ _ noArea ih.1 ih.2 step

def nativeDestroyRead (l : Layout) (s : State) (f : Frame) : State :=
  if s.bit f then setPrimary l s (l.owner f) none else s

def pointerDestroyRead (l : Layout) (s : State) (f : Frame) : State :=
  if s.pointer (l.owner f) = some f then setPrimary l s (l.owner f) none else s

theorem destroy_read_agrees (l : Layout) (s : State) (f : Frame)
    (coherent : Coherent l s) : nativeDestroyRead l s f = pointerDestroyRead l s f := by
  simp [nativeDestroyRead, pointerDestroyRead, coherent f]

theorem history_destroy_read_agrees (l : Layout) (a b : State) (f : Frame)
    (noArea : NoAreaOwner l) (coherent : Coherent l a) (routed : Routed l a)
    (callbacks : History l a b) :
    nativeDestroyRead l b f = pointerDestroyRead l b f := by
  exact destroy_read_agrees l b f (history_preserves l a b noArea coherent routed callbacks).1

end PrimaryBit
