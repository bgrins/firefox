namespace FreshProvider

structure Face where
  wrapper : Nat
  status : Nat
  promise : Nat

structure Wrapper where
  provider : Nat
  scale : Nat

structure Provider where
  resource : Nat
  scale : Nat

structure World where
  faces : Nat → Face
  wrappers : Nat → Wrapper
  providers : Nat → Provider
  members : Nat → Nat → Bool
  generation : Nat → Nat
  oldCache : Nat → Nat

def selected (s : World) (f : Nat) : Nat :=
  (s.wrappers (s.faces f).wrapper).provider

def observed (s : World) (f : Nat) : Nat :=
  (s.providers (selected s f)).scale

def replace (s : World) (f newWrapper newProvider scale : Nat) : World :=
  { s with
    faces := fun i => if i = f then { s.faces i with wrapper := newWrapper }
      else s.faces i
    wrappers := fun i => if i = newWrapper then ⟨newProvider, scale⟩
      else s.wrappers i
    providers := fun i => if i = newProvider then
      ⟨(s.providers (selected s f)).resource, scale⟩ else s.providers i
    generation := fun set => if s.members f set then s.generation set + 1
      else s.generation set }

theorem target_fresh (s : World) (f w p scale : Nat) :
    observed (replace s f w p scale) f = scale := by
  simp [observed, selected, replace]

theorem resource_preserved (s : World) (f w p scale : Nat) :
    ((replace s f w p scale).providers
      (selected (replace s f w p scale) f)).resource =
      (s.providers (selected s f)).resource := by
  simp [selected, replace]

theorem other_face_preserved (s : World) (f g w p scale : Nat)
    (hg : g ≠ f) (hw : (s.faces g).wrapper ≠ w)
    (hp : selected s g ≠ p) :
    observed (replace s f w p scale) g = observed s g := by
  simp only [selected] at hp
  simp [observed, selected, replace, hg, hw, hp]

theorem old_provider_immutable (s : World) (f w p q scale : Nat) (hq : q ≠ p) :
    (replace s f w p scale).providers q = s.providers q := by
  simp [replace, hq]

theorem status_preserved (s : World) (f g w p scale : Nat) :
    ((replace s f w p scale).faces g).status = (s.faces g).status := by
  simp [replace]; split <;> rfl

theorem promise_preserved (s : World) (f g w p scale : Nat) :
    ((replace s f w p scale).faces g).promise = (s.faces g).promise := by
  simp [replace]; split <;> rfl

theorem cache_preserved (s : World) (f w p scale : Nat) :
    (replace s f w p scale).oldCache = s.oldCache := rfl

theorem member_notified (s : World) (f w p scale set : Nat)
    (h : s.members f set = true) :
    (replace s f w p scale).generation set = s.generation set + 1 := by
  simp [replace, h]

theorem nonmember_unchanged (s : World) (f w p scale set : Nat)
    (h : s.members f set = false) :
    (replace s f w p scale).generation set = s.generation set := by
  simp [replace, h]

def shared : World :=
  ⟨fun _ => ⟨0, 2, 7⟩, fun _ => ⟨0, 100⟩,
    fun _ => ⟨42, 100⟩, fun _ _ => true, fun _ => 0, fun _ => 80⟩

def wrapperOnly : World :=
  { shared with wrappers := fun _ => ⟨0, 50⟩ }

def mutateShared : World :=
  { shared with providers := fun _ => ⟨42, 50⟩ }

theorem wrapper_only_stale : observed wrapperOnly 0 = 100 := rfl
theorem shared_mutation_corrupts_peer : observed mutateShared 1 = 50 := rfl
theorem detached_target : observed (replace shared 0 1 1 50) 0 = 50 := rfl
theorem detached_peer : observed (replace shared 0 1 1 50) 1 = 100 := rfl

#print axioms target_fresh
#print axioms resource_preserved
#print axioms other_face_preserved
#print axioms old_provider_immutable
#print axioms status_preserved
#print axioms promise_preserved
#print axioms cache_preserved
#print axioms member_notified
#print axioms nonmember_unchanged
#print axioms wrapper_only_stale
#print axioms shared_mutation_corrupts_peer
#print axioms detached_target
#print axioms detached_peer

end FreshProvider
